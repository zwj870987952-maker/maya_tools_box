"""Full original two native windows, scoped safe callbacks."""
from pathlib import Path
import maya.cmds as cm
cmds=cm
from .tool import ABCBatchExporterTool,roots

def report(result):
    print(result.to_dict())
    if not result.success: cm.warning(result.message)
    return result

def load_mesh():
    try:
        nodes=roots()
        cm.textScrollList('mtbABC_the_mod_list',edit=True,removeAll=True)
        cm.textScrollList('mtbABC_the_mod_list',edit=True,append=nodes)
    except Exception as exc: cm.warning(str(exc))

def remove_mesh(): cm.textScrollList('mtbABC_the_mod_list',edit=True,removeAll=True)

def ABC_set_path_output():
    selected=cm.fileDialog2(fileFilter='Alembic (*.abc)',fileMode=0,caption='设置输出位置')
    if selected: cm.textField('mtbABC_ABC_thePath_to_out',edit=True,text=selected[0])

def ABC_start():
    options={key:cm.checkBox(control,query=True,value=True) for key,control in
      [('uv_write','mtbABC_if_write_UV'),('world_space','mtbABC_if_world_Space'),('write_uv_sets','mtbABC_if_write_UVset'),
       ('write_face_sets','mtbABC_if_write_Faceset'),('write_visibility','mtbABC_if_write_Visibility'),('strip_namespaces','mtbABC_if_remove_NS')]}
    return report(ABCBatchExporterTool().run(action='export',objects=cm.textScrollList('mtbABC_the_mod_list',query=True,allItems=True) or [],
      output=cm.textField('mtbABC_ABC_thePath_to_out',query=True,text=True),start=cm.intField('mtbABC_the_ST_ABC',query=True,value=True),
      end=cm.intField('mtbABC_the_ET_ABC',query=True,value=True),step=cm.floatField('mtbABC_the_EVA_every',query=True,value=True),options=options))

def addnew_Shade(): return report(ABCBatchExporterTool().run(action='materials'))

def browse_folder(*args):
    selected=cmds.fileDialog2(fileMode=3,caption='Select Folder')
    if selected: cmds.textField('mtbABC_folderPathTextField',edit=True,text=selected[0])

def execute_script(*args):
    folder=cmds.textField('mtbABC_folderPathTextField',query=True,text=True)
    return report(ABCBatchExporterTool().run(action='batch',folder=folder,output_dir=folder,
      options={'write_color_sets':True}))

def show_ui():
    window_TX(); create_ui()

def window_TX():
    if cm.window('mtbABC_wit', ex=True):
        cm.deleteUI('mtbABC_wit')
    cm.window('mtbABC_wit', title='ABC导出器', mb=1, widthHeight=(400, 400), sizeable=0)
    pro = 'liulizhan'
    cm.frameLayout(bgc=[0, 0.3, 0.6], label='选择加载需要转化的模型并载入')
    cm.columnLayout()
    cm.rowColumnLayout(numberOfColumns=2, cw=[(1, 200), (2, 185)])
    cm.rowColumnLayout(numberOfColumns=1)
    cm.textScrollList('mtbABC_the_mod_list', w=200, h=220, bgc=(0, 0.3, 0.3))
    cm.setParent('..')
    cm.rowColumnLayout(numberOfColumns=1)
    cm.text(label='ABC导出设置')
    cm.rowColumnLayout(numberOfColumns=3, cw=[(1, 80), (2, 50), (3, 50)])
    cm.text(label='')
    cm.text(label='')
    cm.text(label='')
    cm.text(label='起始/结束')
    get_start_frame = cm.playbackOptions(q=True, min=True)
    get_end_frame = cm.playbackOptions(q=True, max=True)
    cm.intField('mtbABC_the_ST_ABC', v=get_start_frame)
    cm.intField('mtbABC_the_ET_ABC', v=get_end_frame)
    cm.text(label='步长')
    cm.floatField('mtbABC_the_EVA_every', v=1)
    cm.text(label='')
    cm.text(label='')
    cm.text(label='')
    cm.text(label='')
    cm.checkBox('mtbABC_if_write_UV', label='UV 写入', v=1)
    cm.text(label='')
    cm.text(label='')
    cm.checkBox('mtbABC_if_world_Space', label='世界空间', v=1)
    cm.text(label='')
    cm.text(label='')
    cm.checkBox('mtbABC_if_write_Visibility', label='写入可见性', value=True)
    cm.text(label='')
    cm.text(label='')
    cm.checkBox('mtbABC_if_write_UVset', label='写入UV集', value=True)
    cm.text(label='')
    cm.text(label='')
    cm.checkBox('mtbABC_if_remove_NS', label='去除空间名', value=False)
    cm.text(label='')
    cm.text(label='')
    cm.checkBox('mtbABC_if_write_Faceset', label='写入面集', value=True)
    cm.text(label='')
    cm.text(label='')
    cm.text(label='')
    cm.setParent('..')
    cm.rowColumnLayout(numberOfColumns=2, cw=[(1, 90), (2, 90)])
    cm.button(label='载入所选', h=30, c=lambda unused: load_mesh())
    cm.button(label='清空列表', c=lambda unused: remove_mesh())
    cm.setParent('..')
    cm.setParent('..')
    cm.setParent('..')
    cm.setParent('..')
    cm.frameLayout(cll=1, cl=0, bgc=[0, 0.3, 0.6], label='ABC缓存输出')
    cm.rowColumnLayout(numberOfColumns=3, cw=[(1, 90), (2, 230), (3, 60)])
    cm.text(fn='boldLabelFont', label='ABC缓存位置：')
    cm.textField('mtbABC_ABC_thePath_to_out', ed=False)
    cm.button(label='浏览...', c=lambda unused: ABC_set_path_output())
    cm.setParent('..')
    cm.rowColumnLayout(numberOfColumns=4, cw=[(1, 50), (2, 150), (3, 30), (4, 150)])
    cm.text(label='')
    cm.button(label='输出ABC缓存', c=lambda unused: ABC_start())
    cm.text(label='')
    cm.button(label='新建材质', c=lambda unused: addnew_Shade(), bgc=(0, 0.3, 0.3))
    cm.setParent('..')
    cm.showWindow('mtbABC_wit')
def create_ui():
    if cmds.window('mtbABC_abcExportWindow', exists=True):
        cmds.deleteUI('mtbABC_abcExportWindow', window=True)
    cmds.window('mtbABC_abcExportWindow', title='ABC Export Tool', widthHeight=(300, 100))
    cmds.columnLayout(adjustableColumn=True)
    cmds.textField('mtbABC_folderPathTextField', placeholderText='Enter folder path here or browse...')
    cmds.button(label='Browse', command=browse_folder)
    cmds.text(label='每个场景 abc_export 选择集，独立mayapy，输出同文件夹且不覆盖')
    cmds.button(label='Export ABC', command=execute_script)
    cmds.showWindow('mtbABC_abcExportWindow')
