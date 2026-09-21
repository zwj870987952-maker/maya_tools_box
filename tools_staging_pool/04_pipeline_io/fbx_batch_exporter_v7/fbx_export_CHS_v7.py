#相比于V4，内嵌了保存配置功能，修复了烘培功能#######
#增加取消分段比例补偿功能#######
#增加了烘培物体功能，删除时间轴适配每个物体的时长调整后输出，因为没有作用还增加了输出时间##########
#优化导出设置，修复导出动画设置无法起作用bug；添加时间轴适配每个物体的时长调整后输出，对于资产导入到UE有作用；修复##########

import maya.cmds as cmds
import maya.mel as mel
import os

def add_to_list1(*args):
    selected = cmds.ls(selection=True)
    if selected:
        cmds.textScrollList(myList1, edit=True, append=" ".join(selected))
        update_counter1()

def add_to_list2(*args):
    playback_slider = mel.eval("$tmpVar=$gPlayBackSlider")
    if cmds.timeControl(playback_slider, query=True, rangeVisible=True):
        range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
        start_frame = int(range[0])
        end_frame = int(range[1])
        cmds.textScrollList(myList2, edit=True, append="{},{}".format(start_frame, end_frame-1))
        update_counter2()

def update_counter1():
    item_count = cmds.textScrollList(myList1, query=True, numberOfItems=True)
    cmds.text(myList1_count, edit=True, label="Count: {}".format(item_count))

def update_counter2():
    item_count = cmds.textScrollList(myList2, query=True, numberOfItems=True)
    cmds.text(myList2_count, edit=True, label="Count: {}".format(item_count))

def remove_selected_from_list1(*args):
    selected_indices = cmds.textScrollList(myList1, query=True, selectIndexedItem=True)
    if selected_indices:
# 只删除第一个选中的索引
        selected_index = selected_indices[0]  
        cmds.textScrollList(myList1, edit=True, removeIndexedItem=selected_index)

def remove_selected_from_list2(*args):
    selected_indices = cmds.textScrollList(myList2, query=True, selectIndexedItem=True)
    if selected_indices:
 # 只删除第一个选中的索引
        selected_index = selected_indices[0] 
        cmds.textScrollList(myList2, edit=True, removeIndexedItem=selected_index)

######dummy_arg=None可以防止按钮点击传递参数给函数，函数不识别造成代码失效######
def execute_script(dummy_arg=None):
    """
    执行设置骨骼 segmentScaleCompensate 属性的脚本
    """
    def set_segment_scale_compensate(selection):
        """
        设置骨骼的 segmentScaleCompensate 属性为 0。

        :param selection: 需要设置属性的骨骼列表
        """
        for selected_joint in selection:
            cmds.setAttr(selected_joint + ".segmentScaleCompensate", 0)

    # 获取当前选择的骨骼列表
    selection = cmds.ls(selection=True, type='joint')

    # 检查是否选中了一个或多个骨骼
    if selection:
        set_segment_scale_compensate(selection)
    else:
        # 如果没有选中骨骼，则显示警告对话框
        cmds.warning("Please select at least one joint.")



# 保存设置       
def open_settings_window(*args):
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
            "export_animation": cmds.checkBox(exportAnimationCheckBox, query=True, value=True),
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
        # 设置“导出动画”复选框的状态
        cmds.checkBox(exportAnimationCheckBox, edit=True, value=fbx_settings.get("export_animation", False))
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


#########烘培选择的物体##################
def bake_selected_hierarchy(dummy_arg=None):
    # 获取选择的物体
    selected_objects = cmds.ls(selection=True)

    # 获取时间轴的起始和结束时间
    start_frame = int(cmds.playbackOptions(q=True, minTime=True))
    end_frame = int(cmds.playbackOptions(q=True, maxTime=True))

    # 遍历每个选择的物体以及它们的子层级
    for obj in selected_objects:
        # 选择当前物体及其子层级
        cmds.select(obj, hierarchy=True)

        # 烘焙关键帧
        cmds.bakeResults(
            simulation=True,
            t=(start_frame, end_frame),
            sampleBy=1,
            oversamplingRate=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            removeBakedAttributeFromLayer=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=False,
            controlPoints=False,
            shape=True,
        )

    # 取消选择所有物体
    cmds.select(clear=True)


