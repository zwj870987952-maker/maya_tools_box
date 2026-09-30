# bh_speedLines 真人验收

prepared_unverified，GUI not_run。只在真实 Maya 备份场景验收；关闭原窗口，不安装 Shelf/复制原脚本至 scripts。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\bh_speedlines\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 开/关/重开原生窗口，相机列表/更新、全部菜单、按钮和滑条正常，Script Editor 无致命报错。打开窗口不改变 nurbsToPolygonsPref。
2. 对明确两曲线执行 geometry dry_run，比较节点、偏好、选择、时间和 Undo 队列无写入。默认/高细节、层开关、保留曲线开关各验收，观察朝向、pivot、输入曲线消耗；一次 Undo 撤回场景修改且应用偏好恢复。
3. 测试 flip、curve/mesh simplify、smooth，检查拓扑/CV/pivot/history和 Undo。带历史对象观察 Maya ch=0 ignored 提示，不能据此认定没有新增历史。
4. 可见性一帧/两帧、小数时间、邻帧已有键，检查整数截断与覆盖，transform 键与 shape 不打键；Undo、实际播放符合预期。
5. 透视/实际制作相机分别 Pencil/EP Enter Drawing Mode，鼠标画出两曲线；深度拖动/释放、reset、near clip 限制和两位截断正确。退出后曲线保留，自己的 plane 消失，原 live 对象、原工具上下文恢复。
6. EP 切换鼠标工具、绘画中关窗口、Undo 删 plane/deferred 清理、Redo、退出重开，检查残留 plane/scriptJob/live/context。GUI 异步事件尚未自动验证，逐项记录；Redo 若留 plane 需 stop_draw，不凭原归组声称上下文复原。
7. 创建外部同名 plane/layer 应拒绝；候选 plane 重命名后深度拒绝、stop_draw 仍安全清理。添加外部子对象/连接应拒绝，不能误删。引用/锁/歧义/重复输入、曲线外部消费者同样拒绝。保存/切场景之前退出绘画，再检查重新加载的 owned 记录可安全清理。
8. 完整绘画两曲线→退出→生成速度线→简化/翻面→可见性→手动材质预览，检查四纹理素材可访问且不会自动写材质或安装文件。生产 rig/旧版本需独立复验。

记录实际版本、日期、验收人、逐项结果及 Script Editor 问题；修复候选后重验。通过后建立真实记录：

```json
{"tool_id":"bh_speedlines","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

先用 plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 得到当前哈希/目标路径。当前哈希对应的真人记录才可 --acceptance <记录> --apply；正式库在此之前不变。
