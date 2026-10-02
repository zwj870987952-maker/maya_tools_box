"""Complete original V7 native form and separate settings manager."""
import os
from pathlib import Path
from maya import cmds,mel
from .tool import FbxBatchExporterV7Tool,configuration
tool=FbxBatchExporterV7Tool()
CHECKS={'input_connections':'inputConnectionsCheckBox','ascii':'asciiCheckBox','smoothing_groups':'smoothingGroupsCheckBox','smooth_mesh':'smoothMeshCheckBox','referenced_assets':'referencedAssetsContentCheckBox','triangulate':'triangulateCheckBox','skins':'skinsCheckBox','cameras':'camerasCheckBox','embedded_textures':'embeddedTexturesCheckBox','export_animation':'exportAnimationCheckBox'}
def ui_config():
    objects=cmds.textScrollList(myList1,query=True,allItems=True) or []
    ranges=cmds.textScrollList(myList2,query=True,allItems=True) or []
    if len(objects)!=len(ranges): raise ValueError('物体组与时间范围数量必须相同，不能静默截断。')
    jobs=[]
    for objects,frames in zip(objects,ranges):
        parts=frames.split(',')
        if len(parts)!=2: raise ValueError('时间范围需要start,end')
        jobs.append({'objects':objects.split(),'start':float(parts[0]),'end':float(parts[1])})
    opts={key:cmds.checkBox(globals()[name],query=True,value=True) for key,name in CHECKS.items()}
    opts.update(up_axis=cmds.optionMenu(upAxisMenu,query=True,value=True),file_version=cmds.optionMenu(fileVersionMenu,query=True,value=True))
    return configuration({'version':1,'jobs':jobs,'prefix':cmds.textField(prefixTextField,query=True,text=True),'options':opts})
def report(result):
    print(result.to_dict())
    if not result.success: cmds.warning(result.message)
    return result
def export_fbx(*args):
    try:
        config=ui_config()
        source=cmds.file(query=True,sceneName=True)
        directory=os.path.dirname(source) if source else None
        if not directory:
            chosen=cmds.fileDialog2(fileMode=3,caption='选择FBX输出目录')
            if not chosen: return
            directory=chosen[0]
        return report(tool.run(action='export',jobs=config['jobs'],prefix=config['prefix'],options=config['options'],output_dir=directory))
    except Exception as exc: cmds.warning(str(exc))
def execute_script(*args): return report(tool.run(action='disable_ssc',objects=cmds.ls(selection=True,long=True,type='joint') or []))
def bake_selected_hierarchy(*args):
    return report(tool.run(action='bake',objects=cmds.ls(selection=True,long=True) or [],start=cmds.playbackOptions(query=True,minTime=True),end=cmds.playbackOptions(query=True,maxTime=True)))
def save_settings(*args):
    chosen=cmds.fileDialog2(fileMode=0,fileFilter='JSON (*.json)',caption='保存到全新配置JSON（已有文件拒绝）')
    if not chosen: return
    try: return report(tool.run(action='save_settings',settings_path=str(Path(chosen[0]).resolve()),configuration=ui_config()))
    except Exception as exc: cmds.warning(str(exc))
def load_settings(*args):
    chosen=cmds.fileDialog2(fileMode=1,fileFilter='JSON (*.json)',caption='加载配置JSON')
    if not chosen: return
    result=report(tool.run(action='load_settings',settings_path=str(Path(chosen[0]).resolve())))
    if not result.success: return
    config=result.data['configuration']
    cmds.textScrollList(myList1,edit=True,removeAll=True,append=[' '.join(r['objects']) for r in config['jobs']])
    cmds.textScrollList(myList2,edit=True,removeAll=True,append=[str(r['start'])+','+str(r['end']) for r in config['jobs']])
    cmds.textField(prefixTextField,edit=True,text=config['prefix'])
    for key,name in CHECKS.items(): cmds.checkBox(globals()[name],edit=True,value=config['options'][key])
    cmds.optionMenu(upAxisMenu,edit=True,value=config['options']['up_axis']); cmds.optionMenu(fileVersionMenu,edit=True,value=config['options']['file_version'])
    update_counter1(); update_counter2()
def open_settings_window(*args):
    window=cmds.window(title='settings manager',widthHeight=(200,120)); cmds.columnLayout(adjustableColumn=True)
    cmds.button(label='save',command=save_settings,height=45); cmds.button(label='load',command=load_settings,height=45); cmds.setParent('..'); cmds.showWindow(window); return window