def export_fbx(*args):
    # 检查导出动画复选框的状态
    export_animation = cmds.checkBox(exportAnimationCheckBox, query=True, value=True)

    # 根据复选框的状态设置 FBX 属性
    if export_animation:
        mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v true')
    else:
        mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v false')

    # 保存当前动画的起始时间和结束时间
    original_start_time = cmds.playbackOptions(query=True, animationStartTime=True)
    original_end_time = cmds.playbackOptions(query=True, animationEndTime=True)

    # 获取前缀文本框中的内容
    prefix = cmds.textField(prefixTextField, query=True, text=True)  
    objects = cmds.textScrollList(myList1, query=True, allItems=True)
    time_ranges = cmds.textScrollList(myList2, query=True, allItems=True)
    if objects and time_ranges:
        scene_name = cmds.file(query=True, sceneName=True)
        directory = os.path.dirname(scene_name)
        for i in range(min(len(objects), len(time_ranges))):
            obj = objects[i].split()

            start_frame, end_frame = map(int, map(float, time_ranges[i].split(",")))
            # 设置动画的起始时间和结束时间为当前循环迭代的值
            cmds.playbackOptions(animationStartTime=start_frame, animationEndTime=end_frame)
            cmds.playbackOptions(minTime=start_frame, maxTime=end_frame)

            namespace_index = obj[0].find(":")
            if namespace_index != -1:
                filename = "{}_{}_{}.fbx".format(obj[0][:namespace_index].replace(":", "_"), start_frame,
                                                 end_frame)
            else:
                filename = "{}_{}.fbx".format(obj[0], i)
                # 添加前缀到文件名
            if prefix:
                filename = prefix + "_" + filename
            filepath = os.path.join(directory, filename)

            # Check if the file already exists and add a number to the filename if it does
            counter = 1
            while os.path.exists(filepath):
                if namespace_index != -1:
                    filename = "{}_{}_{}_{}.fbx".format(obj[0][:namespace_index].replace(":", "_"), start_frame,
                                                        end_frame, counter)
                else:
                    filename = "{}_{}_{}.fbx".format(obj[0], i, counter)
                filepath = os.path.join(directory, filename)
                counter += 1
            cmds.select(obj, hierarchy=True)
            mel.eval('FBXExportBakeComplexAnimation -v true')
            mel.eval('FBXExportBakeComplexStep -v 1')
            mel.eval('FBXExportBakeComplexStart -v {}'.format(start_frame))
            mel.eval('FBXExportBakeComplexEnd -v {}'.format(end_frame))
            
            mel.eval('FBXExportInputConnections -v {}'.format(str(cmds.checkBox(inputConnectionsCheckBox,
                                                                                query=True,
                                                                                value=True)).lower()))
            mel.eval('FBXExportInAscii -v {}'.format(str(cmds.checkBox(asciiCheckBox,
                                                                       query=True,
                                                                       value=True)).lower()))
            mel.eval('FBXExportSmoothingGroups -v {}'.format(str(cmds.checkBox(smoothingGroupsCheckBox,
                                                                               query=True,
                                                                               value=True)).lower()))
            mel.eval('FBXExportSmoothMesh -v {}'.format(str(cmds.checkBox(smoothMeshCheckBox,
                                                                          query=True,
                                                                          value=True)).lower()))
            mel.eval('FBXExportReferencedAssetsContent -v {}'.format(str(cmds.checkBox(referencedAssetsContentCheckBox,
                                                                                         query=True,
                                                                                         value=True)).lower()))
            mel.eval('FBXExportTriangulate -v {}'.format(str(cmds.checkBox(triangulateCheckBox,
                                                                           query=True,
                                                                           value=True)).lower()))
            mel.eval('FBXExportSkins -v {}'.format(str(cmds.checkBox(skinsCheckBox,
                                                                     query=True,
                                                                     value=True)).lower()))
            mel.eval('FBXExportCameras -v {}'.format(str(cmds.checkBox(camerasCheckBox,
                                                                       query=True,
                                                                       value=True)).lower()))
            mel.eval('FBXExportEmbeddedTextures -v {}'.format(str(cmds.checkBox(embeddedTexturesCheckBox,
                                                                                query=True,
                                                                                value=True)).lower()))
            mel.eval('FBXExportUpAxis {}'.format(cmds.optionMenu(upAxisMenu, query=True, value=True)))
            mel.eval('FBXExportFileVersion "{}"'.format(cmds.optionMenu(fileVersionMenu, query=True, value=True)))
            cmds.file(filepath, force=True, options="v=0;", type="FBX export", preserveReferences=True,
                      exportSelected=True)
                      
            # 循环结束后，还原动画的起始时间和结束时间为之前保存的值
            cmds.playbackOptions(animationStartTime=original_start_time, animationEndTime=original_end_time)
            cmds.playbackOptions(minTime=original_start_time, maxTime=original_end_time)


