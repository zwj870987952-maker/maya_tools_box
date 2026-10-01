# Shift Animation v3.2 真人 Maya 验收：not_run

用复制的动画/rig 场景；商业使用依原 vendor/License.txt，不安装或执行原拖放 Shelf 脚本。

```python
import runpy
tool=runpy.run_path(r'E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/shift_animation_v3_2/release_candidate/launch_candidate.py')['load_tool']()
tool.show_ui()
```

1. 独立全量前端、bitmap、字段/按钮/折叠块/仅预检响应，Script Editor 无 Fatal Traceback；完整原版可通过 show_original_ui 显式对照，但先关候选，原回调不受外围保护，不同时运行。
2. mocap 脚/膝/主控制器/骨盆放非 Base 层，关键帧平移后 MATCH：比较源层静音、复制结果层、T/R 各帧、脚滑和 Euler 结果；明确观察全部原通道和层旗标，不只验证产生一个层。转向另层再做。
3. Extract 选中控制器到独立层；原已有锁定/引用层及外来共享输入曲线应先拒绝；小数 MATCH keys、CV 数导致 int step=0、错误或多个已选层、非运动控制器需明确失败而非输出空结果。
4. AUTOPATH 的 root-motion moving control 自动检测/显式指定、CV/flat/easing/vertical independent，全程生成曲线/约束/path/uValue/烘焙/清理及新结果层，并对照原 guide。
5. 手工 create path→控制 CV/Lock/Unlock/Project→apply，所有阶段用同一会话；曲线重命名/Undo 后仍解析正确 UUID。外来子节点或历史/副形状/共享控制 metadata 先拒绝，不能顺带删除。
6. 多个不同曲线的 control systems，选具体控制器 arrange、delete（保留曲线）后其他系统不动；pending path 时控制器只绑定其 editable curve。原 arrange 的边界行为需实际检查，原源文件不修改。
7. Circle 的 fake/base/second 曲线、Bend_Control 曲率、平坦化、apply circle 和新层完整工作；Root Motion 的 main/pelvis、rotate/flat、冻结其它 layer member、全部 bake/简化/Euler 输出正常，upAxis Y/Z 分别观察。
8. 重点核对原清理影响：复制一份有 IK_FK 等自定义属性的控制器，默认预检明确列出并拒绝；另一份备份显式允许原 cleanup 后确认删除哪些属性、Undo 是否恢复。不对原生产 rig 直接尝试。
9. dry 不动节点/属性/time/selection/Undo/prefs，不 source vendor。成功操作后的原层 mute/selected/preferred 保留算法输出；外围各类单位/autokey/缓存/evaluation/optionVars/trackSelection/刷新/时间滑块状态恢复；VP 主动恢复视口。
10. 故障时保留失败网络和暂存 UUID、正常恢复环境；停止继续写，Undo 失败调用后再运行。每次操作 Undo/Redo，pending 曲线保存重开、多个 namespace/同叶名、动画层链、跨 Maya2022/2025 等分别记录，不把可编译当效果通过。

原 MATCH/路径/Root Motion 依赖真实动画层与时间滑块 UI。batch 检查只验证数值和可运行的真实曲线网络，没有整体动作验收结果。填 Maya/版本/结果，失败先改外围适配或记录原软件问题与作者修正版需求，不改授权 vendor 文件、不转正。真人全部通过后生成 tool_id/candidate_sha256/passed/maya_version/accepted_by/date 验收文件，先预览 promotion，再依验收晋级；本轮不 apply/不运行 Obsidian 同步。
