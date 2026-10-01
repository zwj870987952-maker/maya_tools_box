# 层级分析真实 Maya 验收（not_run）

1. 真实交互 Maya 新建备份测试场景，用 importlib 加载本目录 launch_candidate.py 并调用 show_ui。检查原完整窗口、滚动结果、完整 DAG 名、关闭按钮及 Script Editor。未选择对象时应明确提示。
2. 用 namespace、相同 leaf 不同父级、joint 长链与多个独立对象检查祖先链和稳定层级；无关系对象可以同层，所有选中父级必须前于被影响节点。
3. 使用 parent/point/orient/scale/aim/geometry 及实际需要的 normal/tangent/poleVector/pointOnPoly，各驱动和实际 child 名称、顺序与约束设置一致；驱动和被驱动方向不能颠倒，未选中中介的间接路径也要体现。
4. 验证保留父子潜在边、零权重保守边的说明；图仅反映结构，不宣称实际 Maya Evaluation Manager 求值顺序，复杂矩阵/表达式/动力学/插件需另行分析。
5. 在备份场景制作结构环及下游阻塞，结果应 valid=false，单独显示 cycles/unresolved，不能把未解决对象追加成正常层。用纯图测试可先验证环算法，真实 DG 环请保持在简单备份场景。
6. 只读 API 与 GUI 打开前后的节点/选择/当前帧/Undo/AutoKey/namespace 均不被分析修改；重复别名、实例、不明确输入及预算超限应明确拒绝，不输出“部分验证通过”。
7. 真实 GUI 与实际场景结果满意后，制作 tool_id=hierarchy_analyzer、passed=true、Maya版本/验收人/时间/最新 candidate_sha256 的 acceptance JSON。先 promote_candidate.py --candidate <本目录> --acceptance <json> 预览，再附 --apply 安放代码/原档/知识/目标测试和注册；正式面板复验。

隔离单测不等于真实 GUI 或生产图验收；本轮不提前转正。
