import maya.cmds as cmds

def get_hierarchy_info(nodes):
    """
    获取所选物体的层级关系信息
    
    Args:
        nodes: 需要分析的物体列表
        
    Returns:
        dict: 包含每个物体层级关系的字典 {node: [parents]}
    """
    hierarchy_info = {}
    
    for node in nodes:
        # 获取物体的所有父级
        parents = []
        parent = node
        while True:
            parent_node = cmds.listRelatives(parent, parent=True, fullPath=True)
            if not parent_node:
                break
            parents.append(parent_node[0])
            parent = parent_node[0]
        
        # 存储层级关系
        hierarchy_info[node] = parents
        
    return hierarchy_info


def get_constraint_info(nodes):
    """
    获取所选物体的约束关系信息
    
    Args:
        nodes: 需要分析的物体列表
        
    Returns:
        dict: 包含约束关系的字典 {constrained_node: [driver_nodes]}
    """
    constraint_info = {}
    
    # 约束类型
    constraint_types = [
        'pointConstraint', 'orientConstraint', 'scaleConstraint', 
        'parentConstraint', 'aimConstraint', 'geometryConstraint'
    ]
    
    for node in nodes:
        # 查找影响该物体的约束
        constraints = []
        for const_type in constraint_types:
            # 查找此物体上的约束
            const_nodes = cmds.listConnections(
                node, 
                source=True, 
                destination=False, 
                type=const_type
            )
            if const_nodes:
                constraints.extend(const_nodes)
        
        # 获取约束的驱动物体
        drivers = []
        for constraint in constraints:
            if constraint:
                # 获取约束的目标列表（驱动物体）
                target_list = None
                constraint_type = cmds.nodeType(constraint)
                
                try:
                    if constraint_type == 'parentConstraint':
                        target_list = cmds.parentConstraint(constraint, q=True, targetList=True)
                    elif constraint_type == 'pointConstraint':
                        target_list = cmds.pointConstraint(constraint, q=True, targetList=True)
                    elif constraint_type == 'orientConstraint':
                        target_list = cmds.orientConstraint(constraint, q=True, targetList=True)
                    elif constraint_type == 'scaleConstraint':
                        target_list = cmds.scaleConstraint(constraint, q=True, targetList=True)
                    elif constraint_type == 'aimConstraint':
                        target_list = cmds.aimConstraint(constraint, q=True, targetList=True)
                except:
                    continue
                
                if target_list:
                    drivers.extend(target_list)
        
        # 存储约束关系
        if drivers:
            constraint_info[node] = drivers
    
    return constraint_info


def build_global_influence_graph():
    """
    构建包含整个场景中所有约束和层级关系的影响图
    
    Returns:
        dict: 影响关系图 {node: set(influenced_nodes)}
    """
    # 获取场景中所有变换节点
    all_transforms = cmds.ls(type='transform')
    
    # 构建影响图
    influence_graph = {node: set() for node in all_transforms}
    
    # 添加层级关系（父物体影响子物体）
    for node in all_transforms:
        children = cmds.listRelatives(node, children=True, type='transform', fullPath=True) or []
        for child in children:
            influence_graph[node].add(child)
    
    # 添加约束关系（驱动物体影响被约束物体）
    constraint_types = [
        'pointConstraint', 'orientConstraint', 'scaleConstraint', 
        'parentConstraint', 'aimConstraint', 'geometryConstraint'
    ]
    
    for const_type in constraint_types:
        constraints = cmds.ls(type=const_type) or []
        
        for constraint in constraints:
            # 获取被约束物体
            constrained = None
            
            try:
                if const_type == 'parentConstraint':
                    connections = cmds.listConnections(constraint + '.constraintParentInverseMatrix', destination=False) or []
                    if connections:
                        constrained = connections[0]
                elif const_type in ['pointConstraint', 'orientConstraint', 'scaleConstraint', 'aimConstraint']:
                    # 尝试不同的连接来找到被约束物体
                    for attr in ['.constraintTranslateX', '.constraintRotateX', '.constraintScaleX']:
                        try:
                            connections = cmds.listConnections(constraint + attr, destination=False) or []
                            if connections:
                                constrained = connections[0]
                                break
                        except:
                            continue
            except:
                continue
                
            if not constrained:
                continue
                
            # 获取驱动物体
            drivers = []
            try:
                if const_type == 'parentConstraint':
                    drivers = cmds.parentConstraint(constraint, q=True, targetList=True) or []
                elif const_type == 'pointConstraint':
                    drivers = cmds.pointConstraint(constraint, q=True, targetList=True) or []
                elif const_type == 'orientConstraint':
                    drivers = cmds.orientConstraint(constraint, q=True, targetList=True) or []
                elif const_type == 'scaleConstraint':
                    drivers = cmds.scaleConstraint(constraint, q=True, targetList=True) or []
                elif const_type == 'aimConstraint':
                    drivers = cmds.aimConstraint(constraint, q=True, targetList=True) or []
            except:
                continue
                
            # 更新影响图
            for driver in drivers:
                influence_graph[driver].add(constrained)
                
                # 约束会覆盖层级关系，所以移除父级对被约束物体的影响
                parent = cmds.listRelatives(constrained, parent=True, fullPath=True)
                if parent and parent[0] in influence_graph and constrained in influence_graph[parent[0]]:
                    influence_graph[parent[0]].remove(constrained)
    
    # 计算传递闭包 - 处理间接影响
    changed = True
    while changed:
        changed = False
        
        for node in all_transforms:
            influenced_nodes = list(influence_graph[node])
            
            for influenced in influenced_nodes:
                for indirect_influenced in influence_graph.get(influenced, set()):
                    if indirect_influenced not in influence_graph[node]:
                        influence_graph[node].add(indirect_influenced)
                        changed = True
    
    return influence_graph


