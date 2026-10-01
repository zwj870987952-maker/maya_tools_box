"""Complete source pipeline orchestration, read-only plans and explicit file transactions."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import numpy as np
from maya import cmds
from maya_toolkit.framework.models import ToolResult
from .tool import validate_map

ACTIVE = None
WRITTEN = []
WARNINGS = ['真人原界面、生产骨架/skin和几何往返品质待验；隔离mayapy不是最终验收。', '没有独立许可声明，仅本地候选，不发布。', 'OBJ/JSON文件不可Maya Undo；失败后可能已有部分输出。']


def require_scope():
    if ACTIVE is None:
        raise ValueError('Use PoseMatcherTool.run; native scene/file writes need an API scope')


def backend():
    from . import native
    from . import ui_bridge
    ui_bridge.bind(native)
    return native


def whole(n, kind=None):
    found = cmds.ls(n, long=True) or []
    if len(found) != 1 or '.' in found[0]:
        raise ValueError('Require one unambiguous whole node: ' + str(n))
    n = found[0]
    if kind and cmds.nodeType(n) != kind:
        raise ValueError('Expected ' + kind + ': ' + n)
    if len(cmds.ls(n, long=True, allPaths=True) or []) > 1:
        raise ValueError('Instanced node unsupported')
    return n


def signature(p):
    if not p.exists():
        return None
    if not p.is_file() or p.is_symlink():
        raise ValueError('Refuse non-file or symlink output: ' + str(p))
    return hashlib.sha256(p.read_bytes()).hexdigest()


def input_json(path):
    p = Path(path).resolve() if path else None
    if p is None or not p.is_file() or p.stat().st_size > 64000000:
        raise ValueError('Missing/oversized explicit JSON input')
    return json.loads(p.read_text(encoding='utf-8-sig'))


def map_data(data):
    if isinstance(data, list):
        rows = data
        data = {}
        for row in rows:
            if not isinstance(row, dict) or set(row) - {'mh_joint', 'daz_joint'} or row.get('mh_joint') in data:
                raise ValueError('Malformed/duplicate legacy map row')
            data[row.get('mh_joint')] = row.get('daz_joint')
    return validate_map(data)


def check_arrays(v, uv, vt, vn):
    v = np.asarray(v, dtype=np.float64)
    uv = np.asarray(uv, dtype=np.float64)
    vn = np.asarray(vn, dtype=np.float64)
    raw = np.asarray(vt)
    if raw.ndim != 2 or raw.shape[1] != 4 or raw.shape[0] > 600000 or not np.isfinite(raw.astype(float)).all() or not np.equal(raw, np.floor(raw.astype(float))).all():
        raise ValueError('Invalid bounded integer face-corner table')
    vt = raw.astype(np.int32)
    for a, cols in ((v, 3), (uv, 2), (vn, 3)):
        if a.ndim != 2 or a.shape[1] != cols or not 1 <= len(a) <= 600000 or not np.isfinite(a).all():
            raise ValueError('Invalid finite vertex/UV/normal arrays')
    if len(v) > 200000 or (vt < 0).any() or any(int(vt[:, i].max()) >= bound for i, bound in ((1, len(v)), (2, len(uv)), (3, len(vn)))):
        raise ValueError('Array index/count exceeded')
    unique, counts = np.unique(vt[:, 0], return_counts=True)
    if len(vt) < 3 or not np.array_equal(unique, np.arange(len(unique))) or (np.diff(vt[:, 0]) < 0).any() or (counts < 3).any():
        raise ValueError('Faces must be contiguous ordered groups of at least 3 corners')
    return v.copy(), uv.copy(), vt.copy(), vn.copy()


def mesh(n):
    n = whole(n, 'transform')
    shapes = cmds.listRelatives(n, shapes=True, fullPath=True, noIntermediate=True) or []
    if len(shapes) != 1 or cmds.nodeType(shapes[0]) != 'mesh':
        raise ValueError('Choose a transform with one nonintermediate polygon mesh')
    arrays = backend().get_mesh_arrays_fast(n)
    v, uv, vn, vt = arrays
    v, uv, vt, vn = check_arrays(v, uv, vt, vn)
    return n, v, uv, vn, vt


def index(root):
    ns = {}
    for n in (cmds.listRelatives(root, allDescendents=True, type='joint', fullPath=True) or []) + [root]:
        leaf = n.rsplit('|', 1)[-1].split(':')[-1]
        ns.setdefault(leaf, []).append(n)
    return ns


def plan_align(o):
    native = backend()
    source = whole(o['source_root'], 'joint')
    target = whole(o['target_root'], 'joint')
    if source == target or source.startswith(target + '|') or target.startswith(source + '|'):
        raise ValueError('Require disjoint skeleton roots')
    mapping = map_data(o['joint_map'] if o['joint_map'] is not None else input_json(o['map_path']))
    si, ti = index(source), index(target)
    writes = []
    for s, t in mapping.items():
        if len(si.get(s, [])) != 1 or len(ti.get(t, [])) != 1:
            raise ValueError('Missing or duplicate mapped leaf: ' + s + ' / ' + t)
        src, dst = si[s][0], ti[t][0]
        parents = cmds.listRelatives(dst, parent=True, fullPath=True) or []
        if not parents or not (parents[0] == target or parents[0].startswith(target + '|')):
            raise ValueError('Mapped child must have a parent inside target root')
        parent = parents[0]
        if 'twist' in parent.rsplit('|', 1)[-1].lower():
            p = cmds.listRelatives(parent, parent=True, fullPath=True) or []
            if not p or not (p[0] == target or p[0].startswith(target + '|')):
                raise ValueError('Twist effective parent escapes target skeleton')
            parent = p[0]
        whole(parent, 'joint')
        if cmds.referenceQuery(parent, isNodeReferenced=True) or any(cmds.lockNode(parent, q=True, lock=True) or []):
            raise ValueError('Locked/referenced write joint refused')
        if np.linalg.norm(native.get_joint_direction(src)) <= 1e-12 or np.linalg.norm(native.get_joint_position(dst) - native.get_joint_position(parent)) <= 1e-12:
            raise ValueError('Zero-length source/destination bone')
        for attr in ('rx', 'ry', 'rz'):
            if cmds.getAttr(parent + '.' + attr, lock=True) or cmds.listConnections(parent + '.' + attr, s=True, d=False) or cmds.listConnections(parent + '.rotate', s=True, d=False):
                raise ValueError('Keyed/driven/locked write rotation refused')
        # Original rotation extraction assumes ordinary rotation, not sheared/scaled matrices.
        p = parent
        while p:
            if not np.allclose(cmds.getAttr(p + '.scale')[0], [1, 1, 1]) or not np.allclose(cmds.getAttr(p + '.shear')[0], [0, 0, 0]):
                raise ValueError('Scaled/sheared target hierarchy unsupported')
            ancestors = cmds.listRelatives(p, parent=True, fullPath=True) or []
            p = ancestors[0] if ancestors else None
        writes.append(parent)
    return dict(source_root=source, target_root=target, joint_map=mapping, written_parents=list(dict.fromkeys(writes)))


def destinations(o):
    if not o['output_path']:
        raise ValueError('Explicit output_path required')
    path = Path(o['output_path']).resolve()
    if not path.parent.is_dir() or path.is_dir():
        raise ValueError('Output parent must already exist')
    if o['action'] == 'save_map':
        paths = [path]
    elif o['action'] == 'merge':
        if path.suffix.lower() != '.obj':
            raise ValueError('Merge output_path must end .obj')
        paths = [path, path.with_name(path.stem + '_MergeInfo.json')]
    else:
        base = path.with_suffix('')
        paths = [base.with_name(base.name + '_Part1.obj'), base.with_name(base.name + '_Part2.obj')]
    observed = {str(p): signature(p) for p in paths}
    if any(v is not None for v in observed.values()) and not o['overwrite']:
        raise ValueError('Output group exists; explicit overwrite required')
    inputs = [Path(o['map_path']).resolve()] if o['map_path'] else []
    if any(p in inputs for p in paths):
        raise ValueError('Output would overwrite the input JSON')
    return observed


def split_data(info, merged):
    _, v, uv, vn, vt = merged
    if not isinstance(info, dict):
        raise ValueError('Malformed MergeInfo')
    n1, n2 = info.get('num_vertices_mesh1'), info.get('num_vertices_mesh2')
    if type(n1) is not int or type(n2) is not int or not 1 <= n1 <= len(v) or not 1 <= n2 <= 200000:
        raise ValueError('Invalid original vertex counts')
    mapping = np.asarray(info['map_v'])
    if mapping.shape != (n2,) or not np.equal(mapping, np.floor(mapping)).all() or (mapping < 0).any() or (mapping >= len(v)).any():
        raise ValueError('MergeInfo vertex mapping invalid')
    f1, f2 = np.asarray(info['faces_mesh1']), np.asarray(info['faces_mesh2'])
    if info.get('candidate_format') != 2:
        raise ValueError('Legacy MergeInfo lacks topology/normal provenance; regenerate merge with this candidate')
    expected = np.asarray(info['merged_faces'])
    if expected.shape != vt.shape or not np.array_equal(expected[:, :2], vt[:, :2]) or len(f1) + len(f2) != len(vt):
        raise ValueError('Merged topology changed; only position/normal edits are supported')
    output = []
    for vertices, faces, tex, offset in ((v[:n1], f1, info['uv_mesh1'], 0), (v[mapping.astype(int)], f2, info['uv_mesh2'], len(f1))):
        normals = vn[vt[offset:offset + len(faces), 3]]
        faces = faces.copy()
        faces[:, 3] = np.arange(len(faces))
        vertices, tex, faces, normals = check_arrays(vertices, tex, faces, normals)
        output.append((vertices, tex, faces, normals))
    return output


def prepare(o):
    action = o['action']
    p = dict(action=action, warnings=WARNINGS[:])
    if action in ('open_ui', 'close_ui', 'inspect'):
        if action == 'open_ui' and cmds.about(batch=True):
            raise ValueError('Interactive Maya UI required')
        p['selection'] = cmds.ls(sl=True, long=True) or []
        return p
    if action in ('save_map', 'load_map'):
        p['joint_map'] = map_data(o['joint_map'] if o['joint_map'] is not None else input_json(o['map_path']))
    elif action == 'align':
        p.update(plan_align(o))
    elif action == 'detect':
        s, t = index(whole(o['source_root'], 'joint')), index(whole(o['target_root'], 'joint'))
        p['joint_map'] = {k: k for k in sorted(set(s) & set(t)) if len(s[k]) == len(t[k]) == 1}
    elif action in ('merge', 'split', 'overlaps'):
        chosen = o['meshes'] if o['meshes'] is not None else cmds.ls(sl=True, long=True) or []
        if len(chosen) != (1 if action == 'split' else 2):
            raise ValueError('Choose exactly the required number of mesh transforms')
        arrays = [mesh(n) for n in chosen]
        if len({n[0] for n in arrays}) != len(arrays):
            raise ValueError('Duplicate mesh identity')
        if sum(len(a[1]) for a in arrays) > 200000 or sum(len(a[4]) for a in arrays) > 600000:
            raise ValueError('Combined geometry budget exceeded')
        p['meshes'] = [a[0] for a in arrays]
        if action == 'split':
            split_data(input_json(o['map_path']), arrays[0])
    if action in ('merge', 'split', 'save_map'):
        p['output_signatures'] = destinations(o)
    if action in ('align', 'merge', 'split') and not cmds.undoInfo(q=True, state=True):
        raise ValueError('Enable Undo before scene writes')
    return p


@contextmanager
def scope(plan):
    global ACTIVE
    if ACTIVE is not None:
        raise ValueError('Reentrant operation refused')
    state = dict(selection=cmds.ls(sl=True, long=True) or [], time=cmds.currentTime(q=True), auto=cmds.autoKeyframe(q=True, state=True), refresh=cmds.refresh(q=True, suspend=True), ns=':' + cmds.namespaceInfo(currentNamespace=True).lstrip(':'), relative=cmds.namespace(q=True, relativeNames=True))
    ACTIVE = dict(plan)
    try:
        cmds.namespace(relativeNames=False)
        cmds.namespace(set=':')
        cmds.autoKeyframe(state=False)
        yield
    finally:
        ACTIVE = None
        errors = []
        restore = [lambda: cmds.namespace(relativeNames=False), lambda: cmds.namespace(set=state['ns']), lambda: cmds.namespace(relativeNames=state['relative']), lambda: cmds.autoKeyframe(state=state['auto']), lambda: cmds.currentTime(state['time']), lambda: cmds.refresh(suspend=state['refresh']), lambda: cmds.select([n for n in state['selection'] if cmds.objExists(n)], r=True) if state['selection'] else cmds.select(clear=True)]
        for fn in restore:
            try:
                fn()
            except Exception as e:
                errors.append(str(e))
        if errors:
            raise RuntimeError('Context restore failed: ' + '; '.join(errors))


def publish(staged, plan, overwrite):
    for source, target in staged:
        target = Path(target)
        expected = plan['output_signatures'][str(target)]
        if signature(target) != expected:
            raise ValueError('Output changed after preflight: ' + str(target))
        if expected is None:
            os.link(source, target)
        elif overwrite:
            os.replace(source, target)
        else:
            raise ValueError('Refuse overwriting existing output')
        WRITTEN.append(str(target))


def execute(o, p):
    global WRITTEN
    WRITTEN = []
    native = backend()
    action = o['action']
    if action in ('inspect', 'load_map', 'detect'):
        return ToolResult.ok(data=p, warnings=p['warnings'])
    if action == 'open_ui':
        native.create_alignment_ui()
        return ToolResult.ok('原生候选窗口已打开', data=p, warnings=p['warnings'])
    if action == 'close_ui':
        window = 'mtkPoseCandidate_skeletonAlignmentUI'
        if cmds.window(window, exists=True):
            cmds.deleteUI(window, window=True)
        return ToolResult.ok(data=p, warnings=p['warnings'])
    if action == 'overlaps':
        arrays = [mesh(n) for n in p['meshes']]
        _, a, b = native.find_overlaps(arrays[0][1], arrays[1][1], o['decimals'])
        p['indices'] = [a.tolist(), b.tolist()]
        return ToolResult.ok(data=p, warnings=p['warnings'])
    from .progress import cleanup
    with scope(p), cleanup():
        if action == 'align':
            result = native.align_skeleton(p['joint_map'], p['source_root'], p['target_root'])
            p.update(result)
            if result['errors']:
                return ToolResult.fail('部分骨架对齐失败；一次Undo恢复', errors=result['errors'], data=p)
        else:
            outputs = list(p['output_signatures'])
            with tempfile.TemporaryDirectory(prefix='mtk_pose_', dir=str(Path(outputs[0]).parent)) as temp:
                stage = Path(temp)
                if action == 'save_map':
                    local = stage / 'map.json'
                    local.write_text(json.dumps(p['joint_map'], ensure_ascii=False, indent=4), encoding='utf-8')
                    publish([(local, outputs[0])], p, o['overwrite'])
                elif action == 'merge':
                    a, b = [mesh(n) for n in p['meshes']]
                    _, ia, ib = native.find_overlaps(a[1], b[1], o['decimals'])
                    base = stage / 'merged'
                    f, v, uv, vn = native.MergeMeshes(str(base), a[4], b[4], a[1], b[1], a[2], b[2], a[3], b[3], ia, ib)
                    v, uv, f, vn = check_arrays(v, uv, f, vn)
                    infofile = stage / 'merged_MergeInfo.json'
                    info = input_json(str(infofile))
                    info.update(candidate_format=2, merged_faces=f.tolist())
                    infofile.write_text(json.dumps(info, ensure_ascii=False, indent=4), encoding='utf-8')
                    obj = stage / 'merged.obj'
                    native.writeWithColor(f, v, uv, vn, [], str(obj))
                    p['created_meshes'] = [native.build_mesh_from_numpy(v, uv, f, vn, safe_name(Path(outputs[0]).stem))]
                    native.assign_lambert_to_mesh(p['created_meshes'][0])
                    p['overlap_indices'] = [ia.tolist(), ib.tolist()]
                    publish([(obj, outputs[0]), (infofile, outputs[1])], p, o['overwrite'])
                else:
                    arrays = split_data(input_json(o['map_path']), mesh(p['meshes'][0]))
                    staged = []
                    p['created_meshes'] = []
                    for i, (v, uv, f, vn) in enumerate(arrays):
                        obj = stage / ('part' + str(i) + '.obj')
                        native.writeWithColor(f, v, uv, vn, [], str(obj))
                        node = native.build_mesh_from_numpy(v, uv, f, vn, safe_name(Path(outputs[i]).stem))
                        native.assign_lambert_to_mesh(node)
                        p['created_meshes'].append(node)
                        staged.append((obj, outputs[i]))
                    publish(staged, p, o['overwrite'])
            p['written_files'] = WRITTEN[:]
    return ToolResult.ok('Pose Matcher 操作完成', data=p, warnings=p['warnings'])


def safe_name(name):
    cleaned = re.sub('[^A-Za-z0-9_]', '_', name)
    return 'mtkPose_' + cleaned[:100]
