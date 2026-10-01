"""Full native MEL definitions are loaded only by explicit execution, never by validation."""
import builtins
import hashlib
import json
from pathlib import Path
import re
import tempfile
from maya import cmds, mel
from maya.api import OpenMaya as om
from . import file_guard
from .tool import catalog

PKG = Path(__file__).resolve().parent
BATCH = {'bb_CtrlTool_createShape', 'bb_CtrlTool_changeColorApply', 'bb_attr_addAttr', 'bb_returnSkinList', 'wpRename_js_replaceHash', 'bb_QC_shapes2transforms'}
READ_ONLY = {'bb_returnSkinList', 'wpRename_js_replaceHash', 'bb_QC_shapes2transforms'}
_loaded = False
_declared = {}


def resources():
    c = catalog()
    for folder, rows in (('vendor', c['files']), ('native', c['native_files']+c['support_files'])):
        for row in rows:
            path = PKG/folder/row['path']
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('Missing/changed bundled resource '+folder+'/'+row['path'])
    for row in c['files']:
        if Path(row['path']).suffix.lower() != '.mel':
            path = PKG/'native'/row['path']
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('Missing/changed native asset '+row['path'])


def quote(value):
    return json.dumps(str(value), ensure_ascii=False)


def conflicts():
    c = catalog()
    mapping = {d['native_name']: d['file'] for d in c['procedures'].values() if d['global_scope']}
    mapping['bbstg_JBPerVertWindow'] = 'Script/aboutJBPerVert.mel'
    mapping.update({name: 'bridge.mel' for name in ('staging_bb_scratch', 'staging_bb_qc_dir', 'staging_bb_open', 'staging_bb_copy', 'staging_bb_delete', 'staging_bb_system', 'staging_bb_qc_line')})
    for name, filename in mapping.items():
        value = mel.eval('whatIs '+name)
        if value == 'Unknown':
            continue
        expected = PKG/'native'/filename
        digest = hashlib.sha256(expected.read_bytes()).hexdigest()
        if value == 'Mel procedure entered interactively.' and _declared.get(name) == digest:
            continue
        if not value.startswith('Mel procedure found in:'):
            raise ValueError('Conflicting native command '+name+': '+repr(value)+' owned='+str(_declared.get(name) == digest))
        actual = Path(value.split(':', 1)[1].strip())
        if not actual.is_file() or hashlib.sha256(actual.read_bytes()).hexdigest() != hashlib.sha256(expected.read_bytes()).hexdigest():
            raise ValueError('Another BB candidate version defines '+name+'; use a fresh Maya session')


def nodes(values, editable=True):
    out = []
    for name in values:
        if '.' in name or any(x in name for x in ('*', '?', '[', ']', ';', '`', '"', '\n', '\r', '\\')):
            raise ValueError('Whole literal node name required')
        matches = cmds.ls(name, long=True) or []
        if len(matches) != 1:
            raise ValueError('Unique existing whole node required: '+name)
        node = matches[0]
        if node in out or len(cmds.ls(node, long=True, allPaths=True) or []) != 1:
            raise ValueError('Duplicate aliases/instanced nodes rejected')
        if editable:
            for target in [node]+(cmds.listRelatives(node, shapes=True, fullPath=True) or []):
                if cmds.referenceQuery(target, isNodeReferenced=True) or any(cmds.lockNode(target, query=True, lock=True)):
                    raise ValueError('Referenced/locked input '+target)
        out.append(node)
    return out


