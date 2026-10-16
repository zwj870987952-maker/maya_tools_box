# Maya 工具箱大模型 (LLM / Agent) 脚本 API 调用速查指南 (LLM Tools Cheatsheet)

本工具箱提供统一 Python 调度入口，并可导出 **Function Calling** 与 **MCP Tools** 格式的参数描述。MCP 描述可供外部 MCP 服务端使用；本仓库当前不提供可直接连接的 MCP 服务。工具描述和参数 Schema 帮助大模型选择、调用功能，具体使用条件与影响应结合专项工具文档阅读。

---

## 1. 大模型统一调用入口 (Unified Dispatcher API)

大模型在生成 Maya 自动化脚本时，**无需关注各个工具具体的内部类名和复杂的导入路径**，统一通过 `maya_toolkit.execute_tool` 进行调度：

```python
import sys
tool_root = r"D:/path/to/maya_tools_box"  # 替换为本机仓库路径
if tool_root not in sys.path:
    sys.path.insert(0, tool_root)

import maya_toolkit

# 1. 预检模式（由工具的 validate() 检查，不修改场景）
result_dry = maya_toolkit.execute_tool(
    tool_id="clean_namespaces",
    arguments={"nodes": ["char:head"], "process_all_scene": False},
    dry_run=True
)
print("预检结果:", result_dry.to_dict())

# 2. 已确认操作范围后，仅在预检通过时正式执行
if result_dry.success:
    result = maya_toolkit.execute_tool(
        tool_id="clean_namespaces",
        arguments={"nodes": ["char:head"], "process_all_scene": False},
        dry_run=False
    )
    print("执行结果:", result.to_dict())
```

预检只覆盖工具 `validate()` 已实现的检查，不保证所有业务前提或最终效果。执行后还需查看 `errors`、`warnings`、业务结果与场景实际状态。Undo Chunk 用于分组，不会在失败时自动回滚；文件写入不由 Maya Undo 撤回。

---

## 2. 导出标准 Schema (供 Agent 自动发现)

如果 AI Agent 或 MCP Server 需要工具调用描述，可运行：

```python
import maya_toolkit

# 获取 OpenAI 格式的调用描述；其他服务需按各自接口适配
openai_schemas = maya_toolkit.export_tool_schemas(format_type="openai")

# 获取 MCP (Model Context Protocol) Tools 规范格式
mcp_schemas = maya_toolkit.export_tool_schemas(format_type="mcp")
```

Schema 只描述参数；完整的适用条件、输出、操作影响和组合关系应写入 [工具知识说明](tools/_tool_knowledge_template.md)。当前框架不自动验证传入参数是否满足 Schema，工具必须在 `validate(**kwargs)` 中执行必要检查。

---

## 3. 工具 ID、参数定义与调用示例

已转正：[`advanced_skeleton_animation` — 46个 ADV 动画入口](tools/advanced_skeleton_animation.md)，通过 `maya_toolkit.execute_tool("advanced_skeleton_animation", {"operation": "catalog"})` 获取目录，统一面板已接入。默认发现本机最新 ADV；14个入口仅验证窗口，MocapX 为根命名空间模拟数据驱动验证。检测到 animRescue 时拒绝场景操作；原生粘贴需显式接受清空 Undo 历史。

新增：[`advanced_skeleton_mirror` — ADV 原生 Mirror](tools/advanced_skeleton_mirror.md)。默认调用当前姿态的原生 `asMirror`，不需要额外映射；`action="open_options"` 打开原生选项。逐帧动画扩展使用 `action="mirror_animation"` 与 `time_range=[0, 240]`，仅支持无目标动画层的角色。先阅读专项说明中的实测范围与设键影响。

以下节点名、资产名和路径均为占位示例，应替换为当前任务确认的目标。场景写入示例默认展示 `dry_run=True` 的预检；正式执行遵循第 1 节的流程，使用相同参数并检查实际结果。不要把空列表或省略目标参数当作“什么都不处理”。