if cmds.window("fbx_exporter", exists=True):
    cmds.deleteUI("fbx_exporter")

window = cmds.window("fbx_exporter", title="FBX导出器")
form = cmds.formLayout()
addButton1 = cmds.button(label="添加选择物体", command=add_to_list1)
removeButton1 = cmds.button(label="移除所选物体", command=remove_selected_from_list1, backgroundColor=[1, 0, 0], enableBackground=True)
myList1 = cmds.textScrollList(allowMultiSelection=True, height=200)
addButton2 = cmds.button(label="添加时间轴范围", command=add_to_list2)
removeButton2 = cmds.button(label="移除时间轴范围", command=remove_selected_from_list2, backgroundColor=[1, 0, 0], enableBackground=True)
myList2 = cmds.textScrollList(allowMultiSelection=True, height=200)
# 在文本框上方添加计数器
myList1_count = cmds.text(label="Items: 0")
myList2_count = cmds.text(label="Items: 0")
# 添加前缀文本框
prefixTextField = cmds.textField("prefixTextField", placeholderText="添加前缀",width=200, height=30)

exportButton = cmds.button(label="Export FBX", command=export_fbx, height=50,width=200, backgroundColor=[0, 0.8, 0.5])
# 新建保存配置按钮
create_settingsButton= cmds.button(label="保存配置", command=open_settings_window, height=30,width=100, backgroundColor=[1, 1, 0])
# 新建去除分段比例补偿按钮
segmentScaleCompensateButton= cmds.button(label="取消分段比例补偿", command=execute_script, height=30,width=100, backgroundColor=[0, 0.5, 1])
# 新建烘培所有物体按钮
bake_selected_hiButton= cmds.button(label="烘培物体", command=bake_selected_hierarchy, height=30,width=100, backgroundColor=[0, 0.8, 1])


# 在界面定义部分，添加一个新的复选框
exportAnimationCheckBox = cmds.checkBox(
    label="导出动画", 
    value=True  # 默认打开
)
smoothingGroupsCheckBox = cmds.checkBox(label="导出平滑组", value=True)
smoothMeshCheckBox = cmds.checkBox(label="导出平滑网格", value=True)
referencedAssetsContentCheckBox = cmds.checkBox(label="引用的资源内容", value=True)
triangulateCheckBox = cmds.checkBox(label="三角剖分")

skinsCheckBox = cmds.checkBox(label="导出变形模型", value=True)

camerasCheckBox = cmds.checkBox(label="导出摄像机", value=True)

embeddedTexturesCheckBox = cmds.checkBox(label="包括子对象", value=True)
inputConnectionsCheckBox = cmds.checkBox(label="导出输入连接")

asciiCheckBox = cmds.checkBox(label="以ASCII格式导出", value=True)
upAxisMenu = cmds.optionMenu(label="上方轴向")
cmds.menuItem(label="Y")
cmds.menuItem(label="Z")
fileVersionMenu = cmds.optionMenu(label="FBX文件格式")
cmds.menuItem(label="FBX202000")
cmds.menuItem(label="FBX201900")
cmds.menuItem(label="FBX201800")
cmds.menuItem(label="FBX201600")
cmds.menuItem(label="FBX201400")
cmds.menuItem(label="FBX201300")
cmds.menuItem(label="FBX201200")
cmds.menuItem(label="FBX201100")
cmds.menuItem(label="FBX201000")
cmds.menuItem(label="FBX200900")

