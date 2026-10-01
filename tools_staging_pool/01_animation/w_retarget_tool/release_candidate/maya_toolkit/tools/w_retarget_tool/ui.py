"""Full original four-row UI with safe framework callbacks."""
from pathlib import Path
from maya import cmds
from .native_ui import CopyAnimation


class CandidateUI(CopyAnimation):
    def __init__(self, tool):
        self.tool = tool
        super().__init__()

    def _frames(self):
        return {'start_frame': cmds.intFieldGrp(self.StartFrameField, query=True, value1=True), 'end_frame': cmds.intFieldGrp(self.EndFrameField, query=True, value1=True)}

    def _run(self, **params):
        frames = self._frames()
        dry = self.tool.run(dry_run=True, **frames, **params)
        if not dry.success:
            cmds.warning(dry.message)
            return dry
        maximum = dry.data['sample_count'] * len(dry.data.get('pairs', [None]))
        cmds.progressBar(self.ProgressControl, edit=True, maxValue=maximum, progress=0, beginProgress=True)
        self.tool._progress_control = self.ProgressControl
        try:
            result = self.tool.run(**frames, **params)
            if not result.success:
                cmds.warning(result.message + '; partial keys, if any, can be undone')
            else:
                cmds.text(self.remainingTime, edit=True, label=result.message)
            return result
        finally:
            self.tool._progress_control = None
            cmds.progressBar(self.ProgressControl, edit=True, endProgress=True)

    def CopyAnim(self, source='', target='', ValidObj=1, initTime=0, *args):
        return self._run(action='copy', pairs=[{'source': source, 'target': target}])

    def CopyAll(self, *args):
        pairs = []
        for letter in 'ABCD':
            source = cmds.textFieldButtonGrp(getattr(self, 'SrcObject' + letter), query=True, text=True).strip()
            target = cmds.textFieldButtonGrp(getattr(self, 'TgtObject' + letter), query=True, text=True).strip()
            if source or target:
                pairs.append({'source': source, 'target': target})
        return self._run(action='copy', pairs=pairs)

    def _copy_row(self, letter):
        return self.CopyAnim(source=cmds.textFieldButtonGrp(getattr(self, 'SrcObject' + letter), query=True, text=True).strip(), target=cmds.textFieldButtonGrp(getattr(self, 'TgtObject' + letter), query=True, text=True).strip())

    def SetDestinationFolder(self, *args):
        paths = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption='Choose directory')
        if paths:
            cmds.textFieldButtonGrp(self.DestinationFolder, edit=True, text=paths[0])

    def ButtonExport(self, *args):
        from .tool import resolve
        try:
            names = []
            for letter in 'ABCD':
                target = cmds.textFieldButtonGrp(getattr(self, 'TgtObject' + letter), query=True, text=True).strip()
                if target:
                    leaf = resolve(target).rsplit('|', 1)[-1]
                    namespace, separator, name = leaf.rpartition(':')
                    if not separator:
                        raise ValueError('Export UI requires namespaced targets and namespace geometry/Jnts_grp')
                    if namespace not in names:
                        names.append(namespace)
            directory = Path(cmds.textFieldButtonGrp(self.DestinationFolder, query=True, text=True))
            jobs = [{'nodes': [ns + ':' + ns.rsplit(':', 1)[-1] + '_geo', ns + ':Jnts_grp'], 'path': str(directory / (ns.replace(':', '_') + '.fbx'))} for ns in names]
            return self._run(action='export', exports=jobs, up_axis=cmds.optionMenuGrp(self.OptionMenuAxis, query=True, value=True).lower(), ascii=cmds.optionMenuGrp(self.FileType, query=True, value=True) == 'ASCII', fbx_version=cmds.optionMenuGrp(self.FBXVersion, query=True, value=True) + '00', bake=cmds.checkBoxGrp(self.CheckBackeAnim, query=True, value1=True))
        except Exception as exc:
            cmds.warning(str(exc))


def selection_callback(field):
    def callback(self, *args):
        from .tool import resolve
        selection = cmds.ls(selection=True, long=True) or []
        if not selection:
            cmds.warning('Select a source/target transform first')
            return
        try:
            node = resolve(selection[0])
            cmds.textFieldButtonGrp(getattr(self, field), edit=True, text=node)
        except Exception as exc:
            cmds.warning(str(exc))
    return callback


for _letter in 'ABCD':
    for _side in ('Src', 'Tgt'):
        setattr(CandidateUI, 'Select' + _side + 'Object' + _letter, selection_callback(_side + 'Object' + _letter))
    setattr(CandidateUI, 'ButtonCopyAnim' + _letter, lambda self, *args, letter=_letter: self._copy_row(letter))


def show_ui(tool):
    return CandidateUI(tool)
