# Maya 工具箱大模型 (LLM / Agent) 脚本 API 调用速查指南 (LLM Tools Cheatsheet)

本工具箱已完整实现面向 **大模型 Function Calling** 与 **Model Context Protocol (MCP)** 的自动化服务调度规范。大模型可以直接理解工具语义、生成合法的 JSON 参数并通过单行 Python 代码调度任何内置功能。

---

## 1. 大模型统一调用入口 (Unified Dispatcher API)

大模型在生成 Maya 自动化脚本时，**无需关注各个工具具体的内部类名和复杂的导入路径**，统一通过 `maya_toolkit.execute_tool` 进行调度：

```python
import sys
tool_root = r"D:/Users/zhongweijie/Documents/GitHub/maya_tools_box"
if tool_root not in sys.path:
    sys.path.insert(0, tool_root)

import maya_toolkit

# 1. 预检模式 (Dry-Run: 仅参数校验与分析，绝不修改场景)
result_dry = maya_toolkit.execute_tool(
    tool_id="clean_namespaces",
    arguments={"nodes": ["char:head"], "process_all_scene": False},
    dry_run=True
)
print("预检结果:", result_dry.to_dict())

# 2. 正式执行模式 (自动包裹在 Undo Chunk 中，支持 Ctrl+Z)
result = maya_toolkit.execute_tool(
    tool_id="clean_namespaces",
    arguments={"nodes": ["char:head"], "process_all_scene": False},
    dry_run=False
)
print("执行结果:", result.to_dict())
```

---

## 2. 导出标准 Schema (供 Agent 自动发现)

如果您的 AI Agent 或 MCP Server 需要动态注册工具列表，可直接运行：

```python
import maya_toolkit

# 获取 OpenAI Function Calling 规范格式 (用于 GPT / Claude / Gemini Function Calling)
openai_schemas = maya_toolkit.export_tool_schemas(format_type="openai")

# 获取 MCP (Model Context Protocol) Tools 规范格式
mcp_schemas = maya_toolkit.export_tool_schemas(format_type="mcp")
```

---

## 3. 6 大工具 ID、参数定义与调用示例

### ① 命名空间清理工具 (`clean_namespaces`)
- **功能**：清理场景或指定物体的命名空间，支持本地合并到根 `:`，以及顶层引用的安全迁移。
- **参数说明**：
  - `nodes` (`list[str]`, 可选): 要清理命名空间的节点列表。若留空则自动处理视口当前选中的物体。
  - `process_all_scene` (`bool`, 默认 `false`): 是否对全场景所有非系统命名空间执行清理。
- **调用范例**：
  ```python
  maya_toolkit.execute_tool("clean_namespaces", {
      "nodes": ["char:body", "char:armor"],
      "process_all_scene": False
  })
  ```

---

### ② 欧拉旋转 360 度异常跳变修正 (`fix_rotation_winding`)
- **功能**：扫描并消除控制器动画曲线上因 ±360°/±720° 异常阶跃导致的空转，严格保护切线。
- **参数说明**：
  - `nodes` (`list[str]`, 可选): 控制器/骨骼节点列表，留空默认取视口选区。
  - `channels` (`list[str]`, 默认 `["rotateX", "rotateY", "rotateZ"]`): 检测的旋转通道。
  - `tolerance` (`number`, 默认 `90.0`): 判定为 360 度倍数跳变的容差阈值。
  - `time_range` (`list[float]`, 可选): `[start_frame, end_frame]` 限制时间段。
- **调用范例**：
  ```python
  maya_toolkit.execute_tool("fix_rotation_winding", {
      "nodes": ["char_Rig:spine_ctrl", "char_Rig:head_ctrl"],
      "tolerance": 90.0
  })
  ```

---

### ③ 重叠位置顶点蒙皮权重复制 (`copy_overlapping_weights`)
- **功能**：在源对象 A 与目标对象 B 之间，基于空间哈希算法匹配重叠顶点，并将蒙皮权重复制到 B。
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
      "source": "HighMesh_Skinned",
      "target": "LowMesh_Retopo",
      "tolerance": 0.002,
      "auto_bind": True
  })
  ```

---

### ④ 选择集批量导出 FBX (`export_sets_to_fbx`)
- **功能**：将场景中的 objectSet 选择集或指定列表成员批量导出为独立的 FBX 资产。
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
  })
  ```

---

### ⑤ 双列表按行一对一材质传递 (`assign_materials_by_rows`)
- **功能**：将源物体列表（A）的材质分配严格按顺序赋予给目标物体列表（B）。
- **参数说明**：
  - `source_list` (`list[str]`, 必填): 源模型或组列表。
  - `target_list` (`list[str]`, 必填): 目标模型或组列表。
  - `transfer_face_assignments` (`bool`, 默认 `true`): 是否传递分面多材质。
  - `fallback_on_topology_mismatch` (`bool`, 默认 `true`): 拓扑面数不一致时安全降级赋予整物主材质。
- **调用范例**：
  ```python
  maya_toolkit.execute_tool("assign_materials_by_rows", {
      "source_list": ["Hero_High_Grp"],
      "target_list": ["Hero_Low_Grp"],
      "transfer_face_assignments": True,
      "fallback_on_topology_mismatch": True
  })
  ```

---

### ⑥ 外部 FBX 资产深度比对与同步 (`compare_and_sync_fbx`)
- **功能**：纯内存直接读取外部 FBX，比对当前 Maya 场景同名网格的拓扑、材质分面与位姿 (T/R/S)，并选择性同步。
- **参数说明**：
  - `fbx_path` (`str`, 必填): 外部 FBX 文件的绝对路径。
  - `action` (`str`, 默认 `"diff_only"`): `"diff_only"` (仅比对并输出差异结构), `"sync_materials"` (同步材质), `"sync_transforms"` (同步位姿), `"sync_all"` (全部同步)。
  - `match_by_short_name` (`bool`, 默认 `true`): 是否以短名称匹配。
  - `case_insensitive` (`bool`, 默认 `false`): 是否忽略大小写。
  - `target_assets` (`list[str]`, 可选): 指定同步的部分资产，留空则作用于所有检出差异项。
- **调用范例**：
  ```python
  # 步骤 1：仅比对，获取全维度差异分析
  diff_res = maya_toolkit.execute_tool("compare_and_sync_fbx", {
      "fbx_path": "D:/Project/Assets/Boss_V2.fbx",
      "action": "diff_only"
  })
  print("差异摘要:", diff_res.data["summary"])

  # 步骤 2：对检出的差异物体，精准一键同步外部材质
  sync_res = maya_toolkit.execute_tool("compare_and_sync_fbx", {
      "fbx_path": "D:/Project/Assets/Boss_V2.fbx",
      "action": "sync_materials"
  })
  ```
