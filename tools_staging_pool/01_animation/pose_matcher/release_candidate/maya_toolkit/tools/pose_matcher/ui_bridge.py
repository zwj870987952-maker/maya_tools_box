"""Route original scene/file buttons through the checked API; keep full original layout."""
from maya import cmds
from .tool import PoseMatcherTool

PREFIX = 'mtkPoseCandidate_'
BOUND = False


def text(name):
    return cmds.textField(PREFIX + name, q=True, text=True)


def rows():
    a = cmds.textScrollList(PREFIX + 'mhJointsList', q=True, allItems=True) or []
    b = cmds.textScrollList(PREFIX + 'dazJointsList', q=True, allItems=True) or []
    if len(a) != len(b) or len(set(a)) != len(a):
        raise ValueError('Mapping rows must be aligned with unique source joints')
    return dict(zip(a, b))


def call(**kwargs):
    result = PoseMatcherTool().run(**kwargs)
    if not result.success:
        cmds.warning(result.message + ': ' + '; '.join(result.errors))
    return result


def overwrite(paths):
    from pathlib import Path
    if not any(Path(p).exists() for p in paths):
        return False
    return cmds.confirmDialog(title='Overwrite output group', message='Replace these candidate output files?\n' + '\n'.join(paths), button=['Replace', 'Cancel'], defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel') == 'Replace'


def align(*_):
    # Save Map is an explicit original UI button; alignment no longer saves automatically.
    return call(action='align', source_root=text('mhRootField'), target_root=text('dazRootField'), joint_map=rows())


def save(path, data):
    from pathlib import Path
    exists = Path(path).exists()
    if exists and not overwrite([path]):
        return False
    return call(action='save_map', output_path=path, joint_map=data, overwrite=exists).success


def merge(*_):
    from pathlib import Path
    picked = cmds.fileDialog2(fileMode=0, fileFilter='OBJ Files (*.obj)')
    if not picked:
        return
    obj = Path(picked[0]).resolve()
    files = [str(obj), str(obj.with_name(obj.stem + '_MergeInfo.json'))]
    exists = any(Path(p).exists() for p in files)
    if exists and not overwrite(files):
        return
    return call(action='merge', output_path=str(obj), overwrite=exists)


def split(*_):
    from pathlib import Path
    info = cmds.fileDialog2(fileMode=1, fileFilter='JSON Files (*.json)')
    if not info:
        return
    output = cmds.fileDialog2(fileMode=0, caption='Output prefix (creates Part1.obj and Part2.obj)', fileFilter='OBJ Files (*.obj)')
    if not output:
        return
    base = Path(output[0]).resolve().with_suffix('')
    files = [str(base.with_name(base.name + '_Part1.obj')), str(base.with_name(base.name + '_Part2.obj'))]
    exists = any(Path(p).exists() for p in files)
    if exists and not overwrite(files):
        return
    return call(action='split', map_path=info[0], output_path=output[0], overwrite=exists)


def remove(*_):
    a = cmds.textScrollList(PREFIX + 'mhJointsList', q=True, allItems=True) or []
    b = cmds.textScrollList(PREFIX + 'dazJointsList', q=True, allItems=True) or []
    if len(a) != len(b):
        raise ValueError('Mapping table row counts differ')
    indices = set((cmds.textScrollList(PREFIX + 'mhJointsList', q=True, selectIndexedItem=True) or []) + (cmds.textScrollList(PREFIX + 'dazJointsList', q=True, selectIndexedItem=True) or []))
    for name, items in (('mhJointsList', a), ('dazJointsList', b)):
        cmds.textScrollList(PREFIX + name, e=True, removeAll=True)
        kept = [x for i, x in enumerate(items, 1) if i not in indices]
        if kept:
            cmds.textScrollList(PREFIX + name, e=True, append=kept)


def bind(native):
    global BOUND
    if BOUND:
        return
    from .runtime import input_json, map_data
    native.load_joint_map = lambda path: map_data(input_json(path))
    native.save_joint_map = save
    native.execute_alignment_cmd = align
    native.MergeMeshes_cmd = merge
    native.SplitMeshes_cmd = split
    native.remove_selected_cmd = remove
    original_reset = native.reset_table
    native.reset_table = lambda *_: original_reset()
    original_sync = native.sync_selections
    def sync(*args):
        try:
            original_sync(*args)
        finally:
            native._syncing_selection = False
    native.sync_selections = sync
    BOUND = True
