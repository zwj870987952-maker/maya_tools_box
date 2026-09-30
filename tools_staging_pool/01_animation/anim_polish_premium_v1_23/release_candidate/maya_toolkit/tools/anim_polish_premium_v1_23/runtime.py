"""Lazy private runtime imports and finally restoration for framework calls."""
import importlib


def load(module):
    return importlib.import_module(__package__+'.vendor.animPolish.'+module)


def invoke(module,name,arguments):
    import maya.cmds as cmds
    previous_mode = cmds.evaluationManager(query=True,mode=True)
    suspended = cmds.refresh(query=True,suspend=True)
    track_order = cmds.selectPref(query=True,trackSelectionOrder=True)
    time = cmds.currentTime(query=True)
    errors, error, value = [],None,None
    try:
        function = getattr(load(module),name)
        value = function(**arguments)
    except Exception as caught:
        error = str(caught)
    finally:
        # Evaluation toggle/fixViewport deliberately change these switches.
        for label,read,write,old,skip in [
            ('evaluation',lambda:cmds.evaluationManager(query=True,mode=True),lambda v:cmds.evaluationManager(mode=v[0]),previous_mode,module=='ui' and name.startswith('toggleAnimEval')),
            ('refresh',lambda:cmds.refresh(query=True,suspend=True),lambda v:cmds.refresh(suspend=v),suspended,module=='ui' and name=='fixViewport'),
            ('trackSelectionOrder',lambda:cmds.selectPref(query=True,trackSelectionOrder=True),lambda v:cmds.selectPref(trackSelectionOrder=v),track_order,False),
            ('time',lambda:cmds.currentTime(query=True),lambda v:cmds.currentTime(v),time,module=='caching' and name=='imp_geos')]:
            if skip:
                continue
            try:
                if read()!=old:
                    write(old)
            except Exception as caught:
                errors.append(label+': '+str(caught))
    return dict(return_value=value,error=error,runtime_state_errors=errors)