def add_to_list1(*args):
    selected = cmds.ls(selection=True,long=True)
    if selected:
        cmds.textScrollList(myList1, edit=True, append=' '.join(selected))
        update_counter1()

def add_to_list2(*args):
    playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
    if cmds.timeControl(playback_slider, query=True, rangeVisible=True):
        range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
        start_frame = float(range[0])
        end_frame = float(range[1])
        cmds.textScrollList(myList2, edit=True, append='{},{}'.format(start_frame, end_frame - 1))
        update_counter2()

def update_counter1():
    item_count = cmds.textScrollList(myList1, query=True, numberOfItems=True)
    cmds.text(myList1_count, edit=True, label='Count: {}'.format(item_count))

def update_counter2():
    item_count = cmds.textScrollList(myList2, query=True, numberOfItems=True)
    cmds.text(myList2_count, edit=True, label='Count: {}'.format(item_count))

def remove_selected_from_list1(*args):
    selected_indices = cmds.textScrollList(myList1, query=True, selectIndexedItem=True)
    if selected_indices:
        selected_index = selected_indices[0]
        cmds.textScrollList(myList1, edit=True, removeIndexedItem=selected_index)
        update_counter1()

def remove_selected_from_list2(*args):
    selected_indices = cmds.textScrollList(myList2, query=True, selectIndexedItem=True)
    if selected_indices:
        selected_index = selected_indices[0]
        cmds.textScrollList(myList2, edit=True, removeIndexedItem=selected_index)
        update_counter2()

