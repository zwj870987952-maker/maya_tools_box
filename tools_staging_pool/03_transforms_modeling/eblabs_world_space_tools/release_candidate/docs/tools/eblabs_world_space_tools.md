# EB Labs WorldSpaceTools 完整源码候选

`prepared_unverified`；真实GUI、生产rig和新版Beta Hub未验收。原174文件、114 Python模块、336函数/类完整归档并记录逐字节SHA，所有图片/SVG/GIF/字体/charmap/metadata/原偏好/版本文件保留。bundle保留全部提供的Python源码，native.py保留旧版worldspace.py全部类/方法、业务算法和Spaces/Extras/Paths/Copy完整窗口。候选自包含，完整代码、资源、文档、测试、注册面板的晋级清单已备齐。

新版Hub采用2.7/3.7/3.9/3.10专用混合模块，原包缺370个版本模块文件（覆盖多个Python版本及Hub family，不能解读成当前入口需同时安装370项）。Maya2025 Python3.11不匹配。保留所有已提供模块，不伪造Core/UXFramework/LicenseManager实现，不更改原授权逻辑。`open_beta`预检明确失败并报告原因；将来可在支持的Maya/Python/Qt和合法完整EB Labs发行环境中传`beta_root`（包含eblabs_hub的绝对根）调用原Spaces.launch，命名空间来源冲突需新会话，原授权检查不变。旧版源码原本独立可读，候选直接从随包JSON读取metadata/version，不依赖缺失的Hub读元数据模块；不安装shelf、不自动执行安装器、不联网更新。

`WorldSpaceToolsTool`，category=`animation`，Base/ToolResult/Schema/Undo。默认inventory只读返回范围、缺失依赖、gui_acceptance。validate/dry_run不导入完整原UI、不写节点/关键帧/时间/选择/Undo/偏好。失败报告真实原因。输入按action严格校验，不忽略不适用参数。

|action|输入/原业务|结果与影响|
|---|---|---|
|to_world|objects省略用有序选择；attributes默认tx/ty/tz/rx/ry/rz|完整原world control、hook、constraint、颜色/尺寸、稀疏动画与源通道接管|
|to_parent|前面对象为目标，最后对象为父空间|原parent group/constraint跟随与world control|
|to_local|选择本候选拥有的world control|采样源动画，删除确切拥有的helper，再回烘local；外部旧EB辅助节点拒绝自动清理|
|ik_chain|有序链与TR属性|完整原逆序chain、aim/offset/hook/旋转偏移算法，不是新造IK解算器|
|create_paths|选择动画目标|原逐帧世界轨迹curve，原first到last的range不含最后帧；无动画用playback范围|
|path_locator|有序curve、动画目标|原nearestPoint/curveInfo采样及motionPath locator|
|rebuild_path|明确curve transforms，spans默认6、1..200|原rebuildCurve|
|copy|第一对象动画驱动，后面所有对象目标；maintain_offset默认False|原约束采样/关键帧复制/特殊tick/tangent/euler filter；修正原只给最后目标采样的缺陷|
|snap|严格两个有序对象，第一为来源、第二为目标|原临时constraint采样当前位置/旋转|
|child_cog / parent_cog|选择原控制器|完整原COG/hierarchy算法|
|gimbal|选择控制器，真实GUI|原多rotate order分析与文字报告|
|open_ui / open_beta|原完整窗口；Beta可选beta_root|UI实际运行另行验收，Beta保留原外部依赖|
|import_preferences / export_preferences|绝对JSON path，导出要求新文件和现有父目录|会话偏好明确持久化，独占不覆盖，文件不能Undo|

to_world/to_parent/ik_chain/copy的`on_keys=True`保留原稀疏采样；False必须提供成对start/end（有限数、顺序正确、跨度最多10000帧），使用原逐帧算法。to_local按原保存的commonAttributes回烘；API不重新指定其它属性。API调用不使用GUI高亮区间；原UI回调保留原高亮时间/通道选择行为。create_paths/path_locator仍按原动画范围采样，range末帧不包含是原行为。

对象必须唯一transform/joint，无通配符/组件/代码字符；拒绝引用/锁/真DAG实例、非支持外部驱动/动画层、共享曲线外部使用者。全表预检包括已有owned helper、原对象、曲线和local删除范围，foreign child/新增外部连接阻止清理。新建节点按实际UUID和持久owner token标记，不靠后缀猜删除范围；原metadata同时存UUID，原对象重命名后可继续回烘。helper不得手工接管/复制owner属性，场景复杂graph和生产rig仍需实测。

全原scene写函数及UI回调经标准入口；原算法的真实写命令受到允许UUID限制。临时约束和owned helpers可删除，目标动画曲线可改写，原scene其它节点不被删除。源命名与Maya basename契约修复、toWorld跳过旋转用实际targetObject、copy对全部目标采样并修正special-tick字符串遍历。原包含空的copyAtoB占位方法仍保留，不把其当已实现算法；真正复制业务在CopyAtoB类。

原自动用户AppDir偏好写改会话内存，`eval` scene preference改literal_eval，缺省变量修正；导出JSON显式且不覆盖。去全局隐藏pane/改变isolate以及长期嵌套Undo chunks，保持框架Undo。执行finally恢复time、选择、AutoKey、namespace、原animBlendingOpt；selection对象被local删除则只恢复仍存在的条目。原动画clipboard、buffer和tangent/euler过滤仍有影响；一次Undo场景节点/动画可恢复，clipboard/UI/偏好文件不承诺Undo。失败可能已有部分写入，标准结果明确失败，检查并Undo。

```python
tool = load_tool()  # 候选launch_candidate.py
p = dict(action='to_world', objects=['character_control'])
print(tool.run(dry_run=True, **p).to_dict())
print(tool.run(**p).to_dict())
tool.show_ui()  # 完整原四页窗口，仅真实GUI
```

复用现有框架协议和Undo，不修改core或正式库。root_motion_bake、EB ScreenSpace与此有采样/constraint概念关联，但空间控制器metadata、清理范围与算法不同，未声称组合已验证。候选测试仅证明自己API；不能把旧版源码检查等同Beta Hub通过。Eric Bates/EB Labs私有版权，原管理器/许可信息完整保留，无公开再发布授权推断。

2组离线检查：全部原字节/定义/资源闭包、严格协议及session偏好/no eval。4组隔离Maya2025：实际world/parent/local动画值与keytime、源重命名UUID、dry不变/单Undo；多目标copy、路径curve/逐帧采样；foreign child/共享曲线/实例/锁/错范围/缺Beta及batchGUI拒绝。IK/pathLocator/COG/gimbal完整源码保留，其实际生产效果和全部原GUI按钮仍not_run。跨版本验证缺失，不迁正式库。
