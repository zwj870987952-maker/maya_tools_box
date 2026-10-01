from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
import pyside2uic
myUI = 'C:\\Users\\rodri\\Documents\\maya\\2018\\scripts\\Folder\\name.ui'
myPY = 'C:\\Users\\rodri\\Documents\\maya\\2018\\scripts\\Folder\\name.py'
'\n\nimport os\nfrom maya import cmds\nimport maya.OpenMayaUI as omui\nfrom shiboken2 import wrapInstance\n\n\n\n\ndef getMayaWindow():\n    ptr = omui.MQtUtil.mainWindow()\n    if ptr:\n        return wrapInstance(long(ptr), QtWidgets.QmainWindow)\n        \ndef run():\n    global win\n    win = Ui_Form(parent = getMayaWindow())\n    win.show\n\n\n\n'


def run_script():
    exec(compile("myUI = 'C:\\\\Users\\\\rodri\\\\Documents\\\\maya\\\\2018\\\\scripts\\\\Folder\\\\name.ui'\nmyPY = 'C:\\\\Users\\\\rodri\\\\Documents\\\\maya\\\\2018\\\\scripts\\\\Folder\\\\name.py'\nwith checked_output() as thePython:\n    pyside2uic.compileUi(explicit_ui_input(), thePython, False, 4, False)", __file__, "exec"), globals())
