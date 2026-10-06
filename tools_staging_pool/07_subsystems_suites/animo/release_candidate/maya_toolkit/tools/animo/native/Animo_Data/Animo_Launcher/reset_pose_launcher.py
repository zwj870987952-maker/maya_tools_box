import os, sys, maya.cmds as cmds, importlib.machinery

n, v = "reset_pose", cmds.about(version=True).split()[0]
f = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Reset")

if os.path.exists(f):
    if f not in sys.path: sys.path.insert(0, f)
    if n in sys.modules: del sys.modules[n]
    py, pyc = os.path.join(f, n + ".py"), os.path.join(f, "{}_py{}.pyc".format(n, v))
    if os.path.exists(py):
        exec(compile(open(py).read(), py, "exec"), {"__name__": "__main__", "__file__": py})
    elif os.path.exists(pyc):
        importlib.machinery.SourcelessFileLoader(n, pyc).load_module(n)
