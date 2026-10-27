"""Entire original layout; every business button dispatches the safe API."""
from maya import cmds, mel
from .original_logic import RelationshipTool
from .tool import RelationshipToolsTool

_window = None


class RelationshipUI(RelationshipTool):
    def __init__(self):
        self.window_name = 'RelationshipToolWindow'
        self.world_coordinate_mode = False
        self.world_transform_data = {}
        self.world_space_btn = None
        self.DEFAULT_MAX_ATTEMPTS = 6
        self.DEFAULT_FULL_CHECK_ATTEMPTS = 6
        self.api = RelationshipToolsTool()
        self.setup_ui()
        cmds.setParent(self.main_layout)
        cmds.button(label='Export World Pose JSON', command=lambda *a: self.pose_file('export_pose'))
        cmds.button(label='Import World Pose JSON', command=lambda *a: self.pose_file('import_pose'))

    def option(self, name):
        control = {'translate': 'translate_checkbox', 'rotate': 'rotate_checkbox', 'bake': 'bake_checkbox', 'world_coords': 'world_coords_checkbox', 'layer': 'anim_layer_checkbox', 'step': 'frame_step'}[name]
        return cmds.intField(getattr(self, control), query=True, value=True) if name == 'step' else cmds.checkBox(getattr(self, control), query=True, value=True)

    def dispatch(self, action):
        p = {name: self.option(name) for name in ('translate', 'rotate', 'bake', 'world_coords', 'layer', 'step')}
        p.update(action=action, advance=action in ('one_step', 'more_step'))
        if action in ('align', 'mark_animation', 'more_step'):
            slider = mel.eval('$tmpVar=$gPlayBackSlider')
            if cmds.timeControl(slider, query=True, rangeVisible=True):
                p['frame_range'] = [int(n) for n in cmds.timeControl(slider, query=True, rangeArray=True)]
            elif action != 'align':
                p['frame_range'] = [int(cmds.playbackOptions(query=True, minTime=True)), int(cmds.playbackOptions(query=True, maxTime=True)) + 1]
        result = self.api.run(**p)
        if not result.success:
            cmds.warning(result.message)
        return result

    def mark_action(self, *args):
        return self.dispatch('mark')

    def mark_foot_action(self, *args):
        return self.dispatch('mark_foot')

    def mark_ani_action(self, *args):
        return self.dispatch('mark_animation')

    def world_space_action(self, *args):
        return self.dispatch('copy_world')

    def one_step_action(self, *args):
        return self.dispatch('one_step')

    def more_step_action(self, *args):
        return self.dispatch('more_step')

    def align_objects_action(self, *args):
        return self.dispatch('align')

    def delete_marks_action(self, *args):
        return self.dispatch('delete_marks')

    def pose_file(self, action):
        paths = cmds.fileDialog2(fileMode=0 if action == 'export_pose' else 1, fileFilter='JSON (*.json)') or []
        if paths:
            result = self.api.run(action=action, file_path=paths[0])
            if not result.success:
                cmds.warning(result.message)


def show_ui():
    global _window
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required for full Relationship UI')
    _window = RelationshipUI()
    return _window
