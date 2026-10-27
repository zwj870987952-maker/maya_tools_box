# Skin Info / Super Connect / Timal 完整套件候选

本单元有 7 个原始文件：Skin Info 1.92/1.7（Khaled Hussein）、Super Connect（同作者）的完整代码/图标/安装说明/installer、Hugo Timal 的 Export-Import JointsWeights 1.3。原字节及 SHA 全保留。33 个 MEL 过程和 Timal 全部类方法保存在审计代码中；完整原界面布局的业务回调均改为安全 API，原 installer 不执行。无许可文件，不推断发布许可。

工具 ID `skin_info_and_super_connect`，类别 `rigging`，采用 BaseMayaTool/ToolResult/Schema、框架单 Undo chunk。真实 Maya GUI/生产 rig/版本验收均 not_run；候选包不能据此直接迁入正式库。

## 完整功能与参数

`inspect` 返回资源和完整过程清单；`info` 返回每个 mesh 的 skinCluster、全部/weighted influences、顶点数及拓扑指纹；`select_weighted` 选择有权重关节；`select_influences` 解析 TXT 关节名称并加入选择（保留原选择中的 mesh）；`lock_weights`/`unlock_weights` 修改所选/显式 joint 的 liw。

`objects` 省略使用当前完整节点选择；必须非空、有唯一 DAG 路径、不引用/锁定写入节点。每个皮肤对象只支持一个 polygon shape、至多一个 skinCluster；不自动处理多层蒙皮、组件或 DAG 实例。批次上限 1000；现有皮肤事务最多 200 万顶点×关节权重。属性/驱动锁及 liw 锁拒绝，以免静默丢权重。源查询只读，目标写入须可编辑。

`export` 使用明确绝对既有 `directory`；`formats=['xml']` 或 `['xml','json']`。`basename` 单对象自定义，批处理从 mesh 叶名移除 namespace 派生，重名整体拒绝。全部输出以独占新文件预留，禁止覆盖/软链接/路径逃逸/保留设备名；失败清理仅本次新建文件。SkinInfo 格式为 base.txt（安全 select-add 名称列表）+ base.xml/json；Timal `convention='timal'` 为 plain joint TXT + base_sknCls.xml。两者额外生成 base.staging.json 记录顶点拓扑，不改变原权重文件格式。

`import` 只选一个格式，读取同名 TXT/权重；index 映射，必须匹配 staging 元数据的拓扑。旧文件缺 metadata 时需显式 `allow_unchecked_topology=True` 并人工核查顶点编号。TXT 只解析有限关节名，不 eval，不执行任意 MEL/Python。XML 不接受 DOCTYPE/ENTITY；JSON 不接受非有限数字；文件限大小。所有批次先全部预检，再写场景。已有 skin 需包含全部导入 influence；否则明确拒绝，不自动篡改已有蒙皮。未绑定时 `create_skin=True` 创建；False 仅已有蒙皮。

Timal 的 `post_normalize=True` 保留 post normalize 方式，新 skin normalizeWeights=2，导入后不 forceNormalize；默认及 SkinInfo 则导入后 forceNormalize。为保证现有 skin 的 Undo，不仅调用 deformerWeights：采集原与导入权重，API 恢复原权重后通过 undoable skinPercent 回放导入值。每次一个 Undo chunk；新创建 skin 的 Undo 恢复未绑定状态。外部导出文件不受 Maya Undo；MEL 声明和窗口亦不属于场景 Undo。

`transfer` 首 mesh 为源，后续目标创建/复用 skin，再 copySkinWeights（closestPoint，名称/closestJoint influence），保留原 pruneWeights=0.05 和 removeUnusedInfluence。`delete_history=True` 必须另有 `allow_delete_history=True`，仅目标历史，不改源；默认保留目标构建历史。`copy` 要求全部目标已绑定。原 TransferSkin 错误的 influence 越界循环、吞失败及第二次重复全量复制不再执行，实际结果失败明确返回。

`connect` 要求明确 `sources`/`destinations`；移除 namespace 后按 `source_prefix`/`destination_prefix` 各移除一次字面量前缀匹配，返回 matched/unmatched 对象与将替换的连接。重复匹配键、零匹配、自连接、层级/已有依赖反馈拒绝。`channels` 为 tx/ty/tz/rx/ry/rz/sx/sy/sz 的选择；`mode=direct` 对所选轴 connectAttr，已有驱动需 `allow_replace_connections=True`；constraint 模式 parent/point/orient/point_orient 只使用相关 TR 轴，`maintain_offset=True` 默认，不替换既有驱动。与原 MEL 正则 substitute 不同，候选按字面量处理 prefix，避免意外扩大匹配。不改变未选属性/其它配对。

## 界面、影响与组合

`show_ui()` 打开四入口面板，每项打开完整原 SkinInfo1.92、SkinInfo1.7、SuperConnect、Timal 布局。原 Browse/GetInfo/AutoImport/批处理/导入导出/transfer/copy/锁按钮及 Source/Destination 列表/模式/轴/MO 全保留并路由 API。安全勾选明确处理已有连接替换、删目标历史、旧 topology map；默认关闭。原 windowPref/安装器全局写入不执行；Timal 去掉 import-time 窗口，原类布局通过子类回调复用。

只读 `dry_run=True` 无文件、节点、UI、MEL 声明或选择变化；执行除明确选择动作外恢复原选择 UUID。锁权重、连接、创建 skin 和转移属于场景写入，导出是外部文件写入。可先用 hierarchy_analyzer 审核骨架/名称；info 可供权重备份与后续批处理选择；connect 产生驱动关系后不能直接当作独立普通动画输入交给动画工具，需先人工烘焙。以上是接口条件说明，未声明真实组合通过。

```python
tool.run(dry_run=True, action='export', objects=['body_geo'],
         directory='E:/temp/weights', formats=['xml','json'])
tool.run(action='export', objects=['body_geo'],
         directory='E:/temp/weights', formats=['xml','json'])
tool.run(action='import', objects=['body_geo'], directory='E:/temp/weights')
tool.run(action='connect', sources=['src:S_hand'], destinations=['dst:D_hand'],
         source_prefix='S_', destination_prefix='D_', channels=['tx','ty','tz'])
```

隔离检查覆盖全 MEL/UI 定义无副作用编译、XML/JSON/Timal 权重实值往返及现有 skin Undo、Timal 新绑定、转移与 Undo、复制、info/weighted 选择、关节锁、恶意 TXT 拒绝/拓扑保护、direct 与各约束。完整 GUI、复杂生产蒙皮、命名/姿态差异、性能、目标历史删除和跨版本仍需人工验收。
