# Overslapper 真实 Maya 验收

仅使用备份/临时场景和临时JSON目录。许可原文在payload/upstream/LICENSE.txt，本候选不构成修改或发布授权，不分享/上传套件。mayapy检查不等于以下UI/运动验收。

1. 在真实Maya Python Script Editor执行：

```python
import runpy
tool = runpy.run_path(r"E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\overslapper_v1_03\release_candidate\launch_candidate.py")["load_tool"]()
print(tool.run(action="open_ui").to_dict())
```

2. 核对完整旋转/平移面板、两个图标、主/上轴六向、选择轴、Manual/Playback/Selection范围、顺序/名称/分组、普通/复杂刚度渐变、两个layer选择、过冲、风、全部/部分JSON进出；检查Script Editor无致命错误，进度/光标结束恢复。高DPI布局与原20页手册页6..20对照；不运行安装器，不创建shelf或拷贝userScripts。
3. 临时动画父级下做tail1..3本地transform控制器，旋转测试1..12、六rotateOrder/不同主上轴、0/.5/1刚度/正负与0 strength、自身平移忽略、距离自动/强制。实际比较原工具合法测试中的视觉延迟/顺序级联；只选z时x/y保持，单控制器无child可执行。预检非零rotateAxis/joint/引用/锁/driver拒绝是明确适用边界。
4. 平移父级tx动画，frame lag 0/1/2.5、只选x、replacer/additive/deleteall。确认y/z原位不变，additive不会删范围外键、deleteall仅目标通道全时间键被删。负wind/frame lag小数输入不被slider回写；看实际父级旋转/非均匀或负scale下效果，不把finite检查当运动正确。
5. 三种时间范围和整数端点；拒绝小数端点/空轴/坏刚度/超预算。循环在起终点预览，去父级影响与旋转自身平移切换效果核对；不同DAG父级同短名/namespace自然排序分组要可解释。UI复杂曲线按组位置采样行为与手册一致。
6. 新建override/additive层及明确已有层：先备份base/foreignLayer键，运行后只有chosen attrs加入目的层、cut/scale只该层，其他层/base值保持。检查目的层数值是原始layer键值，合成结果随layer类型/权重叠加，不能当目标最终姿态求解。结束原选择/preferred恢复，新层不残留首选。layer lock/mute或隐式层不确定时明确拒绝。
7. 过冲first/between/end/strength/frequency不同组合，逐个稳定区看峰谷衰减和末尾。可在end之后写尾键，记录实际生成范围；结束绝对帧不再重复加start，源除零修正按至少1帧处理。视觉结果满意才通过，始终做一次Undo/Redo检查整个动作。
8. 创建30点风曲线，旋转/手动strength、开关、select、visibility不关闭效果、多个风相加、namespace深度≥3/改名tag仍找得到。风曲线复制不作为推荐场景（原手册限制）；API winds可限定一条，原GUI开关全部完整tag风控。负强度及绝对平移wind均测试；无启用风明确失败，风正反矩阵修正后的运动与期望比较。
9. 全部/部分预设导入8组开关，非法JSON在改变控件前拒绝；旧default可读，新文件含frame_lag/wind strength，重开读回。保存取消无文件；同名覆盖只经确认/overwrite，文件不能Undo。import不执行代码、不改业务场景，私有渐变optionVar不会覆盖pratte_custom_var；关窗清理自身gradient/window，再开无残留/重复旧窗口。
10. inspect/dry_run确认不改scene/time/select/AutoKey/namespace/layer/Undo/optionVar/文件。失败或受锁对象只报真实错误；已写部分键的业务异常可一次Undo，不宣称自动回滚。记录Maya/Python/Qt、帧范围、rig条件、每项结果及缺陷。

用户逐项通过并确认后，用promotion.json及plans/staging_run/promote_candidate.py的预制流程/hash验收记录进行一次晋级，注册ALL_TOOL_CLASSES和面板；本轮仅预览，没有迁入正式库。
