"""Retain V7 native form and controls, route all writing operations to API."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/04_pipeline_io/fbx_batch_exporter_v7'
PKG=UNIT/'release_candidate/maya_toolkit/tools/fbx_batch_exporter_v7'
tree=ast.parse((UNIT/'fbx_export_CHS_v7.py').read_text(encoding='utf8'))
retained=[]; body=[]; start=False
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name not in ('execute_script','open_settings_window','bake_selected_hierarchy','export_fbx'): retained.append(ast.unparse(node))
    elif isinstance(node,ast.If) and not start: start=True; body.append(node)
    elif start: body.append(node)
names=sorted({n.id for node in body for n in ast.walk(node) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store)})
main='def show_ui():\n    if cmds.about(batch=True): raise RuntimeError(\'Interactive Maya required\')\n    global '+','.join(names)+'\n'+ '\n'.join('    '+line for line in '\n'.join(ast.unparse(n) for n in body).splitlines())+'\n    return window\n'
header='''"""Complete original V7 native form and separate settings manager."""
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
'''
code=header+'\n\n'+'\n\n'.join(retained)+'\n\n'+main
code=code.replace('cmds.ls(selection=True)','cmds.ls(selection=True,long=True)').replace('start_frame = int(range[0])','start_frame = float(range[0])').replace('end_frame = int(range[1])','end_frame = float(range[1])').replace("label='包括子对象'","label='嵌入贴图（可能增大FBX文件）'")
code=code.replace('cmds.textScrollList(myList1, edit=True, removeIndexedItem=selected_index)','cmds.textScrollList(myList1, edit=True, removeIndexedItem=selected_index)\n        update_counter1()')
code=code.replace('cmds.textScrollList(myList2, edit=True, removeIndexedItem=selected_index)','cmds.textScrollList(myList2, edit=True, removeIndexedItem=selected_index)\n        update_counter2()')
ast.parse(code)
(PKG/'ui.py').write_text('\n'.join(line.rstrip() for line in code.splitlines())+'\n',encoding='utf8',newline='\n')
print('Complete V7 form, grouped rows, all FBX flags/bake/SSC and settings manager prepared')
