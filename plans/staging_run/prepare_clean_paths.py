"""Preserve original node vocabulary, native UI and proven reference helpers."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/04_pipeline_io/clean_invalid_paths'
PKG=UNIT/'release_candidate/maya_toolkit/tools/clean_invalid_paths'
source=ROOT/'tools_staging_pool/04_pipeline_io/batch_importer_v3/release_candidate/maya_toolkit/tools/batch_importer_v3/tool.py'
tree=ast.parse(source.read_text(encoding='utf8'))
helpers=[ast.unparse(n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('file_hash','references','create_reference')]
(PKG/'reference_ops.py').write_text('"""Self-contained eligible-reference helpers shared in behavior with batch importer."""\nimport hashlib\nfrom pathlib import Path\n'+ '\n\n'.join(helpers)+'\n',encoding='utf8',newline='\n')
tree=ast.parse((UNIT/'clean_invalid_paths.py').read_text(encoding='utf8'))
nodes=[]
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ('show_invalid_path_nodes','create_ui'):
        # Replace command strings with callables; they no longer rely on globals
        # injected into Maya Script Editor, nor delete a cached name blindly.
        if node.name=='create_ui': node.body.append(ast.Return(value=ast.Name(id='window',ctx=ast.Load())))
        nodes.append(node)
code='''"""Complete original native two-window inspection UI; explicit policy and deletion."""
from functools import partial
from maya import cmds
from .tool import CleanInvalidPathsTool,scan,normalize,reasons,direct_paths,get_file_nodes
tool=CleanInvalidPathsTool()
policy='ascii'
allow_reference=False
def is_path_valid(path): return not reasons(path,policy)
def get_path_from_node(node):
    rows=direct_paths(node); return rows[0][1] if rows else None
def find_invalid_path_nodes():
    return {r['node']:r['path'] for r in scan(normalize({'policy':policy}))['issues']}
def select_nodes(nodes,*args):
    valid=[n for n in nodes if cmds.objExists(n)]
    if valid: cmds.select(valid,replace=True)
def remove_invalid_path_nodes(nodes_to_remove=None,confirm=True,*args):
    params=dict(action='delete',nodes=nodes_to_remove,policy=policy,allow_reference_removal=allow_reference)
    preview=tool.run(dry_run=True,**params)
    if not preview.success: cmds.warning(preview.message); return []
    data=preview.data
    if not data['issues']: return []
    message='实际删除路径所有者，不删除其材质容器。涉及 {} 个节点及 {} 份完整引用；只改场景，不删除磁盘文件。'.format(len(data['delete_nodes']),len(data['references']))
    if confirm and cmds.confirmDialog(title='确认删除',message=message,button=['是','否'],defaultButton='否',cancelButton='否',dismissString='否')!='是': return []
    result=tool.run(**params)
    if not result.success: cmds.warning(result.message); return []
    return [r['node'] for r in data['delete_nodes']]+[r['reference_node'] for r in data['references']]
def refresh(*args): return show_invalid_path_nodes()
def delete_all(*args):
    result=remove_invalid_path_nodes(confirm=True)
    if cmds.window('invalidPathsWindow',exists=True): cmds.deleteUI('invalidPathsWindow')
    return result
def set_policy(value,*args):
    global policy
    policy={'ASCII兼容策略':'ascii','仅中日韩汉字策略':'cjk','仅Unicode替换字符':'replacement'}[value]
def set_reference(value,*args):
    global allow_reference
    allow_reference=bool(value)
'''+ '\n\n'.join(ast.unparse(n) for n in nodes)
code=code.replace("command=f'import maya.cmds as cmds; cmds.select(\"{node}\", replace=True)'","command=partial(select_nodes,[node])")
code=code.replace("command=f'import maya.cmds as cmds; cmds.delete(\"{node}\")'","command=partial(remove_invalid_path_nodes,[cmds.ls(node,uuid=True)[0]],True)")
code=code.replace("command='import maya.cmds as cmds; cmds.deleteUI(\"invalidPathsWindow\"); show_invalid_path_nodes()'","command=refresh")
code=code.replace("command=f'import maya.cmds as cmds; cmds.select({list(invalid_nodes.keys())}, replace=True)'","command=partial(select_nodes,list(invalid_nodes))")
code=code.replace("command='import maya.cmds as cmds; remove_invalid_path_nodes(confirm=True); cmds.deleteUI(\"invalidPathsWindow\")'","command=delete_all")
code=code.replace("command='show_invalid_path_nodes()'","command=refresh").replace("command='remove_invalid_path_nodes(confirm=True)'","command=partial(remove_invalid_path_nodes,None,True)")
code=code.replace("cmds.text(label='此工具用于查找并删除场景中包含中文或乱码路径的节点', height=30, align='left')", "cmds.text(label='按路径字符策略检查；非ASCII不等于文件损坏。',height=30,align='left')\n    menu=cmds.optionMenu(label='检查策略',changeCommand=set_policy)\n    for label in ('ASCII兼容策略','仅中日韩汉字策略','仅Unicode替换字符'): cmds.menuItem(label=label)\n    cmds.optionMenu(menu,edit=True,select={'ascii':1,'cjk':2,'replacement':3}[policy])\n    cmds.checkBox(label='允许移除完整引用（默认关闭）',value=allow_reference,changeCommand=set_reference)")
code=code.replace('中文或乱码路径','违反字符策略的路径').replace('中文/乱码路径','字符策略路径')
code=code.replace('    cmds.showWindow(window)\n','    cmds.showWindow(window)\n    return window\n')
code=code.replace("    window_name = 'cleanInvalidPathsWindow'","    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')\n    window_name = 'cleanInvalidPathsWindow'")
ast.parse(code)
(PKG/'ui.py').write_text('\n'.join(line.rstrip() for line in code.splitlines())+'\n',encoding='utf8',newline='\n')
print('Full original native inspection UI and self-contained reference helpers prepared')
