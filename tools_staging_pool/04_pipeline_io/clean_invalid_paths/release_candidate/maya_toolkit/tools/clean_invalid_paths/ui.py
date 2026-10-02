"""Complete original native two-window inspection UI; explicit policy and deletion."""
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
def show_invalid_path_nodes():
    """
    显示包含无效路径的节点

    Returns:
        int: 找到的无效节点数量
    """
    invalid_nodes = find_invalid_path_nodes()
    if not invalid_nodes:
        cmds.confirmDialog(title='结果', message='未找到包含违反字符策略的路径的节点！', button=['确定'])
        return 0
    if cmds.window('invalidPathsWindow', exists=True):
        cmds.deleteUI('invalidPathsWindow')
    window = cmds.window('invalidPathsWindow', title='包含违反字符策略的路径的节点', width=800)
    cmds.columnLayout(adjustableColumn=True, columnOffset=['both', 10])
    cmds.text(label=f'找到 {len(invalid_nodes)} 个包含违反字符策略的路径的节点:', height=30, align='left')
    cmds.scrollLayout(childResizable=True, height=400)
    cmds.columnLayout(adjustableColumn=True)
    for node, path in invalid_nodes.items():
        node_type = cmds.nodeType(node)
        frame = cmds.frameLayout(label=f'{node} ({node_type})', collapsable=True, marginWidth=5, marginHeight=5, collapse=False, borderStyle='etchedIn')
        cmds.columnLayout(adjustableColumn=True)
        cmds.textField(text=path, editable=False)
        cmds.rowLayout(numberOfColumns=2)
        cmds.button(label='选择节点', command=partial(select_nodes,[node]))
        cmds.button(label='删除此节点', command=partial(remove_invalid_path_nodes,[cmds.ls(node,uuid=True)[0]],True))
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(200, 200, 200), columnAlign3=['center', 'center', 'center'])
    cmds.button(label='刷新', command=refresh)
    cmds.button(label='全部选择', command=partial(select_nodes,list(invalid_nodes)))
    cmds.button(label='全部删除', command=delete_all)
    cmds.setParent('..')
    cmds.showWindow(window)
    return window
    return len(invalid_nodes)

def create_ui():
    """
    创建工具UI界面
    """
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    window_name = 'cleanInvalidPathsWindow'
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    window = cmds.window(window_name, title='清理字符策略路径节点工具', width=400)
    cmds.columnLayout(adjustableColumn=True, columnOffset=['both', 10])
    cmds.text(label='按路径字符策略检查；非ASCII不等于文件损坏。',height=30,align='left')
    menu=cmds.optionMenu(label='检查策略',changeCommand=set_policy)
    for label in ('ASCII兼容策略','仅中日韩汉字策略','仅Unicode替换字符'): cmds.menuItem(label=label)
    cmds.optionMenu(menu,edit=True,select={'ascii':1,'cjk':2,'replacement':3}[policy])
    cmds.checkBox(label='允许移除完整引用（默认关闭）',value=allow_reference,changeCommand=set_reference)
    cmds.separator(height=10, style='none')
    cmds.button(label='查找字符策略路径节点', height=40, command=refresh, annotation='查找场景中所有包含违反字符策略的路径的节点并显示')
    cmds.separator(height=10)
    cmds.button(label='直接删除字符策略路径节点', height=40, command=partial(remove_invalid_path_nodes,None,True), annotation='直接查找并删除所有包含违反字符策略的路径的节点')
    cmds.separator(height=20)
    cmds.text(label='作者：Claude AI', align='center')
    cmds.showWindow(window)
    return window
    return window
