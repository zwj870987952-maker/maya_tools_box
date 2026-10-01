"""Complete suite business functions, explicit bounded files and scene scope."""
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from maya import cmds
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

PKG = Path(__file__).resolve().parent


def catalog():
    return json.loads((PKG / 'catalog.json').read_text(encoding='utf8'))


def resources():
    for row in catalog()['files']:
        if hashlib.sha256((PKG / 'vendor' / row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Original resource missing/changed')


def nodes(values, joints=False, writable=False):
    result = []
    for value in values:
        found = cmds.ls(value, long=True) or []
        if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform') or (joints and cmds.nodeType(found[0]) != 'joint'):
            raise ValueError('Unique whole ' + ('joint' if joints else 'transform') + ' required: ' + value)
        n = found[0]
        sl = om.MSelectionList()
        sl.add(n)
        if len(om.MDagPath.getAllPathsTo(sl.getDependNode(0))) != 1:
            raise ValueError('True DAG instances unsupported')
        if writable and (cmds.referenceQuery(n, isNodeReferenced=True) or any(cmds.lockNode(n, query=True, lock=True))):
            raise ValueError('Referenced/locked write scope')
        if n in result:
            raise ValueError('Duplicate object aliases')
        result.append(n)
    return result


def mesh(n):
    shapes = cmds.listRelatives(n, shapes=True, noIntermediate=True, fullPath=True) or []
    if len(shapes) != 1 or cmds.nodeType(shapes[0]) != 'mesh':
        raise ValueError('One polygon mesh shape required: ' + n)
    sl = om.MSelectionList()
    sl.add(shapes[0])
    fn = om.MFnMesh(sl.getDagPath(0))
    counts, indices = fn.getVertices()
    topology = hashlib.sha256(json.dumps([fn.numVertices, list(counts), list(indices)]).encode()).hexdigest()
    skins = list(dict.fromkeys(cmds.ls(cmds.listHistory(shapes[0]) or [], type='skinCluster') or []))
    if len(skins) > 1:
        raise ValueError('Multiple skinClusters unsupported')
    cluster = skins[0] if skins else None
    return {'object': n, 'shape': shapes[0], 'vertex_count': fn.numVertices, 'topology_sha256': topology, 'skin': cluster, 'influences': cmds.skinCluster(cluster, query=True, influence=True) or [] if cluster else [], 'weighted': cmds.skinCluster(cluster, query=True, weightedInfluence=True) or [] if cluster else []}


def checked_dir(value):
    if not isinstance(value, str):
        raise ValueError('Explicit absolute existing directory required')
    path = Path(value)
    if not path.is_absolute() or not path.is_dir() or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Existing absolute nonsymlink directory required')
    return path.resolve()


def basename(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]{0,127}', value) or '..' in value or value.upper().split('.')[0] in ('CON', 'NUL', 'PRN', 'AUX', *['COM'+str(i) for i in range(1, 10)], *['LPT'+str(i) for i in range(1, 10)]):
        raise ValueError('Safe nonreserved basename required')
    return value


def influence_file(path, convention):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 5_000_000:
        raise ValueError('Missing/oversized/linked influence TXT')
    names = []
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():
            continue
        if convention == 'skininfo':
            match = re.fullmatch(r'\s*select\s+-add\s+"?([A-Za-z_][A-Za-z0-9_:|]*)"?;\s*', line)
            if not match:
                raise ValueError('Influence TXT contains unsupported command; never evaluated')
            name = match.group(1)
        else:
            name = line.strip()
            if not re.fullmatch(r'[A-Za-z_|][A-Za-z0-9_:|]*', name):
                raise ValueError('Timal TXT must contain joint names only')
        names.append(name)
    if not names or len(names) > 1000 or len(set(names)) != len(names):
        raise ValueError('Nonempty unique influence names required')
    return nodes(names, joints=True)


def weight_writable(row):
    if cmds.referenceQuery(row['shape'], isNodeReferenced=True) or any(cmds.lockNode(row['shape'], query=True, lock=True)):
        raise ValueError('Referenced/locked mesh shape')
    if row['skin'] and (cmds.referenceQuery(row['skin'], isNodeReferenced=True) or any(cmds.lockNode(row['skin'], query=True, lock=True))):
        raise ValueError('Referenced/locked skinCluster')
    if row['skin'] and cmds.getAttr(row['skin'] + '.weightList', lock=True):
        raise ValueError('Locked skin weight array')
    if row['vertex_count'] * max(1, len(row['influences'])) > 2_000_000:
        raise ValueError('Skin transaction exceeds bounded weight budget')
    for n in row['influences']:
        if cmds.getAttr(n + '.liw'):
            raise ValueError('Influence weights locked: ' + n)


def plan(p):
    resources()
    action = p['action']
    if action == 'inspect':
        return {'catalog': catalog(), 'scene_write': False, 'file_write': False, 'gui_acceptance': 'not_run'}
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before suite operations')
    if action == 'connect':
        source = nodes(p.get('sources', []))
        destination = nodes(p.get('destinations', []), writable=True)
        if not source or not destination:
            raise ValueError('Explicit source and destination lists required')
        def key(n, prefix):
            return n.rsplit('|', 1)[-1].rsplit(':', 1)[-1].replace(prefix, '', 1) if prefix else n.rsplit('|', 1)[-1].rsplit(':', 1)[-1]
        srcmap = {}
        dstmap = {}
        for values, mapping, prefix in ((source, srcmap, p['source_prefix']), (destination, dstmap, p['destination_prefix'])):
            for n in values:
                k = key(n, prefix)
                if k in mapping:
                    raise ValueError('Ambiguous stripped pair name: ' + k)
                mapping[k] = n
        pairs = [(srcmap[k], dstmap[k]) for k in srcmap if k in dstmap]
        if not pairs:
            raise ValueError('No matched pairs')
        channels = p['channels'] if p['mode'] == 'direct' else [c for c in p['channels'] if c[0] in ('tr' if p['mode'] in ('parent', 'point_orient') else 't' if p['mode'] == 'point' else 'r')]
        if not channels:
            raise ValueError('No relevant constraint channels')
        connections = []
        for src, dst in pairs:
            if src == dst or src.startswith(dst + '|') or dst in (cmds.listHistory(src, allConnections=True) or []):
                raise ValueError('Pair creates self/hierarchy/dependency feedback')
            for c in channels:
                plug = dst + '.' + c
                if cmds.getAttr(plug, lock=True):
                    raise ValueError('Locked destination channel')
                incoming = cmds.listConnections(plug, source=True, destination=False, plugs=True) or []
                if incoming and (p['mode'] != 'direct' or not p['allow_replace_connections']):
                    raise ValueError('Existing driven channel needs explicit direct replacement; constraint replacement refused')
                connections.append({'source': src + '.' + c, 'destination': plug, 'replaces': incoming})
        return {'action': action, 'pairs': pairs, 'channels': channels, 'connections': connections, 'unmatched_sources': [srcmap[k] for k in srcmap if k not in dstmap], 'unmatched_destinations': [dstmap[k] for k in dstmap if k not in srcmap], 'scene_write': True, 'file_write': False}
    selected = nodes(p.get('objects', cmds.ls(selection=True, long=True) or []), joints=action in ('lock_weights', 'unlock_weights'), writable=action in ('lock_weights', 'unlock_weights', 'import', 'transfer', 'copy'))
    if not selected:
        raise ValueError('Nonempty object scope required')
    if action in ('lock_weights', 'unlock_weights'):
        for n in selected:
            if cmds.getAttr(n + '.liw', lock=True) or cmds.listConnections(n + '.liw', source=True, destination=False):
                raise ValueError('Locked/driven influence lock attribute')
        return {'action': action, 'objects': selected, 'scene_write': True, 'file_write': False}
    rows = [mesh(n) for n in selected]
    if action in ('info', 'select_weighted', 'export', 'copy', 'transfer') and not rows[0]['skin']:
        raise ValueError('Source must have one skinCluster')
    if action in ('copy', 'transfer'):
        if len(rows) < 2:
            raise ValueError('Source first, at least one destination')
        for row in rows[1:]:
            weight_writable(row)
            if action == 'copy' and not row['skin']:
                raise ValueError('Copy requires already bound targets')
            if action == 'transfer' and p['delete_history']:
                for h in cmds.listHistory(row['shape']) or []:
                    if cmds.referenceQuery(h, isNodeReferenced=True) or any(cmds.lockNode(h, query=True, lock=True)):
                        raise ValueError('Locked/referenced target history')
        return {'action': action, 'meshes': rows, 'scene_write': True, 'file_write': False}
    if action in ('info', 'select_weighted'):
        if any(not row['skin'] for row in rows):
            raise ValueError('Every info object must be skinned')
        return {'action': action, 'meshes': rows, 'scene_write': action == 'select_weighted', 'file_write': False}
    directory = checked_dir(p.get('directory'))
    if 'basename' in p and len(rows) != 1:
        raise ValueError('Explicit basename supports one mesh; batch derives unique stripped names')
    files = []
    used = set()
    for row in rows:
        base = basename(p.get('basename', row['object'].rsplit('|', 1)[-1].rsplit(':', 1)[-1]))
        if base in used:
            raise ValueError('Batch output basename collision')
        used.add(base)
        weightbase = base + '_sknCls' if p['convention'] == 'timal' else base
        paths = {'txt': directory / (base + '.txt'), 'meta': directory / (base + '.staging.json'), **{f: directory / (weightbase + '.' + f) for f in p['formats']}}
        if action == 'export':
            if not row['skin'] or any(path.exists() or path.is_symlink() for path in paths.values()):
                raise ValueError('Export requires skin and exclusive new files; no overwrite')
            for influence in row['weighted'] if p['convention'] == 'skininfo' else row['influences']:
                if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_:|]*', influence):
                    raise ValueError('Unsupported influence name for safe text interchange')
        else:
            joints = influence_file(paths['txt'], p['convention'])
            if action == 'import':
                weight_writable(row)
                if not row['skin'] and not p['create_skin']:
                    raise ValueError('Existing skin required when create_skin=False')
                for joint in joints:
                    if cmds.getAttr(joint + '.liw'):
                        raise ValueError('Imported influence is weight locked')
                if row['skin'] and any(j not in nodes(row['influences'], joints=True) for j in joints):
                    raise ValueError('Existing skin missing imported influences; add explicitly first')
                for fmt in p['formats']:
                    path = paths[fmt]
                    if not path.is_file() or path.is_symlink() or path.stat().st_size > 100_000_000:
                        raise ValueError('Missing/linked/oversized weight file')
                    data = path.read_bytes()
                    if fmt == 'xml':
                        if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
                            raise ValueError('XML entities unsupported')
                        ET.fromstring(data)
                    else:
                        json.loads(data, parse_constant=lambda v: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
                if paths['meta'].is_file():
                    if paths['meta'].is_symlink() or paths['meta'].stat().st_size > 1_000_000:
                        raise ValueError('Unsafe metadata')
                    metadata = json.loads(paths['meta'].read_text(encoding='utf8'))
                    if metadata.get('topology_sha256') != row['topology_sha256']:
                        raise ValueError('Index import topology differs from exported mesh')
                elif not p['allow_unchecked_topology']:
                    raise ValueError('Legacy map lacks topology metadata; explicit allow_unchecked_topology required')
            row['import_joints'] = joints
        files.append({'mesh': row, 'basename': base, 'paths': {k: str(v) for k, v in paths.items()}})
    return {'action': action, 'files': files, 'objects': selected, 'scene_write': action in ('import', 'select_influences'), 'file_write': action == 'export'}


def execute(p):
    result = plan(p)
    action = p['action']
    selection = cmds.ls(selection=True, long=True) or []
    identifiers = [cmds.ls(n, uuid=True)[0] for n in selection]
    try:
        if action in ('inspect', 'info'):
            return result
        if action == 'select_weighted':
            cmds.select(list(dict.fromkeys(n for row in result['meshes'] for n in row['weighted'])), replace=True)
        elif action == 'select_influences':
            cmds.select(list(dict.fromkeys(n for row in result['files'] for n in row['mesh']['import_joints'])), add=True)
        elif action in ('lock_weights', 'unlock_weights'):
            for n in result['objects']:
                cmds.setAttr(n + '.liw', action == 'lock_weights')
        elif action == 'export':
            created = []
            try:
                # Reserve every file before Maya writes, so batch cannot partially
                # overwrite an existing path between preflight and execute.
                for row in result['files']:
                    for name in row['paths'].values():
                        path = Path(name)
                        with path.open('xb'):
                            pass
                        created.append(path)
                for row in result['files']:
                    data = row['mesh']
                    joints = data['weighted'] if p['convention'] == 'skininfo' else data['influences']
                    text = ''.join(('select -add "' + n + '";\n') if p['convention'] == 'skininfo' else n + '\n' for n in joints)
                    Path(row['paths']['txt']).write_text(text, encoding='utf8')
                    Path(row['paths']['meta']).write_text(json.dumps({'topology_sha256': data['topology_sha256'], 'vertex_count': data['vertex_count'], 'influences': joints}), encoding='utf8')
                    for fmt in p['formats']:
                        path = Path(row['paths'][fmt])
                        cmds.deformerWeights(path.name, export=True, deformer=data['skin'], path=str(path.parent), format=fmt.upper())
            except Exception:
                for path in created:
                    path.unlink(missing_ok=True)
                raise
        elif action == 'import':
            for row in result['files']:
                data = row['mesh']
                skin = data['skin']
                saved = skin_weights(skin, data['shape']) if skin else None
                if not skin:
                    skin = cmds.skinCluster(data['import_joints'], data['object'], toSelectedBones=True, normalizeWeights=2 if p['post_normalize'] else 1, skinMethod=2 if p['convention'] == 'skininfo' else 0)[0]
                fmt = p['formats'][0]
                path = Path(row['paths'][fmt])
                cmds.deformerWeights(path.name, im=True, method='index', deformer=skin, path=str(path.parent), format=fmt.upper())
                if not p['post_normalize']:
                    cmds.skinCluster(skin, edit=True, forceNormalizeWeights=True)
                if saved:
                    # Native deformerWeights is not reliably Undo-aware across
                    # versions. Replay imported values through undoable skinPercent.
                    imported = skin_weights(skin, data['shape'])
                    saved['fn'].setWeights(saved['dag'], saved['component'], om.MIntArray(range(saved['count'])), saved['weights'], False)
                    names = [path.fullPathName() for path in imported['fn'].influenceObjects()]
                    for index in range(data['vertex_count']):
                        values = [(n, imported['weights'][index*imported['count']+i]) for i,n in enumerate(names)]
                        cmds.skinPercent(skin, data['object']+'.vtx['+str(index)+']', transformValue=values, normalize=False)
        elif action in ('transfer', 'copy'):
            source = result['meshes'][0]
            for target in result['meshes'][1:]:
                skin = target['skin']
                if action == 'transfer' and p['delete_history']:
                    cmds.delete(target['object'], constructionHistory=True)
                    skin = None
                if not skin:
                    skin = cmds.skinCluster(source['influences'], target['object'], toSelectedBones=True)[0]
                cmds.copySkinWeights(sourceSkin=source['skin'], destinationSkin=skin, noMirror=True, normalize=True, surfaceAssociation='closestPoint', influenceAssociation=['name', 'closestJoint'])
                if action == 'transfer':
                    cmds.skinPercent(skin, target['object'], pruneWeights=0.05)
                    cmds.skinCluster(skin, edit=True, removeUnusedInfluence=True)
        elif action == 'connect':
            if p['mode'] == 'direct':
                for row in result['connections']:
                    cmds.connectAttr(row['source'], row['destination'], force=p['allow_replace_connections'])
            else:
                skip_t = [axis for axis in 'xyz' if 't'+axis not in result['channels']]
                skip_r = [axis for axis in 'xyz' if 'r'+axis not in result['channels']]
                for src, dst in result['pairs']:
                    if p['mode'] == 'parent':
                        cmds.parentConstraint(src, dst, maintainOffset=p['maintain_offset'], skipTranslate=skip_t or ['none'], skipRotate=skip_r or ['none'])
                    else:
                        if p['mode'] in ('point', 'point_orient') and len(skip_t) < 3:
                            cmds.pointConstraint(src, dst, maintainOffset=p['maintain_offset'], skip=skip_t or ['none'])
                        if p['mode'] in ('orient', 'point_orient') and len(skip_r) < 3:
                            cmds.orientConstraint(src, dst, maintainOffset=p['maintain_offset'], skip=skip_r or ['none'])
        return result
    finally:
        if action not in ('select_weighted', 'select_influences'):
            selected = [cmds.ls(identifier, long=True)[0] for identifier in identifiers if cmds.ls(identifier, long=True)]
            cmds.select(selected, replace=True) if selected else cmds.select(clear=True)


def skin_weights(skin, shape):
    sl = om.MSelectionList()
    sl.add(skin)
    fn = oma.MFnSkinCluster(sl.getDependNode(0))
    sl2 = om.MSelectionList()
    sl2.add(shape)
    dag = sl2.getDagPath(0)
    component_fn = om.MFnSingleIndexedComponent()
    component = component_fn.create(om.MFn.kMeshVertComponent)
    component_fn.addElements(range(om.MFnMesh(dag).numVertices))
    weights, count = fn.getWeights(dag, component)
    return {'fn': fn, 'dag': dag, 'component': component, 'weights': weights, 'count': count}
