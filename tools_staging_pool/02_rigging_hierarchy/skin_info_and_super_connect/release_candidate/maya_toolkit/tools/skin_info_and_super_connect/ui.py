"""All original layouts; every scene/file callback uses the guarded API."""
from pathlib import Path
from maya import cmds, mel
from .tool import SkinInfoSuperConnectTool
from .operations import PKG, resources
from .timal_original import exportImportJointsWeight


def call(**p):
    result = SkinInfoSuperConnectTool().run(**p)
    if not result.success:
        cmds.warning(result.message)
    return result


def selected_meshes():
    return [n for n in cmds.ls(selection=True, long=True, type='transform') or [] if cmds.listRelatives(n, shapes=True, noIntermediate=True, type='mesh')]


def dispatch(suite, procedure):
    prefix = 'scpstg_' + suite + '_'
    def cb(name, default=False):
        return cmds.checkBox(prefix + name, query=True, value=True) if cmds.control(prefix + name, exists=True) else default
    def text(name, group='textFieldGrp'):
        return getattr(cmds, group)(prefix + name, query=True, text=True)
    def settext(name, value, group='textFieldGrp'):
        getattr(cmds, group)(prefix + name, edit=True, text=str(value))
    if suite == 'connect':
        if procedure in ('Store_01', 'Store_02'):
            name = prefix + ('ChangeControlsTSL_01' if procedure == 'Store_01' else 'ChangeControlsTSL_02')
            cmds.textScrollList(name, edit=True, removeAll=True)
            selected = cmds.ls(selection=True, long=True) or []
            if selected:
                cmds.textScrollList(name, edit=True, append=selected)
            return ''
        mode = 'direct' if cmds.radioButton(prefix+'RB1', query=True, select=True) else 'parent' if cmds.radioButton(prefix+'RB2', query=True, select=True) else 'point_orient'
        channels = []
        maintain = True
        if mode == 'direct':
            for group, key in (('Direct_T_CHB', 't'), ('Direct_R_CHB', 'r'), ('Direct_S_CHB', 's')):
                channels.extend(key+axis for i, axis in enumerate('xyz', 1) if cmds.checkBoxGrp(prefix+group, query=True, **{'value'+str(i): True}))
        elif mode == 'parent':
            maintain = cmds.checkBoxGrp(prefix+'Parent_constraints_CHB', query=True, value1=True)
            if cmds.checkBoxGrp(prefix+'Parent_constraints_CHB', query=True, value2=True):
                channels = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        else:
            maintain = cmds.checkBoxGrp(prefix+'Point_Orient_constraints_CHB', query=True, value1=True)
            for i, key in ((2, 't'), (3, 'r')):
                if cmds.checkBoxGrp(prefix+'Point_Orient_constraints_CHB', query=True, **{'value'+str(i): True}):
                    channels.extend(key+a for a in 'xyz')
        call(action='connect', sources=cmds.textScrollList(prefix+'ChangeControlsTSL_02', query=True, allItems=True) or [], destinations=cmds.textScrollList(prefix+'ChangeControlsTSL_01', query=True, allItems=True) or [], source_prefix=text('SourceTXF'), destination_prefix=text('DestinationTXF'), mode=mode, channels=channels, maintain_offset=maintain, allow_replace_connections=cb('allowReplace'))
        return ''
    if procedure == 'ChechMayaVer':
        return ''
    if procedure in ('BrowseToExport', 'BrowseToImport'):
        importing = procedure == 'BrowseToImport'
        found = cmds.fileDialog2(fileMode=1 if importing else 3, fileFilter='Influences (*.txt)' if importing else None)
        if found:
            settext('tFButton_import' if importing else 'tFButton_export', found[0], 'textFieldButtonGrp')
        return ''
    objects = selected_meshes()
    if procedure == 'AutoImport':
        if not objects:
            cmds.warning('Select one mesh')
            return ''
        path = Path(text('tFButton_import', 'textFieldButtonGrp'))
        settext('tFButton_import', str(path.parent / (objects[0].rsplit('|',1)[-1].rsplit(':',1)[-1]+'.txt')), 'textFieldButtonGrp')
        return ''
    if procedure in ('GetInfo', 'SelectWeightedJnts'):
        result = call(action='info' if procedure == 'GetInfo' else 'select_weighted', objects=objects[:1])
        if result.success and procedure == 'GetInfo':
            row = result.data['meshes'][0]
            settext('TextF_TotalInfluences', len(row['influences']))
            settext('TextF_WeightedInfluences', len(row['weighted']))
            settext('TextF_FileName', objects[0].rsplit('|',1)[-1].rsplit(':',1)[-1])
        return ''
    if procedure in ('LockSelectedJoints', 'UnLockSelectedJoints'):
        call(action='lock_weights' if procedure == 'LockSelectedJoints' else 'unlock_weights', objects=cmds.ls(selection=True, long=True, type='joint') or [])
        return ''
    if procedure in ('TransferSkin', 'CopySkinAll'):
        call(action='transfer' if procedure == 'TransferSkin' else 'copy', objects=objects, delete_history=cb('DeleteHistoryChBox') if procedure == 'TransferSkin' else False, allow_delete_history=cb('allowDelete'))
        return ''
    if procedure in ('ExportInfo', 'ExportAllInfo'):
        p = {'action': 'export', 'objects': objects if procedure == 'ExportAllInfo' else objects[:1], 'directory': text('tFButton_export', 'textFieldButtonGrp'), 'formats': [f for key, f in (('CHB_XML','xml'), ('CHB_JSON','json')) if cb(key, default=key=='CHB_XML')]}
        if procedure == 'ExportInfo':
            p['basename'] = text('TextF_FileName')
        call(**p)
        return ''
    if procedure in ('SelectInfluences', 'ImportSkin_proc', 'AutoImportAllSelection'):
        path = Path(text('tFButton_import', 'textFieldButtonGrp'))
        p = {'action': 'select_influences' if procedure == 'SelectInfluences' else 'import', 'objects': objects if procedure == 'AutoImportAllSelection' else objects[:1], 'directory': str(path.parent), 'formats': ['json' if cb('CHB_JSON2') else 'xml'], 'allow_unchecked_topology': cb('allowTopology')}
        if procedure != 'AutoImportAllSelection':
            p['basename'] = path.stem
        call(**p)
        return ''
    raise ValueError('Unmapped original UI procedure: ' + procedure)


