"""Original widgets remain intact. Scene actions use the same checked public API."""
from .tool import RetimeToolsTool


def call(**kwargs):
    result = RetimeToolsTool().run(**kwargs)
    if not result.success:
        raise RuntimeError(result.message + ': ' + str(result.errors))
    return result.data


class CheckedCore:
    def __getattr__(self, name):
        from .engine import CoreFunctions
        actions = {'create_new_retime_controller':'create', 'create_new_retime_controller_exec':'create',
            'addCurvesToTimewarp':'connect', 'completely_disconnect_retime':'disconnect', 'disconnect_curve':'disconnect',
            'bake_retime_controller':'bake', 'cleanSubframeKeys':'clean_subframes', 'update_old_retime_curve':'update_legacy'}
        if name in actions:
            def checked(*args, **kwargs):
                o = {'action':actions[name]}
                if name.startswith('create_new'):
                    o['name'] = kwargs.get('retime_controller',args[0] if args else 'retime_controller')
                elif args:
                    o['controller'] = args[0]
                if name=='disconnect_curve' and len(args)>1:
                    o['curves'] = args[1]
                if name=='cleanSubframeKeys' and kwargs.get('curve_nodes'):
                    o['curves'] = kwargs['curve_nodes']
                data = call(**o)
                return data['controller'] if name.startswith('create_new') else True
            return checked
        if name in ('set_retime_controller_state','reset_retime','invert_retime','delete_retime'):
            def state(c, value=None):
                from .engine import RetimeStates
                state_name = {1:'Enable',2:'Disable',3:'Reset',4:'Invert',5:'Disconnect',6:'Delete'}[value] if value is not None else {'reset_retime':'Reset','invert_retime':'Invert','delete_retime':'Delete'}[name]
                call(action='state',controller=c,state=state_name)
                return RetimeStates.Enable if state_name in ('Reset','Disconnect') else value
            return state
        if name=='update_old_retime_curves':
            return self.old_core.update_old_retime_curves
        if name=='select_maya_nodes':
            return self.old_core.select_maya_nodes
        return getattr(CoreFunctions,name)


class CheckedShuffle:
    @classmethod
    def process(cls, c):
        call(action='shuffle',controller=c)
        return True


def install(ns):
    core = CheckedCore()
    core.old_core = ns['CoreFunctions']
    core.old_core.update_old_retime_curve = classmethod(lambda cls,c: call(action='update_legacy',controller=c))
    ns['CoreFunctions'] = core
    ns['ShuffleKeys'] = CheckedShuffle
    # Whole shuffle+disconnect+optional rounding is one exception-safe Undo chunk.
    def shuffle(self,*args,**kwargs):
        c = self.get_data()
        if not c:
            return False
        call(action='shuffle',controller=c,clean=bool(args[0]) if args else False)
        self.scene_change.emit()
        return True
    ns['ActionsWidget'].action_shuffle = shuffle