def preflight(p):
    resources()
    c = catalog()
    if p['action'] == 'inspect':
        return {'action': 'inspect', 'files': c['files'], 'procedures': c['procedures'], 'entries': c['entries'], 'original_declarations': c['original_declarations'], 'active_declarations': c['active_declarations'], 'archive_only': c['archive_only'], 'license': c['license'], 'batch_procedures': sorted(BATCH), 'scene_write': False, 'file_write': False, 'gui_acceptance': 'not_run'}
    conflicts()
    proc = p['procedure']
    if proc not in BATCH and not p.get('allow_scene_scope'):
        raise ValueError('Interactive native calls require allow_scene_scope=True; scope may include the whole scene')
    if cmds.about(batch=True) and proc not in BATCH:
        raise ValueError('This original workflow needs interactive Maya; no batch substitute')
    if proc not in READ_ONLY and not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable scene Undo before writing calls')
    values = p['objects'] or (cmds.ls(selection=True, long=True) or [])
    resolved = nodes(values, editable=proc not in READ_ONLY)
    args = p['arguments']
    if proc in ('bb_CtrlTool_changeColorApply', 'bb_attr_addAttr', 'bb_returnSkinList'):
        explicit = nodes([args[0]], editable=proc != 'bb_returnSkinList')[0]
        if explicit not in resolved:
            raise ValueError('Argument object must belong to explicit objects/selection')
        if proc == 'bb_CtrlTool_changeColorApply':
            shapes = cmds.listRelatives(explicit, shapes=True, fullPath=True) or []
            if not shapes:
                raise ValueError('Color operation requires shapes')
            for shape in shapes:
                for attr in ('overrideEnabled', 'overrideColor'):
                    plug = shape+'.'+attr
                    if cmds.getAttr(plug, lock=True) or cmds.listConnections(plug, source=True, destination=False):
                        raise ValueError('Locked/driven shape override channel')
        if proc == 'bb_attr_addAttr' and cmds.attributeQuery(args[1][0], node=explicit, exists=True):
            raise ValueError('Existing attribute protected')
    if proc == 'bb_CtrlTool_createShape' and cmds.objExists(args[1]):
        raise ValueError('Existing controller name protected')
    if proc == 'bb_QC_shapes2transforms' and args[0] not in ('mesh', 'nurbsSurface', 'nurbsCurve', 'camera', 'light'):
        raise ValueError('Expected supported Maya shape type')
    return {'action': 'call', 'procedure': proc, 'arguments': args, 'objects': resolved, 'command': p['command'], 'signature': c['procedures'][proc], 'scene_write': proc not in READ_ONLY, 'file_write': proc not in BATCH, 'batch_supported': proc in BATCH, 'gui_acceptance': 'not_run', 'native_scope': 'Interactive callbacks retain original connected-node/whole-scene and UI scope; isolated selected algorithms only are checked'}


def io_request(action, a, b):
    if action == 'weight_dir':
        # A fresh directory per conversion prevents stale/interrupted XML overwrites.
        return Path(tempfile.mkdtemp(prefix='weights_', dir=file_guard.scratch())).as_posix()+'/'
    if action == 'qc_dir':
        path = file_guard.scratch()/'QC_sets'
        path.mkdir(exist_ok=True)
        return path.as_posix()
    if action == 'reserve':
        return file_guard.reserve(a)
    if action == 'delete':
        return file_guard.delete_scratch(a)
    if action == 'copy':
        # Verify the complete settings file before placing it in the local menu.
        for line in Path(a).read_text(encoding='utf-8-sig').splitlines():
            file_guard.parse_qc_line(line)
        return file_guard.copy_file(a, b)
    if action == 'system':
        return file_guard.system_request(a)
    if action == 'qc_line':
        parsed = file_guard.parse_qc_line(a)
        if parsed:
            kind, control, value = parsed
            if kind == 'checkbox':
                cmds.checkBox(control, edit=True, value=value)
            elif kind == 'text':
                cmds.textField(control, edit=True, text=value)
            elif kind == 'clear_list':
                cmds.textScrollList(control, edit=True, removeAll=True)
            else:
                cmds.textScrollList(control, edit=True, append=value)
        return 1
    raise ValueError('Unknown native IO operation')


def load_native():
    global _loaded
    resources()
    conflicts()
    if _loaded:
        return
    for name, callback in (('_bb_staging_io', io_request), ('_bb_staging_cleanup_ui', cleanup_ui)):
        existing = getattr(builtins, name, None)
        if existing is not None and existing is not callback:
            raise ValueError('Another candidate owns the native Python bridge; restart Maya')
        setattr(builtins, name, callback)
    mel.eval('global string $bbstg_bundleRoot; $bbstg_bundleRoot='+quote((PKG/'native').as_posix()+'/')+';')
    mel.eval('source '+quote(PKG/'native/bridge.mel')+';')
    for row in catalog()['native_files']:
        # Windows MEL source uses the local legacy code page. Pass decoded Unicode
        # through the Python MEL evaluator instead, preserving Chinese labels.
        source = PKG/'native'/row['path']
        mel.eval(source.read_text(encoding='utf-8'))
        for name, item in catalog()['procedures'].items():
            if item['global_scope'] and item['file'] == row['path']:
                _declared[item['native_name']] = row['sha256']
        if row['path'] == 'Script/aboutJBPerVert.mel':
            _declared['bbstg_JBPerVertWindow'] = row['sha256']
    _loaded = True