### ① 命名空间清理工具 (`clean_namespaces`)
- **功能**：清理场景或指定物体涉及的命名空间，支持本地合并到根 `:`，以及顶层引用命名空间的处理。命名空间操作可能影响其中其他节点；指定节点不等于只重命名该节点。操作后需核对名称冲突、引用状态，并重新定位后续任务目标。
- **参数说明**：
  - `nodes` (`list[str]`, 可选): 要清理命名空间的节点列表。若留空则自动处理视口当前选中的物体。
  - `process_all_scene` (`bool`, 默认 `false`): 是否对全场景所有非系统命名空间执行清理。
- **调用范例**：
  ```python
  maya_toolkit.execute_tool("clean_namespaces", {
      "nodes": ["char:body", "char:armor"],
      "process_all_scene": False
  }, dry_run=True)
  ```

---

### ② 欧拉旋转 360 度异常跳变修正 (`fix_rotation_winding`)
- **功能**：检测并修复旋转曲线的 360 度整数倍异常数值跳变。不能据此保证解决万向锁、约束或动画层等其他原因造成的旋转问题；执行后需检查曲线、切线与实际动作，避免误改有意设计的多圈旋转。
- **参数说明**：
  - `nodes` (`list[str]`, 可选): 控制器/骨骼节点列表，留空默认取视口选区。
  - `channels` (`list[str]`, 默认 `["rotateX", "rotateY", "rotateZ"]`): 检测的旋转通道。
  - `tolerance` (`number`, 默认 `90.0`): 判定为 360 度倍数跳变的容差阈值。
  - `time_range` (`list[float]`, 可选): `[start_frame, end_frame]` 限制时间段。
- **调用范例**：
  ```python
  maya_toolkit.execute_tool("fix_rotation_winding", {
      "nodes": ["char_Rig:spine_ctrl", "char_Rig:head_ctrl"],
      "tolerance": 90.0,
      "time_range": [1, 48]
  }, dry_run=True)
  ```

---

### ③ 重叠位置顶点蒙皮权重复制 (`copy_overlapping_weights`)
- **功能**：在源对象 A 与目标对象 B 之间，基于空间哈希算法匹配重叠顶点，并将蒙皮权重复制到 B。
- **适用边界**：需要在指定空间和容差内存在可匹配的顶点。任意高模与重拓扑低模之间的权重传递不能默认使用本工具；不重叠的情况需另选方法。复制后应核对实际匹配范围及变形效果。
- **参数说明**：
  - `source` (`str`, 必填): 源网格或 Transform 节点（必须具备蒙皮簇）。
  - `target` (`str`, 必填): 目标网格或 Transform 节点。
  - `tolerance` (`number`, 默认 `0.001`): 顶点空间重叠最大距离容差。
  - `space` (`str`, 默认 `"world"`): `"world"` (世界空间) 或 `"object"` (局部空间)。
  - `auto_bind` (`bool`, 默认 `true`): 若目标未蒙皮，是否自动完成骨骼绑定。
  - `add_missing_influences` (`bool`, 默认 `true`): 自动补充目标缺失的影响骨骼。
- **调用范例**：
  ```python
  maya_toolkit.execute_tool("copy_overlapping_weights", {
      "source": "Body_Source_Skinned",
      "target": "Body_Target_Overlapping",
      "tolerance": 0.002,
      "space": "world",
      "auto_bind": True
  }, dry_run=True)
  ```

  示例假定两个网格的待复制顶点在世界空间重叠。`auto_bind=True` 与默认的 `add_missing_influences=True` 可能新增蒙皮绑定或影响骨骼，应符合当前任务范围。

---

### ④ 选择集批量导出 FBX (`export_sets_to_fbx`)
- **功能**：将场景中的 objectSet 选择集或指定列表成员批量导出为独立的 FBX 资产。
- **影响与验收**：导出写入外部文件，不能由 Maya Undo 撤回。明确输出路径和已有文件的处理要求；执行后逐项核对结果及输出文件，不能只凭总状态判断整批导出完成。
- **参数说明**：
  - `export_items` (`list[dict]`, 可选): `[{"set_name": "...", "fbx_name": "...", "export_dir": "..."}]`。若留空则自动读取场景内所有用户选择集。
  - `fbx_options` (`dict`, 可选): 平滑组、骨骼、动画烘焙等导出参数。
