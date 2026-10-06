import os, sys, maya.cmds as cmds
import importlib

n = "global_offset"
f = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Global_Offset")

if os.path.exists(f):
    if f not in sys.path:
        sys.path.insert(0, f)
    
    if n in sys.modules:
        mod = importlib.reload(sys.modules[n])
    else:
        mod = importlib.import_module(n)
    
    sys.modules[n] = mod
    mod.run()
