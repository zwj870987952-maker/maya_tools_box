# fix_rotation_winding (欧拉旋转360度跳变修正工具)

## 身份与用途

- tool_id: fix_rotation_winding
- category: animation (动画与动作)
- version: 1.2.0
- 状态: 已转正
- 一句话用途: 自动扫描并消除 Maya 控制器旋转曲线上因 360 度跳变造成的空转与插值阶跃。
- 适用场景: 欧拉角翻转 (Euler Flip)、动捕数据重定向后曲线跳变、烘焙动画修复。
- 不适用场景: 真实需要多圈连续旋转的特技动作或陀螺运动。

## 调用前提

- Maya 与 Python 实测版本: Maya 2023 / 2024 / 2025 (Python 3.9+)
- 必需插件、场景节点或选择: 目标节点需具有可打帧的旋转曲线 (`animCurveTA`)。

## API

调用入口: `maya_toolkit.execute_tool("fix_rotation_winding", arguments={...}, dry_run=True/False)`

| 参数 | 类型 | 必填 | 默认值 | 含义与限制 |
| --- | --- | --- | --- | --- |
| nodes | array[string] | 否 | [] (当前选中) | 目标 Transform 节点列表。 |
| channels | array[string] | 否 | ["rotateX", "rotateY", "rotateZ"] | 需要检测与修整的轴向。 |
| tolerance | number | 否 | 180.0 | 判定为 360 度跳变的角度阶跃阈值。 |
| time_range | array[number] | 否 | None (全时间轴) | 起始与结束帧范围 `[start, end]`。 |

### dry_run 会检查什么

- 只读扫描动画曲线的关键帧，识别所有产生 360° 跳跃的关键帧时间与建议偏移量，不修改曲线数据。

### 返回结果

- data 字段包含: `scanned_nodes`, `curves_fixed`, `keys_adjusted`。

## 操作影响与恢复

- 修改的 Maya 场景内容: 目标动画曲线的值被平移 360° 整数倍，严格保持切线连续性。
- 写入、覆盖或导出的文件: 无。
- Maya Undo 可撤销的范围: 单步 Undo 完全还原关键帧数值。

## 调用示例

```python
import maya_toolkit

args = {"nodes": ["ctrl_arm_L"], "channels": ["rotateX", "rotateY"]}
preview = maya_toolkit.execute_tool("fix_rotation_winding", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("fix_rotation_winding", args)
    print(result.to_dict())
```