def show_ui():
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    global addButton1,addButton2,asciiCheckBox,bake_selected_hiButton,camerasCheckBox,create_settingsButton,embeddedTexturesCheckBox,exportAnimationCheckBox,exportButton,fileVersionMenu,form,inputConnectionsCheckBox,myList1,myList1_count,myList2,myList2_count,prefixTextField,referencedAssetsContentCheckBox,removeButton1,removeButton2,segmentScaleCompensateButton,skinsCheckBox,smoothMeshCheckBox,smoothingGroupsCheckBox,triangulateCheckBox,upAxisMenu,watermark_label,window
    if cmds.window('fbx_exporter', exists=True):
        cmds.deleteUI('fbx_exporter')
    window = cmds.window('fbx_exporter', title='FBX导出器')
    form = cmds.formLayout()
    addButton1 = cmds.button(label='添加选择物体', command=add_to_list1)
    removeButton1 = cmds.button(label='移除所选物体', command=remove_selected_from_list1, backgroundColor=[1, 0, 0], enableBackground=True)
    myList1 = cmds.textScrollList(allowMultiSelection=True, height=200)
    addButton2 = cmds.button(label='添加时间轴范围', command=add_to_list2)
    removeButton2 = cmds.button(label='移除时间轴范围', command=remove_selected_from_list2, backgroundColor=[1, 0, 0], enableBackground=True)
    myList2 = cmds.textScrollList(allowMultiSelection=True, height=200)
    myList1_count = cmds.text(label='Items: 0')
    myList2_count = cmds.text(label='Items: 0')
    prefixTextField = cmds.textField('prefixTextField', placeholderText='添加前缀', width=200, height=30)
    exportButton = cmds.button(label='Export FBX', command=export_fbx, height=50, width=200, backgroundColor=[0, 0.8, 0.5])
    create_settingsButton = cmds.button(label='保存配置', command=open_settings_window, height=30, width=100, backgroundColor=[1, 1, 0])
    segmentScaleCompensateButton = cmds.button(label='取消分段比例补偿', command=execute_script, height=30, width=100, backgroundColor=[0, 0.5, 1])
    bake_selected_hiButton = cmds.button(label='烘培物体', command=bake_selected_hierarchy, height=30, width=100, backgroundColor=[0, 0.8, 1])
    exportAnimationCheckBox = cmds.checkBox(label='导出动画', value=True)
    smoothingGroupsCheckBox = cmds.checkBox(label='导出平滑组', value=True)
    smoothMeshCheckBox = cmds.checkBox(label='导出平滑网格', value=True)
    referencedAssetsContentCheckBox = cmds.checkBox(label='引用的资源内容', value=True)
    triangulateCheckBox = cmds.checkBox(label='三角剖分')
    skinsCheckBox = cmds.checkBox(label='导出变形模型', value=True)
    camerasCheckBox = cmds.checkBox(label='导出摄像机', value=True)
    embeddedTexturesCheckBox = cmds.checkBox(label='嵌入贴图（可能增大FBX文件）', value=True)
    inputConnectionsCheckBox = cmds.checkBox(label='导出输入连接')
    asciiCheckBox = cmds.checkBox(label='以ASCII格式导出', value=True)
    upAxisMenu = cmds.optionMenu(label='上方轴向')
    cmds.menuItem(label='Y')
    cmds.menuItem(label='Z')
    fileVersionMenu = cmds.optionMenu(label='FBX文件格式')
    cmds.menuItem(label='FBX202000')
    cmds.menuItem(label='FBX201900')
    cmds.menuItem(label='FBX201800')
    cmds.menuItem(label='FBX201600')
    cmds.menuItem(label='FBX201400')
    cmds.menuItem(label='FBX201300')
    cmds.menuItem(label='FBX201200')
    cmds.menuItem(label='FBX201100')
    cmds.menuItem(label='FBX201000')
    cmds.menuItem(label='FBX200900')
    cmds.formLayout(form, edit=True, attachForm=[(addButton1, 'top', 5), (addButton1, 'left', 5), (removeButton1, 'left', 5), (myList1_count, 'left', 5), (myList1, 'left', 5), (addButton2, 'top', 5), (addButton2, 'right', 5), (removeButton2, 'right', 5), (myList2_count, 'right', 20), (myList2, 'right', 5), (prefixTextField, 'left', 5), (inputConnectionsCheckBox, 'left', 5), (asciiCheckBox, 'left', 5), (smoothingGroupsCheckBox, 'left', 5), (smoothMeshCheckBox, 'left', 5), (referencedAssetsContentCheckBox, 'left', 5), (triangulateCheckBox, 'left', 5), (skinsCheckBox, 'left', 5), (camerasCheckBox, 'left', 5), (embeddedTexturesCheckBox, 'left', 5), (exportAnimationCheckBox, 'left', 5), (upAxisMenu, 'left', 5), (fileVersionMenu, 'left', 5), (create_settingsButton, 'left', 5), (segmentScaleCompensateButton, 'left', 5), (bake_selected_hiButton, 'left', 5), (exportButton, 'bottom', 5)], attachControl=[(removeButton1, 'top', 5, addButton1), (myList1_count, 'top', 5, removeButton1), (myList1, 'top', 5, myList1_count), (removeButton2, 'top', 5, addButton2), (myList2_count, 'top', 5, removeButton2), (myList2, 'top', 5, myList2_count), (prefixTextField, 'top', 5, myList1), (inputConnectionsCheckBox, 'top', 5, prefixTextField), (asciiCheckBox, 'top', 5, inputConnectionsCheckBox), (smoothingGroupsCheckBox, 'top', 5, asciiCheckBox), (smoothMeshCheckBox, 'top', 5, smoothingGroupsCheckBox), (referencedAssetsContentCheckBox, 'top', 5, smoothMeshCheckBox), (triangulateCheckBox, 'top', 5, referencedAssetsContentCheckBox), (skinsCheckBox, 'top', 5, triangulateCheckBox), (camerasCheckBox, 'top', 5, skinsCheckBox), (embeddedTexturesCheckBox, 'top', 5, camerasCheckBox), (exportAnimationCheckBox, 'top', 5, embeddedTexturesCheckBox), (upAxisMenu, 'top', 5, exportAnimationCheckBox), (fileVersionMenu, 'top', 5, upAxisMenu), (create_settingsButton, 'top', 5, fileVersionMenu), (segmentScaleCompensateButton, 'top', 5, fileVersionMenu), (segmentScaleCompensateButton, 'left', 5, create_settingsButton), (bake_selected_hiButton, 'top', 5, fileVersionMenu), (bake_selected_hiButton, 'left', 5, segmentScaleCompensateButton)], attachPosition=[(addButton1, 'right', 5, 50), (addButton2, 'left', 5, 50), (myList1, 'right', 5, 50), (myList2, 'left', 5, 50)], attachNone=[(exportButton, 'top'), (exportButton, 'left'), (exportButton, 'right')])
    watermark_label = cmds.text(label="<font size='4'>by ZWJ</font>", align='right')
    cmds.formLayout(form, edit=True, attachForm=[(watermark_label, 'bottom', 5), (watermark_label, 'right', 5)])
    cmds.showWindow(window)
    return window
