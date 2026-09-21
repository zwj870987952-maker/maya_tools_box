import maya.cmds as cmds

def ask_action():
    result = cmds.confirmDialog(
        title='文件操作',
        message='请选择对该文件的操作方式：',
        button=['打开', '导入', '引用', '取消'],
        defaultButton='导入',
        cancelButton='取消',
        dismissString='取消'
    )
    if result == '打开':
        return 'open'
    elif result == '导入':
        return 'import'
    elif result == '引用':
        return 'reference'
    else:
        return None 