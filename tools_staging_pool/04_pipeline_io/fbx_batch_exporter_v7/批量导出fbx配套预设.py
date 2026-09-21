import maya.cmds as cmds
import maya.mel as mel
import os
import json

# 获取当前 Maya 文件的路径
current_file = cmds.file(query=True, sceneName=True)
current_file_dir = os.path.dirname(current_file) if current_file else None

# 要保存和加载设置的文件名
settings_file = os.path.join(current_file_dir, 'fbx_exporter_settings.json')


def save_settings(*args):
    # 获取 FBX 导出器工具的设置
    fbx_settings = {
        'objects': cmds.textScrollList(myList1, query=True, allItems=True),
        'time_ranges': cmds.textScrollList(myList2, query=True, allItems=True),
        'prefix': cmds.textField(prefixTextField, query=True, text=True),
        'inputConnectionsCheckBox': cmds.checkBox(inputConnectionsCheckBox, query=True, value=True),
        'asciiCheckBox': cmds.checkBox(asciiCheckBox, query=True, value=True),
        'smoothingGroupsCheckBox': cmds.checkBox(smoothingGroupsCheckBox, query=True, value=True),
        'smoothMeshCheckBox': cmds.checkBox(smoothMeshCheckBox, query=True, value=True),
        'referencedAssetsContentCheckBox': cmds.checkBox(referencedAssetsContentCheckBox, query=True, value=True),
        'triangulateCheckBox': cmds.checkBox(triangulateCheckBox, query=True, value=True),
        'skinsCheckBox': cmds.checkBox(skinsCheckBox, query=True, value=True),
        'camerasCheckBox': cmds.checkBox(camerasCheckBox, query=True, value=True),
        'embeddedTexturesCheckBox': cmds.checkBox(embeddedTexturesCheckBox, query=True, value=True),
        'upAxisMenu': cmds.optionMenu(upAxisMenu, query=True, value=True),
        'fileVersionMenu': cmds.optionMenu(fileVersionMenu, query=True, value=True)
    }

    # 将设置保存到文件中
    with open(settings_file, 'w') as file:
        json.dump(fbx_settings, file)

    print("设置已保存到文件: {}".format(settings_file))


def load_settings(*args):
    # 检查设置文件是否存在
    if not os.path.isfile(settings_file):
        print("找不到设置文件: {}".format(settings_file))
        return

    # 从文件中加载设置
    with open(settings_file, 'r') as file:
        fbx_settings = json.load(file)

    # 将设置应用于 FBX 导出器工具
    cmds.textScrollList(myList1, edit=True, removeAll=True, append=fbx_settings.get('objects', []))
    cmds.textScrollList(myList2, edit=True, removeAll=True, append=fbx_settings.get('time_ranges', []))
    cmds.textField(prefixTextField, edit=True, text=fbx_settings.get('prefix', ''))
    cmds.checkBox(inputConnectionsCheckBox, edit=True, value=fbx_settings.get('inputConnectionsCheckBox', False))
    cmds.checkBox(asciiCheckBox, edit=True, value=fbx_settings.get('asciiCheckBox', False))
    cmds.checkBox(smoothingGroupsCheckBox, edit=True, value=fbx_settings.get('smoothingGroupsCheckBox', False))
    cmds.checkBox(smoothMeshCheckBox, edit=True, value=fbx_settings.get('smoothMeshCheckBox', False))
    cmds.checkBox(referencedAssetsContentCheckBox, edit=True, value=fbx_settings.get('referencedAssetsContentCheckBox', False))
    cmds.checkBox(triangulateCheckBox, edit=True, value=fbx_settings.get('triangulateCheckBox', False))
    cmds.checkBox(skinsCheckBox, edit=True, value=fbx_settings.get('skinsCheckBox', False))
    cmds.checkBox(camerasCheckBox, edit=True, value=fbx_settings.get('camerasCheckBox', False))
    cmds.checkBox(embeddedTexturesCheckBox, edit=True, value=fbx_settings.get('embeddedTexturesCheckBox', False))
    cmds.optionMenu(upAxisMenu, edit=True, value=fbx_settings.get('upAxisMenu', 'Y'))
    cmds.optionMenu(fileVersionMenu, edit=True, value=fbx_settings.get('fileVersionMenu', 'FBX202000'))

    print("设置已从文件中加载: {}".format(settings_file))


import maya.cmds as cmds

# 创建工具窗口
window = cmds.window(title="settings manager", widthHeight=(200, 120))
cmds.columnLayout(adjustableColumn=True)
cmds.button(label="save", command=save_settings, height=30 * 1.5)  # 将按钮高度设置为原始高度的1.5倍
cmds.button(label="load", command=load_settings, height=30 * 1.5)  # 将按钮高度设置为原始高度的1.5倍
cmds.setParent('..')
cmds.showWindow(window)