- **调用范例**：
  ```python
  maya_toolkit.execute_tool("export_sets_to_fbx", {
      "export_items": [
          {"set_name": "Set_HeroBody", "fbx_name": "HeroBody.fbx", "export_dir": "D:/GameAssets"},
          {"set_name": "Set_Weapons", "fbx_name": "Weapons.fbx", "export_dir": "D:/GameAssets"}
      ],
      "fbx_options": {
          "smoothing_groups": True,
          "skins": True,
          "animation": False
      }
  }, dry_run=True)
  ```

---

### ⑤ 双列表按行一对一材质传递 (`assign_materials_by_rows`)
- **功能**：将源物体列表（A）的材质分配严格按顺序赋予给目标物体列表（B）。
- **参数说明**：
  - `source_list` (`list[str]`, 必填): 源模型或组列表。
  - `target_list` (`list[str]`, 必填): 目标模型或组列表。
  - `transfer_face_assignments` (`bool`, 默认 `true`): 是否传递分面多材质。
  - `fallback_on_topology_mismatch` (`bool`, 默认 `true`): 拓扑面数不一致时回退为整物主材质；回退不保留原分面材质效果，只有任务允许该结果时才启用。
- **调用范例**：
  ```python
  maya_toolkit.execute_tool("assign_materials_by_rows", {
      "source_list": ["Body_Source", "Helmet_Source"],
      "target_list": ["Body_Target", "Helmet_Target"],
      "transfer_face_assignments": True,
      "fallback_on_topology_mismatch": False
  }, dry_run=True)
  ```

  示例假定已确认逐项对应关系及分面传递条件。列表顺序决定源目标配对，面数相同本身不能证明面索引语义一致。

---

### ⑥ 外部 FBX 资产深度比对与同步 (`compare_and_sync_fbx`)
- **功能**：读取外部 FBX，比对当前 Maya 场景中匹配网格的受支持拓扑信息、材质分面与位姿 (T/R/S)，并选择同步目标。读取方式和副作用边界取决于实际引擎，见 [专项说明](tools/fbx_diff_sync_guide.md)。
- **参数说明**：
  - `fbx_path` (`str`, 必填): 外部 FBX 文件的绝对路径。
  - `action` (`str`, 默认 `"diff_only"`): `"diff_only"` (仅比对并输出差异结构), `"sync_materials"` (同步材质), `"sync_transforms"` (同步位姿), `"sync_all"` (全部同步)。
  - `match_by_short_name` (`bool`, 默认 `true`): 是否以短名称匹配。
  - `case_insensitive` (`bool`, 默认 `false`): 是否忽略大小写。
  - `target_assets` (`list[str]`, 可选): 指定同步的部分资产，留空则作用于所有检出差异项。
- **调用范例**：
  ```python
  # 步骤 1：执行比对；diff_only 是业务动作，不等于 dry_run 预检
  diff_res = maya_toolkit.execute_tool("compare_and_sync_fbx", {
      "fbx_path": "D:/Project/Assets/Boss_V2.fbx",
      "action": "diff_only"
  })
  print("比对结果:", diff_res.to_dict())

  # 步骤 2：核对实际匹配结果，将下列占位名称替换为需要同步的资产标识
  # 不要传空列表；省略 target_assets 会扩大到所有检出的差异项
  selected_assets = ["Body_Target", "Helmet_Target"]
  if diff_res.success and not diff_res.errors and selected_assets:
      sync_args = {
          "fbx_path": "D:/Project/Assets/Boss_V2.fbx",
          "action": "sync_materials",
          "target_assets": selected_assets
      }
      sync_preview = maya_toolkit.execute_tool(
          "compare_and_sync_fbx", sync_args, dry_run=True
      )
      print("同步预检:", sync_preview.to_dict())
      # 正式同步按第 1 节流程进行，并核对 warnings 和目标资产的实际结果
  ```

短名称匹配可能遇到不同层级或命名空间中的同名对象；同步前应核对源目标对应关系。比对未发现差异仅表示所检查字段一致，不代表全部几何、贴图网络或最终渲染效果一致。
