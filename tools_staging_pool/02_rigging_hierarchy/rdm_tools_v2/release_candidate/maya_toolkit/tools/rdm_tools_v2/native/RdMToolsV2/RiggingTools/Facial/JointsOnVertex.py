from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
def locOnVertex():
    cmds.undoInfo(openChunk=True)
    selList = getSelection()
    for c in selList:
        cmds.select(cl=1)
        cmds.joint(n='joint#', p=cmds.pointPosition(c), rad=0.25)
    cmds.undoInfo(closeChunk=True)

def getSelection():
    cmds.undoInfo(openChunk=True)
    components = cmds.ls(sl=1)
    selList = []
    objName = components[0][0:components[0].index('.')]
    for c in components:
        if ':' not in c:
            selList.append(c)
        else:
            print(c)
            startComponent = int(c[c.index('[') + 1:c.index(':')])
            endComponent = int(c[c.index(':') + 1:c.index(']')])
            componentType = c[c.index('.') + 1:c.index('[')]
            while startComponent <= endComponent:
                selList.append(objName + '.' + componentType + '[' + str(startComponent) + ']')
                startComponent += 1
    return selList
    cmds.undoInfo(closeChunk=True)
'\n\nlocOnVertex()\n\n'


def run_script():
    exec(compile('', __file__, "exec"), globals())
