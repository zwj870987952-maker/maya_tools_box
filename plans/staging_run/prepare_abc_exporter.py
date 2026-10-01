"""Convert complete UI layouts only; unsafe old execution stays archived."""
import ast
from pathlib import Path
from lib2to3.refactor import RefactoringTool,get_fixers_from_package
ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/04_pipeline_io/abc_batch_exporter'
PKG=UNIT/'release_candidate/maya_toolkit/tools/abc_batch_exporter'
refactor=RefactoringTool(get_fixers_from_package('lib2to3.fixes'))


def function(filename,name):
    src=str(refactor.refactor_string((UNIT/filename).read_text(encoding='utf8')+'\n',str(filename)))
    tree=ast.parse(src); node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    for child in ast.walk(node):
        if isinstance(child,ast.keyword) and child.arg in ('c','command') and isinstance(child.value,ast.Constant) and isinstance(child.value.value,str):
            expression=ast.parse(child.value.value,mode='eval').body
            child.value=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='unused')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=expression)
    return ast.unparse(ast.fix_missing_locations(node))


header='''"""Full original two native windows, scoped safe callbacks."""
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
        cm.textScrollList('the_mod_list',edit=True,removeAll=True)
        cm.textScrollList('the_mod_list',edit=True,append=nodes)
    except Exception as exc: cm.warning(str(exc))

def remove_mesh(): cm.textScrollList('the_mod_list',edit=True,removeAll=True)

def ABC_set_path_output():
    selected=cm.fileDialog2(fileFilter='Alembic (*.abc)',fileMode=0,caption='设置输出位置')
    if selected: cm.textField('ABC_thePath_to_out',edit=True,text=selected[0])

def ABC_start():
    options={key:cm.checkBox(control,query=True,value=True) for key,control in
      [('uv_write','if_write_UV'),('world_space','if_world_Space'),('write_uv_sets','if_write_UVset'),
       ('write_face_sets','if_write_Faceset'),('write_visibility','if_write_Visibility'),('strip_namespaces','if_remove_NS')]}
    return report(ABCBatchExporterTool().run(action='export',objects=cm.textScrollList('the_mod_list',query=True,allItems=True) or [],
      output=cm.textField('ABC_thePath_to_out',query=True,text=True),start=cm.intField('the_ST_ABC',query=True,value=True),
      end=cm.intField('the_ET_ABC',query=True,value=True),step=cm.floatField('the_EVA_every',query=True,value=True),options=options))

def addnew_Shade(): return report(ABCBatchExporterTool().run(action='materials'))

def browse_folder(*args):
    selected=cmds.fileDialog2(fileMode=3,caption='Select Folder')
    if selected: cmds.textField('folderPathTextField',edit=True,text=selected[0])

def execute_script(*args):
    folder=cmds.textField('folderPathTextField',query=True,text=True)
    return report(ABCBatchExporterTool().run(action='batch',folder=folder,output_dir=folder,
      options={'write_color_sets':True}))

def show_ui():
    window_TX(); create_ui()
'''
content=header+'\n'+function('ABC导出_v3.py','window_TX')+'\n'+function('ABC导出_选择集批量UI版.py','create_ui')+'\n'
names=['wit','the_mod_list','the_ST_ABC','the_ET_ABC','the_EVA_every','if_write_UV','if_world_Space','if_write_Visibility','if_write_UVset','if_remove_NS','if_write_Faceset','ABC_thePath_to_out','abcExportWindow','folderPathTextField']
for name in sorted(names,key=len,reverse=True):
    # Exact quoted tokens avoid corrupting prefix-sharing controls/words.
    for marker in ("'",'"'): content=content.replace(marker+name+marker,marker+'mtbABC_'+name+marker)
content=content.replace("cmds.button(label='Export ABC', command=execute_script)","cmds.text(label='每个场景 abc_export 选择集，独立mayapy，输出同文件夹且不覆盖')\n    cmds.button(label='Export ABC', command=execute_script)")
(PKG/'ui.py').write_text(content,encoding='utf8',newline='\n')
print('Both complete original UI layouts prepared with Python 3 callbacks')