cmds.formLayout(form, edit=True,
                attachForm=[
                    (addButton1, 'top', 5), (addButton1, 'left', 5),
                    (removeButton1, 'left', 5), (myList1_count, 'left', 5),
                    (myList1, 'left', 5),
                    (addButton2, 'top', 5), (addButton2, 'right', 5),
                    (removeButton2, 'right', 5), (myList2_count, 'right', 20),
                    (myList2, 'right', 5),
                    (prefixTextField, 'left', 5),
                    (inputConnectionsCheckBox, 'left', 5),
                    (asciiCheckBox, 'left', 5),
                    (smoothingGroupsCheckBox, 'left', 5),
                    (smoothMeshCheckBox, 'left', 5),
                    (referencedAssetsContentCheckBox, 'left', 5),
                    (triangulateCheckBox, 'left', 5),
                    (skinsCheckBox, 'left', 5),
                    (camerasCheckBox, 'left', 5),
                    (embeddedTexturesCheckBox, 'left', 5),
                    (exportAnimationCheckBox, 'left', 5),  # 添加到布局中
                    (upAxisMenu, 'left', 5),
                    (fileVersionMenu, 'left', 5),
                    (create_settingsButton, 'left', 5),
                    (segmentScaleCompensateButton, 'left', 5),
                    (bake_selected_hiButton, 'left', 5),
                    (exportButton, 'bottom', 5)
                ],
                attachControl=[
                    (removeButton1, 'top', 5, addButton1),
                    (myList1_count, 'top', 5, removeButton1),
                    (myList1, 'top', 5, myList1_count),
                    (removeButton2, 'top', 5, addButton2),
                    (myList2_count, 'top', 5, removeButton2),
                    (myList2, 'top', 5, myList2_count),
                    (prefixTextField, 'top', 5, myList1),
                    (inputConnectionsCheckBox, 'top', 5, prefixTextField),
                    (asciiCheckBox, 'top', 5, inputConnectionsCheckBox),
                    (smoothingGroupsCheckBox, 'top', 5, asciiCheckBox),
                    (smoothMeshCheckBox, 'top', 5, smoothingGroupsCheckBox),
                    (referencedAssetsContentCheckBox, 'top', 5, smoothMeshCheckBox),
                    (triangulateCheckBox, 'top', 5, referencedAssetsContentCheckBox),
                    (skinsCheckBox, 'top', 5, triangulateCheckBox),
                    (camerasCheckBox, 'top', 5, skinsCheckBox),
                    (embeddedTexturesCheckBox, 'top', 5, camerasCheckBox),
                    (exportAnimationCheckBox, 'top', 5, embeddedTexturesCheckBox),  # 在此处添加控制
                    (upAxisMenu, 'top', 5, exportAnimationCheckBox),  # 将接下来的控件放在复选框下方
                    (fileVersionMenu, 'top', 5, upAxisMenu),
                    (create_settingsButton, 'top', 5, fileVersionMenu),
                    (segmentScaleCompensateButton, 'top', 5, fileVersionMenu),
                    (segmentScaleCompensateButton, 'left', 5, create_settingsButton),
                    (bake_selected_hiButton, 'top', 5, fileVersionMenu),
                    (bake_selected_hiButton, 'left', 5, segmentScaleCompensateButton)
                ],
                attachPosition=[
                    (addButton1, 'right', 5, 50), (addButton2, 'left', 5, 50),
                    (myList1, 'right', 5, 50), (myList2, 'left', 5, 50)
                ],
                attachNone=[(exportButton, 'top'), (exportButton, 'left'), (exportButton, 'right')]
)
                


##########水印
watermark_label = cmds.text(label="<font size='4'>by ZWJ</font>", align="right")
cmds.formLayout(form, edit=True, attachForm=[(watermark_label, 'bottom', 5), (watermark_label, 'right', 5)])


cmds.showWindow(window)