class TimalSafe(exportImportJointsWeight):
    def loadFolder(self):
        result = cmds.fileDialog2(dialogStyle=2, fileMode=3)
        if result:
            cmds.textFieldButtonGrp('folderPathField', edit=True, text=result[0])

    def exportWeights(self, unused=None):
        return call(action='export', objects=selected_meshes(), directory=cmds.textFieldButtonGrp('folderPathField', query=True, text=True), convention='timal')

    def importWeights(self, unused=None):
        return call(action='import', objects=selected_meshes(), directory=cmds.textFieldButtonGrp('folderPathField', query=True, text=True), convention='timal', create_skin=not cmds.checkBox('skinnedCB', query=True, value=True), post_normalize=cmds.checkBox('postCB', query=True, value=True), allow_unchecked_topology=cmds.checkBox('scpstg_timal_allowTopology', query=True, value=True))

    def exportImportWeightsUI(self):
        if cmds.window('ExportImportJointsWeight', exists=True):
            cmds.showWindow('ExportImportJointsWeight')
            return
        # Original full class layout and labels, virtual callbacks dispatch safely.
        super().exportImportWeightsUI()
        cmds.setParent('mainColumn')
        cmds.checkBox('scpstg_timal_allowTopology', label='Allow legacy maps without topology metadata', value=False)


def show_suite(suite):
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    resources()
    if suite == 'timal':
        TimalSafe().exportImportWeightsUI()
        return 'ExportImportJointsWeight'
    window = 'scpstg_'+suite+'_'+('Super_Connect' if suite == 'connect' else 'SkinInfo')
    if cmds.window(window, exists=True):
        cmds.showWindow(window)
        return window
    mel.eval((PKG / (suite+'_ui.mel')).read_text(encoding='utf8'))
    mel.eval('scpstg_'+suite+'_showUI();')
    cmds.setParent(window)
    cmds.columnLayout(adjustableColumn=True)
    if suite == 'connect':
        cmds.checkBox('scpstg_'+suite+'_allowReplace', label='Allow replacing existing direct connections', value=False)
    else:
        cmds.checkBox('scpstg_'+suite+'_allowDelete', label='Allow deleting target construction history', value=False)
        cmds.checkBox('scpstg_'+suite+'_allowTopology', label='Allow legacy maps without topology metadata', value=False)
    return window


def show_ui():
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    name = 'stagingSkinSuiteLauncher'
    if cmds.window(name, exists=True):
        cmds.showWindow(name)
        return name
    cmds.window(name, title='Skin Info / Super Connect / Timal')
    cmds.columnLayout(adjustableColumn=True)
    for suite, label in (('skin192','Skin Info 1.92 完整界面'), ('skin17','Skin Info 1.7 完整界面'), ('connect','Super Connect 完整界面'), ('timal','Timal 1.3 完整界面')):
        cmds.button(label=label, command=lambda unused=False, value=suite: show_suite(value))
    cmds.showWindow(name)
    return name
