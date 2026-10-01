# 世界坐标复制还原 V4 候选

`world_transform_v4`，领域 `modeling_surfacing`。原用户单文件完整归档，catalog 记录逐文件 SHA；源码未附授权声明，不推断再分发许可。候选保留完整原生窗口、两尝试数滑条、只处理关键帧选项、复制/粘贴按钮、Channel Box 提示和进度显示。

复制的是一个时刻的世界位移/Euler旋转快照；不是复制动画曲线，不复制 scale、pivot、jointOrient、rotateAxis 或父子关系。粘贴在每个目标帧恢复同一份世界姿态，并给所选组的三个轴设置关键帧。同场景 UUID 对象可重命名、改父路径；不得把旧路径同名新对象误当原对象。只有副本身份匹配的 live transform/joint 可写，无选择时处理全部仍存在对象；有选择时所有选中对象必须包含在快照内。父级先于子级，全部行预检后写入。

## API 输入与预检

- `action=inspect` 默认只读当前对象，返回 snapshot。`copy` 在内存中保存 snapshot，模块导入不开窗。`paste` 读取传入 snapshot 或内存副本。
- `objects` 可指定唯一整体 transform/joint，否则使用当前选择；shape、组件、模式、重名歧义、别名重复、真实 DAG 实例拒绝。
- snapshot 精确格式 `{version:1, linear_unit, angle_unit, rows:[{uuid,path,pos:[x,y,z],rot:[x,y,z],rotate_order}]}`。UUID、有限数、行数、单位、字段严格校验。当前线性/角度单位必须与副本一致，rotateOrder 必须与复制时一致，避免隐式转换造成错位。
- `channels=both|translate|rotate`；Channel Box 中 tx/translateX 等任一位移轴会选择完整位移组，rx/rotateX 等选完整旋转组；无选择或只选其它属性时 both。API 不隐式读取界面。
- `start/end` 显式、包含端点；不传只处理当前时刻（可小数）。UI 使用真实全局时间滑块且仅在高亮可见时取范围，将 Maya 排他末端转包含末端。不会将无高亮的滑块单帧误认作范围。
- `only_keyframes=False` 逐整数帧；True 只取被处理组的已有 key 的联合，小数 key 不丢失。范围内无 key 保留原当前帧 fallback 并返回警告。范围<=10000帧，帧×对象<=100000。
- `max_attempts=10`、`full_check_attempts=5`，整数1..50。前N轮完整检查，后续可先检查位移，但每个成功退出及最终一轮总是完整检查旋转，失败明确返回错误，不再静默宣称已还原。位置容差0.01当前线性单位、旋转容差0.01度等值；归一化角差修复±180边界。
- 写入拒绝引用、节点/TRS/子轴锁、非keyable轴、非identity OPM、shear、反射/零scale、约束/层/复杂驱动。仅支持可编辑且 output 独占目标轴、采用 Maya 隐式当前时间或 time1.outTime/unwarpedTime 的直接 animCurveTL/TA；全目标、全采样帧链预检不改时间、不创建key。JO/nonXYZ采用 Maya 原生 xform，不另造矩阵算法。
- `save/load` 才使用 `path`（绝对 .json）。save 读取传入或内存快照，独占创建文件，不覆盖旧文件；load 仅读有限8MiB规则JSON并校验，不执行代码，不自动读取原共享临时JSON。无任意pickle或eval。dry_run 不写文件、不改变内存副本。

## 输出与影响

inspect/copy/load 返回 `data.snapshot`；save 返回 path/snapshot。paste dry 返回 objects/attributes/frames；成功返回已处理 frames 和 cancelled=False。失败/取消明确错误，已经执行的帧或当前帧部分写入留在一次 Base Undo chunk，可一次撤销；框架异常不自动回滚。选择保持，时间和 AutoKey 在 finally 恢复；不改时间单位、选择模式、父关系。已有key范围外值保持，范围内key会替换所选轴，可能改变插值/切线，非复制原动画切线。文件、内存clipboard和UI状态不由scene Undo撤销。进度取消仅交互GUI，batch不造UI。

```python
from maya_toolkit.tools.world_transform_v4 import WorldTransformV4Tool
t=WorldTransformV4Tool()
saved=t.run(action='copy',objects=['controlA']).data['snapshot']
preview=t.run(dry_run=True,action='paste',snapshot=saved,objects=['controlA'],channels='translate',start=1,end=24)
if preview.success:
    result=t.run(action='paste',snapshot=saved,objects=['controlA'],channels='translate',start=1,end=24)
```

组合候选：`eblabs_world_space_tools` 用于不同空间动画处理；此工具提供单一姿态恢复，传递 snapshot/UUID，不把它当完整轨迹。可先用 `hierarchy_analyzer` 检视父关系，再复制/重排同场景对象/粘贴；上述联用未做真实GUI组合验收。复用现有 BaseMayaTool/ToolResult/UndoChunk，不重复新增 core；现有 weights/material/export工具无重复单姿态恢复能力。

## 验证与晋级

离线解析、archive/Schema/参数测试、临时正式布局注册和可用 Maya2025隔离检查见 manifest；真实GUI/Channel Box/高亮/取消/生产骨架复杂pivot和跨版本仍 not_run，prepared_unverified。promotion.json及单次晋级脚本已预备，注册与面板来自实际 ALL_TOOL_CLASSES。人工通过前留在 staging。相较原稿变化：不默认覆盖系统temp；时间范围由可见高亮判定；快照UUID/单位防错；选择坏行全表拒绝；关键帧仅对应轴；异常finally恢复；没有收敛的帧不写key、不报成功；没有原共享JSON自动降级读取。需集中验收确认这些明确行为变化。