def analyze_influence_hierarchy(nodes):
    """
    分析物体间的影响层级
    
    Args:
        nodes: 需要分析的物体列表
    
    Returns:
        list: 按影响层级排序的物体层级列表
    """
    # 获取层级和约束信息
    hierarchy_info = get_hierarchy_info(nodes)
    constraint_info = get_constraint_info(nodes)
    
    # 构建影响图
    influence_graph = {}
    for node in nodes:
        influence_graph[node] = set()
        
        # 添加层级关系
        if node in hierarchy_info:
            for parent in hierarchy_info[node]:
                if parent in nodes:  # 只考虑在选中节点中的父级
                    influence_graph[node].add(parent)
        
        # 添加约束关系
        if node in constraint_info:
            for driver in constraint_info[node]:
                if driver in nodes:  # 只考虑在选中节点中的驱动物体
                    influence_graph[node].add(driver)
    
    # 使用拓扑排序确定层级
    sorted_nodes = topological_sort(influence_graph, nodes)
    
    # 将排序后的节点分组到层级中
    influence_layers = []
    remaining_nodes = set(sorted_nodes)
    
    while remaining_nodes:
        # 当前层级中的节点不会影响同一层级中的其他节点
        current_layer = []
        nodes_to_remove = set()
        
        for node in remaining_nodes:
            # 检查此节点是否影响当前层级中的任何节点
            influences_current_layer = False
            for layer_node in current_layer:
                if layer_node in influence_graph.get(node, set()):
                    influences_current_layer = True
                    break
            
            if not influences_current_layer:
                current_layer.append(node)
                nodes_to_remove.add(node)
        
        remaining_nodes -= nodes_to_remove
        influence_layers.append(current_layer)
    
    return influence_layers


def topological_sort(graph, nodes):
    """
    对有向无环图进行拓扑排序
    
    Args:
        graph: 影响关系图 {node: set(influenced_nodes)}
        nodes: 需要排序的节点列表
    
    Returns:
        list: 拓扑排序后的节点列表
    """
    # 计算每个节点的入度（被影响次数）
    in_degree = {node: 0 for node in nodes}
    for node in nodes:
        for influenced in graph.get(node, set()):
            in_degree[influenced] = in_degree.get(influenced, 0) + 1
    
    # 找出入度为0的节点作为起始节点
    queue = [node for node in nodes if in_degree[node] == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        # 更新受此节点影响的节点的入度
        for influenced in graph.get(node, set()):
            in_degree[influenced] -= 1
            if in_degree[influenced] == 0:
                queue.append(influenced)
    
    # 如果结果长度不等于节点数，说明图中有环
    if len(result) != len(nodes):
        # 尝试打破环
        remaining = set(nodes) - set(result)
        result.extend(list(remaining))
        cmds.warning("影响关系图中存在环，结果可能不准确")
    
    return result


def verify_influence_hierarchy(influence_layers):
    """
    验证影响层级的正确性
    
    Args:
        influence_layers: 按影响层级排序的物体层级列表
    
    Returns:
        bool: 验证结果
    """
    # 建立一个字典，存储每个节点的层级
    node_layers = {}
    for i, layer in enumerate(influence_layers):
        for node in layer:
            node_layers[node] = i
    
    # 构建全局影响图
    global_influence_graph = build_global_influence_graph()
    
    # 检查每个物体是否被它应该被影响的物体所影响
    for i, layer in enumerate(influence_layers):
        for node in layer:
            for j, other_layer in enumerate(influence_layers):
                if j < i:  # 只检查较低层级的物体
                    for other_node in other_layer:
                        if node in global_influence_graph.get(other_node, set()):
                            # 此节点被较低层级的节点影响，这是正确的
                            pass
                        elif other_node in global_influence_graph.get(node, set()):
                            # 此节点影响了较低层级的节点，这是错误的
                            print(f"警告: {node}(层级{i+1})影响了{other_node}(层级{j+1})，但它应该是相反的")
                            return False
    
    return True


def main():
    """
    主函数，获取所选物体并分析其影响层级
    """
    # 获取所选物体
    selected_nodes = cmds.ls(selection=True, long=True)
    
    if not selected_nodes:
        cmds.error("请选择至少一个物体")
        return
    
    # 分析影响层级
    influence_layers = analyze_influence_hierarchy(selected_nodes)
    
    # 验证结果
    is_valid = verify_influence_hierarchy(influence_layers)
    
    # 输出结果
    result = "影响层级分析结果:\n"
    for i, layer in enumerate(influence_layers):
        result += f"\n第{i+1}层级 (不会影响同层级物体):\n"
        for node in layer:
            # 获取短名称以便显示
            short_name = node.split('|')[-1]
            result += f"  - {short_name}\n"
    
    result += "\n"
    if is_valid:
        result += "验证通过: 所有层级关系正确。"
    else:
        result += "验证失败: 存在问题，请查看脚本编辑器中的警告信息。"
    
    # 创建结果窗口
    if cmds.window("influenceHierarchyWindow", exists=True):
        cmds.deleteUI("influenceHierarchyWindow")
    
    cmds.window("influenceHierarchyWindow", title="物体影响层级分析", width=400)
    cmds.columnLayout(adjustableColumn=True)
    cmds.scrollField(text=result, editable=False, wordWrap=True, height=400, width=400)
    cmds.button(label="关闭", command=("cmds.deleteUI(\"influenceHierarchyWindow\")"))
    cmds.showWindow("influenceHierarchyWindow")


# 运行主函数
if __name__ == "__main__":
    main() 