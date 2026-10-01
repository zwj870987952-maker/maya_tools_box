# SmartMesh Tools

id `smart_mesh`，域 `modeling_surfacing`，Dennis Bartalon Porter 原1.1.0/27 January 2015，原MEL/README全字节SHA归档 upstream，所有四业务/窗口/工具架/快捷键/About源保留。候选四几何业务改显式Python命令与完整原生UI/API，继承Base，完整资源/知识/测试/面板晋级备齐；不source原MEL或安装偏好。GUI/复杂生产拓扑/跨版本not_run。

combine：objects默认当前整节点选择，可为无直接shape的组，扩展mesh叶；至少两mesh，合并材质/UV原生Maya polyUnite、清输出history、居中pivot、删除准确输入叶与孤立的独占poly历史，输出放最多输入所在的完整路径父组。所有原组/无关child保留，不照原临时rename整个层级/删除组/猜短组名；输出SmartCombine_0自动无冲突编号，整组旧名不替换旧group。多个输入父同票按输入顺序，世界级无需访问空父数组。custom_names=False使用Maya生成名。

separate：一个含至少两shell的mesh，native polySeparate并清输出history，输出父组保持，继承原rotate/scale世界pivot分别原值，不原先把两pivot都设rotatePivot；命名源_Sep_1等保留basename的下划线和namespace，唯一名称不覆盖。原单shell、multi-shape、child-transform输入拒绝，避免删不相关子对象。

历史作用域仅从 mesh.inMesh 上游读取，避免 shape 整体 listHistory 经 groupId 材质成员关系走进共享 shadingEngine；必要 polygon/groupParts/groupId 数据节点按消费者验证，材质关系不作为可删除历史。pivot 分别查询 rotatePivot/scalePivot，不依赖组合 pivots 查询顺序。

extract/duplicate：components默认当前face/edge/vertex/UV，明确一个mesh及范围，通过只读转换得到面序号；复制整mesh再删除新mesh未选面，输出仅一个对象即使面不连续，原材质/UV/pivot和parent复制。extract再删源指定面，只支持无引用/实例/变形器的静态poly历史，all-faces extract拒绝避免残留空源；duplicate支持只读已变形rig/引用/实例源，源不写、不删history，独立当前几何副本清掉其自己的中间shape/子transform/history。all-faces duplicate跳过空delete，避免意外删除当前选择。节点UUID检查任何清理均仅新副本，源skin/子控制器不清理。

几何动作custom_names=True；exact整节点/唯一shape/alias/锁/引用/实例按写入权限拒绝，combine/separate/extract仅独占static polygon construction history，外部geometry/history consumer拒绝。duplicate源只读放宽，但新副本可编辑节点才解其自己的lock，不解源锁/引用。输入scene modifier/任意deformer不自动bake原源。validate/dry_run仅场景查询/face转换不改选择/节点/Undo/time/AutoKey。run一个UndoChunk；AutoKey临时关再恢复，操作后选择输出，原选择由Undo恢复，时间不改。失败可能部分创建/改几何，基类不自动回滚，Undo本次并复查。

输出data `{action,inputs,outputs,output_uuids,created_uuids}`，inputs有源/shapeUUID、parent、pivots，geometry不写外部文件。示例`tool.run(action='combine',objects=['|a','|b'],dry_run=True)`成功后同参数run；`tool.run(action='duplicate',components=['|mesh.f[0:2]'])`。

原四row窗口保留Maya内置poly图标（缺则文字button，不复制Autodesk资源），逐操作自定义命名/执行/预检/Shelf/Hotkey，另窗口Shelf和About作者链接。persistent安装仅真实GUI且候选验收/晋级注册后可用；不会整理时写偏好。`shelf` option=0..4、shelf可指定现存layout；`hotkey` option=0..3、key一字母数字、alt/ctrl默认True，仅空闲键可绑定，外源runtime/named碰撞拒绝，不覆盖已有热键。UI明确原不可Undo配置影响与取消默认确认。命令静态引用正式包，不存待整理路径；快捷键/工具架会话配置不受sceneUndo保护，保存/撤销由Maya偏好管理，候选不自动savePrefs。

复用框架Undo/结果，core无同一SmartMesh四操作完整业务，不改core。可先isolate_selected直看几何，但需先恢复其receipt再删除mesh，否则记录失效；FCM Hider集合在删除输入后需要用户核对成员，无自动改集合组合。静态依赖/作用域分析非生产组合实测。

验证：原两文件与完整MEL业务/安装/About来源SHA、Schema/静态安装命令可编译/严格类型；隔离Maya2025真实combine数量/parent/无关对象/材质、separate壳/两个pivot、rigged源duplicate无变/全face/原生extract/一次Undo及锁/错scope/实例/GUI与安装batch拒绝。真实GUI、生产拓扑/UV材质复杂情况、引用/实例只读duplicate与持久安装/其它版本not_run；原许可无明确公开发行授权，不推断。
