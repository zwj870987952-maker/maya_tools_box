import maya.cmds as cmds

def get_namespace():
    result = cmds.promptDialog(
        title='命名空间',
        message='请输入命名空间：',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    if result == 'OK':
        return cmds.promptDialog(query=True, text=True)
    else:
        return '' 