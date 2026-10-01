from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

PROPERTIES={'action':{'type':'string','enum':['inspect','reset'],'default':'reset'},'camera':{'type':'string','default':'persp'},'reset_rotation':{'type':'boolean','description':'Omit to use resetTransformationsRotate (default True if unset)'},'reset_scale':{'type':'boolean','description':'Omit to use resetTransformationsScale (default True if unset)'},'preserve_selection':{'type':'boolean','default':False}}


def normalize(kwargs):
    if set(kwargs)-set(PROPERTIES):
        raise ValueError('Unknown arguments')
    p=dict(kwargs)
    p.setdefault('action','reset')
    p.setdefault('camera','persp')
    p.setdefault('preserve_selection',False)
    if p['action'] not in ('inspect','reset') or not isinstance(p['camera'],str) or not p['camera']:
        raise ValueError('Invalid action or camera name')
    for name in ('reset_rotation','reset_scale','preserve_selection'):
        if name in p and type(p[name]) is not bool:
            raise ValueError(name+' must be boolean')
    return p


class CameraFFixTool(BaseMayaTool):
    tool_id='camera_f_fix'
    tool_name='按 F 相机重置'
    category='modeling_surfacing'
    version='1.0.0-candidate.1'
    description='Original persp ResetTransformations respecting rotation/scale preferences, then local translate (1,1,1); optional explicit perspective camera. Undoable; viewport F fix effectiveness awaits real Maya acceptance.'
    parameters_schema={'type':'object','properties':PROPERTIES,'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .operations import preflight
            return ToolResult.ok(message='Read-only perspective camera reset plan',data=preflight(normalize(kwargs)),dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from .operations import execute
        return ToolResult.ok(message='Camera local transform reset; actual F framing requires GUI acceptance',data=execute(normalize(kwargs)))

    def show_ui(self,parent=None):
        from .ui import show_ui
        return show_ui()
