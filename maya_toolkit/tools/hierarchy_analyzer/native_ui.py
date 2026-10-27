import maya.cmds as cmds
from .tool import HierarchyAnalyzerTool

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
    analysis = HierarchyAnalyzerTool().run(objects=selected_nodes)
    if not analysis.success:
        cmds.warning(analysis.message)
        return
    influence_layers = analysis.data["layers"]

    # 验证结果
    is_valid = analysis.data["valid"]

    # 输出结果
    result = "影响层级分析结果:\n"
    for i, layer in enumerate(influence_layers):
        result += f"\n第{i+1}层级 (不会影响同层级物体):\n"
        for node in layer:
            # 获取短名称以便显示
            short_name = node
            result += f"  - {short_name}\n"

    result += "\n"
    if is_valid:
        result += "结构图分层校验通过；不代表 Maya 全部 DG 求值依赖。"
    else:
        result += "验证失败: 存在问题，请查看脚本编辑器中的警告信息。"

    if analysis.data["unresolved"]:
        result += "\n未解决环或被环阻塞的节点：\n" + "\n".join(analysis.data["unresolved"])
    for warning in analysis.data["warnings"]:
        result += "\n" + warning
    # 创建结果窗口
    if cmds.window("influenceHierarchyWindow", exists=True):
        cmds.deleteUI("influenceHierarchyWindow")

    cmds.window("influenceHierarchyWindow", title="物体影响层级分析", width=400)
    cmds.columnLayout(adjustableColumn=True)
    cmds.scrollField(text=result, editable=False, wordWrap=True, height=400, width=400)
    cmds.button(label="关闭", command=lambda *unused: cmds.deleteUI("influenceHierarchyWindow"))
    cmds.showWindow("influenceHierarchyWindow")