def uuids():
    return {cmds.ls(n, uuid=True)[0] for n in cmds.ls(long=True) or []}


def execute(p):
    plan = preflight(p)
    if p['action'] == 'inspect':
        return plan
    load_native()
    state = {'time': cmds.currentTime(query=True), 'selection': [cmds.ls(n, uuid=True)[0] for n in cmds.ls(selection=True, long=True) or []], 'namespace': cmds.namespaceInfo(currentNamespace=True), 'autokey': cmds.autoKeyframe(query=True, state=True)}
    before = uuids()
    depth = [0]
    def callback(command, *unused):
        if re.match(r'\s*undoInfo\b', command):
            depth[0] += int(bool(re.search(r'-(?:ock|openChunk)\b', command)))
            depth[0] -= int(bool(re.search(r'-(?:cck|closeChunk)\b', command)))
    hook = om.MCommandMessage.addCommandCallback(callback)
    try:
        cmds.autoKeyframe(state=False)
        if plan['objects']:
            cmds.select(plan['objects'], replace=True)
        result = mel.eval(p['command'])
        if depth[0] < 0:
            raise RuntimeError('Native call closed an outer Undo chunk')
        return dict(plan, native_result=result, native_result_selection=cmds.ls(selection=True, long=True) or [], created_node_uuids=sorted(uuids()-before))
    finally:
        om.MMessage.removeCallback(hook)
        try:
            for unused in range(max(depth[0], 0)):
                cmds.undoInfo(closeChunk=True)
        finally:
            cmds.currentTime(state['time'])
            cmds.autoKeyframe(state=state['autokey'])
            cmds.namespace(setNamespace=state['namespace'])
            surviving = [n for identity in state['selection'] for n in (cmds.ls(identity, long=True) or [])]
            cmds.select(surviving, replace=True) if surviving else cmds.select(clear=True)


def cleanup_ui():
    """Explicit review of exact suspicious files/nodes; never blanket-delete userSetup."""
    if cmds.about(batch=True):
        raise RuntimeError('Cleanup review requires interactive Maya')
    root = Path(cmds.internalVar(userAppDir=True))/'scripts'
    files = [root/name for name in ('vaccine.py', 'vaccine.pyc', 'userSetup.py') if (root/name).is_file()]
    scene_nodes = [n for n in ('breed_gene', 'vaccine_gene') if cmds.objExists(n)]
    window = 'bbstg_cleanup_review'
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    cmds.window(window, title='BB 病毒清理：选择文件后隔离，保留恢复副本', widthHeight=(620, 350))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='userSetup.py 可能包含个人启动代码；仅隔离你选中的文件。外部文件无法用 Maya Undo 恢复。', wordWrap=True)
    listing = cmds.textScrollList(allowMultiSelection=True, append=[str(x) for x in files], height=150)
    def quarantine(*unused):
        selected = cmds.textScrollList(listing, query=True, selectItem=True) or []
        if not selected:
            raise ValueError('先选择要隔离的具体文件')
        targets = cmds.fileDialog2(fileMode=3, caption='选择已有隔离目录') or []
        if not targets:
            return
        # Preflight every output before the first external change.
        pairs = [(p, str(Path(targets[0])/Path(p).name)) for p in selected]
        for src, dst in pairs:
            file_guard.checked_path(src)
            file_guard.new_output(dst)
        for src, dst in pairs:
            file_guard.copy_file(src, dst, move=True)
        cmds.textScrollList(listing, edit=True, removeItem=selected)
    cmds.button(label='将所选文件移入隔离目录（拒绝覆盖）', command=quarantine)
    def clean_scene(*unused):
        targets = nodes(scene_nodes)
        if targets:
            from maya_toolkit.core.context import UndoChunkContext
            with UndoChunkContext(chunk_name='BB_scene_virus_cleanup'):
                cmds.delete(targets)
    cmds.button(label='删除场景内 breed_gene / vaccine_gene（可 Undo）', command=clean_scene, enable=bool(scene_nodes))
    cmds.showWindow(window)
    return window


def show_member(member):
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for native BB interfaces')
    entries = catalog()['entries']
    if member not in entries:
        raise ValueError('Unknown native member')
    load_native()
    mel.eval('bbstg_'+entries[member]+'();')
    return member


def show_ui():
    return show_member('bb_Tools.mel')
