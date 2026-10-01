# Retime Tools 真人 Maya 验收（not_run）

所有结果待用户填写；仅在备份动画场景与临时目录进行，候选不转正。

```python
import runpy
tool = runpy.run_path(r"E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/retime_tools/release_candidate/launch_candidate.py")['load_tool']()
tool.show_ui()
```

1. 原中文 Qt 窗口正常打开；控制器列表、连接树、重命名、颜色、确认按钮、折叠/编辑标签和关闭/重新打开逐项响应；Script Editor 不应出现致命错误。
2. 用两个不同命名空间的有动画控制器 Create/Add/Remove；确认只连接目标 animCurve，另一个 warp/约束/引用/锁定输出拒绝写入；移除后恢复 time 输入、动画没有冻结。
3. 修改 timeWarp 后 Enable/Disable/Reset；offline 槽保留动画，各操作一次 Undo/Redo，选择/time/autokey/namespace 恢复；保存 .ma 重开后行为一致。
4. 正负关键帧、零帧、线性/非线性/加权切线测 Shuffle；匹配原期望姿态与时间。单调反向另验切线、Infinity，非单调/hold 要拒绝逆操作并改用 Bake。逐帧检查 Bake，重点检查范围外关键帧影响。
5. Clean subframes 先复制曲线：核对负帧取整、整数帧保留及视觉变化。不得把数学取整变化当原界面已验收。
6. Invert 的末帧、短范围及状态列表响应；Delete 保留动画对象并恢复 time，控制器外部子节点存在时应拒绝删除；一次 Undo 应恢复控制器与原连接。
7. 用 API 将原两列 ASCII/一列值和 JSON 导入，再导出到临时目录；取消/坏文件/重复帧/NaN/已有文件/overwrite/读写权限失败逐项测试。导出的外部文件不可 Undo。
8. 复制历史 MEL 控制器，明确 update_legacy，验证 state 与旧 offline 状态，Undo 后可回到旧结构。
9. `tool.run(action='open_legacy_ui')` 在另一份备份场景验历史 MEL calculator、velocityTimeWarp、全部连接/筛选、shuffle/bake、子帧和进度 UI。其回调保留旧行为，与受预检保护的 Python API 分别记录；失败先修候选，不晋级。
10. 根据 docs/tools/retime_tools.md 末尾全体 211 方法/38 过程目录记录套件测试覆盖；Maya2025 以外版本、生产 rig、材质/动画层等不能由离线检查代替。

验收通过后生成带 tool_id、candidate_sha256、passed、maya_version、accepted_by、date 的验收文件，先运行 plans/staging_run/promote_candidate.py --candidate 本目录 查看晋级清单，再按已记录真人验收执行晋级。注册和面板变更由该脚本预制；本轮不 apply。
