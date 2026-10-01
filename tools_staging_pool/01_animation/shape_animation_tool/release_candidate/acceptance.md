# Shape Animation Tool 真实 Maya 验收：not_run

仅在备份场景；不要执行原 `sat/__init__.py`（会自动建 UI/全局回调并尝试载入插件）。

```python
import runpy
tool = runpy.run_path(r'E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/shape_animation_tool/release_candidate/launch_candidate.py')['load_tool']()
tool.show_ui()
```

1. 全量原窗口/菜单/About/中文文本/重复呼出正常，Script Editor 无 Error/Fatal Traceback；关闭后无遗留 timeChanged job，原 timeline press/release 回调不被替换。
2. Add 选中模型、Pick 从可见非 intermediate 网格射线拾取、多层添加、清单切层与勾选、Remove/Remove All；在重复叶名、嵌套 namespace 和 mesh 重命名场景检查实际 UUID 对应对象，不删外部 `sat`/`shape_1_mult` 节点。
3. 1 帧 Key，10 帧 Edit 后用 Artisan/Vertex 编辑，Edit 完成；观察成对 baseline/positive 目标、负乘法器、时间曲线、之前/当前/之间帧形状；需验证皮肤、其他变形层、父旋转/缩放/pivot/非均匀缩放与变形器排序。
4. 首次激活 Artisan 是否仍需多次点击（原 Word 指出该现象）；Vertex、Reset 和画笔窗口全部响应。SHAPESBrush 仅在自行合法安装并加载其 plugin/MEL 后测试；缺少时禁用该按钮，其他操作须完整工作。
5. Edit 菜单和按钮均一次执行；换帧后仍显示待完成雕刻并提示，返回原帧或显式结束，目标归属不能随换帧/选中对象变化。关闭窗口会完成当前雕刻；若新增外来历史/子节点/改拓扑导致失败，窗口不隐式删数据。
6. Reset 清回本层禁用时的上游基准；Del key、Delete All Keys、重新使用空层、Layer On/Off、前后帧跳转，在多层上逐项确认。切线可编辑，整层 weight 曲线一致 retime 后更新帧；不一致/未知权重图明确拒绝。
7. dry_run 不建/改任何节点或时间/选择/Undo；引用/锁定、实例化、多 mesh/子 transform、拓扑变化、外部共享权重与曲线、非时间驱动均先拒绝。失败需 Undo 恢复已写部分，临时副本正常清理，原 envelope/选择/time/autokey/namespace 保持。
8. 开始/完成/Reset/删除分别一次 Undo/Redo；正在编辑及完成后分别 `.ma` 保存重开，候选会话、编辑 mesh、目标几何可恢复。GUI 的 Undo/时间回调不隐式提交雕刻，重复呼出/关闭不干扰其他工具 context。
9. 如有原 SAT 场景：先在旧工具完成编辑，另存备份；`tool.run(action='inspect_legacy')` 和 dry_run 只读。通过检查后显式 `tool.run(action='adopt_legacy',accept_legacy_ownership=True)`；旧 `sat` 网络不改，完整旧曲线/目标可继续修型；不得再用旧工具同时修改接管层。异常旧 pickle/共享图必须拒绝。

记录 Maya/Qt/Python 版本、每步结果及场景备份；未通过先修候选，不迁正式库。全部真人步骤通过后制作含 tool_id/candidate_sha256/passed/maya_version/accepted_by/date 的验收文件，先用 `plans/staging_run/promote_candidate.py --candidate 本目录` 预览，再按验收晋级。本轮不执行 apply、不运行 Obsidian 同步。
