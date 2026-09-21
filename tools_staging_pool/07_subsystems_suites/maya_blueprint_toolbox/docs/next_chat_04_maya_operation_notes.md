# 新聊天交接：第四类 Maya 操作节点

这份文档给新聊天直接阅读，用来继续设计和实现第四类节点。

当前项目路径：

```text
D:\jiaoben\maya_blueprint_toolbox
```

注意：本目录即包根目录（`core/`、`maya_api/`、`ui/` 直接位于其下），且当前目录不是 git 仓库。如需版本管理，先 `git init` 并提交现状；文档中旧的 GitHub 推送记录对应历史副本 `D:\Users\zhongweijie\Documents\maya蓝图工具`，不适用于本目录。

用户要求：

- 不需要 Codex 调用 Maya。
- 只需要产出脚本和项目文件，用户会自己在 Maya 里执行测试。
- UI 使用中文，方便用户检查。
- 节点规则必须符合 Maya 操作习惯，不要按代码文件或 Maya 菜单机械分类。

## 当前工作进度

已完成的内容：

- 画布 UI（拖动、连线、搜索、分类菜单、平移缩放、属性面板）
- 保存 / 加载工作流 JSON
- 运行选中节点上游流程 / 未选中时运行全部，支持多次运行
- 节点头部颜色按功能类型区分，端口和连线颜色按数据类型区分
- 第一类：常量（文本、数字、布尔、路径）
- 第二类：数据获取（含快捷获取、属性读取、动画时间、通道栏）
- 第三类：数据转换（节点列表 / 属性引用列表成对工具、创建属性引用、变换通道）
- 第四类：Maya 操作首批（选择、重命名、打组、删除、设置属性、四种约束、导入文件、导出 FBX）
- 动画工作流首批：复制帧（含 JSON 输出与直接粘贴打关键帧）
- 调试节点：打印结果

## 已有节点类型规则

通用规则文档：

```text
docs/node_type_rules.md
```

已有类型文档：

```text
docs/node_types/01_constant.md
docs/node_types/02_data_get.md
docs/node_types/03_data_transform.md
```

功能类型颜色：

| 类型 | 颜色 | 含义 |
| --- | --- | --- |
| 常量 | `#4EA1FF` | 只提供固定值 |
| 数据获取 | `#38C7C7` | 读取 Maya 或环境，不修改 Maya |
| 数据转换 | `#9B6DFF` | 整理输入数据，不读取 Maya，不修改 Maya |
| Maya 操作 | `#F2994A` | 会修改 Maya 场景、选择、文件或外部结果 |
| 流程控制 | `#F2C94C` | 控制执行顺序、条件、循环 |
| 调试 / 报告 | `#7FB069` | 输出、检查、报告、预览数据 |

## 第四类节点定义

第四类建议正式命名为：

```text
Maya 操作
```

它的边界：

- 可以修改 Maya 场景。
- 可以修改当前选择。
- 可以创建、删除、重命名、分组、约束对象。
- 可以设置属性。
- 可以导入 / 引用 / 导出文件。
- 可以产生外部文件结果。
- 必须使用统一 `maya_api` 包装函数，不要在 `executor.py` 里直接写大量 `cmds` 逻辑。

不属于第四类的情况：

- 只读取 Maya，不修改 Maya：放到“数据获取”。
- 只整理输入数据，不读不改 Maya：放到“数据转换”。
- 只打印或显示数据：放到“调试 / 报告”。
- 控制条件、循环、分支：以后放到“流程控制”。

## 实现位置

路径均相对包根目录 `D:\jiaoben\maya_blueprint_toolbox`。

新增节点规格：

```text
core/node_specs.py
```

新增执行分发：

```text
core/executor.py
```

Maya 操作封装：

```text
maya_api/
```

已有可复用模块：

```text
maya_api/scene_nodes.py
maya_api/attributes.py
maya_api/constraints.py
maya_api/io.py
maya_api/export.py
maya_api/selection.py
```

如果新增操作类型，优先放进已有模块。只有边界明显不合适时再新增模块。

## Maya 操作节点必须遵守的规则

1. 会改 Maya 的函数必须尽量用 `UndoChunk` 包起来。
2. 输入节点必须验证存在性。
3. 不要隐式依赖当前选择，除非节点本身名字就是“选择相关”。
4. 如果会改变当前选择，要在说明里明确。
5. 文件导入、导出、设置属性、删除节点等危险操作要有清楚参数。
6. 错误要抛出 `MayaApiError`，由 executor 转成 `WorkflowExecutionError`。
7. 操作完成要 `print` 简洁结果，方便 Maya Script Editor 检查。
8. 节点 UI 参数必须中文。
9. 端口类型要明确，不要滥用 `ANY`。`ANY` 目前只给调试 / 报告节点用。
10. 代码要兼容 Maya 的 Python 环境，不依赖系统 Python，不引入第三方库。

## 已有第四类节点

当前已有这些 Maya 操作节点：

| 节点 | 类型 ID | 说明 |
| --- | --- | --- |
| 选择节点 | `maya.selection.select_nodes` | 修改 Maya 当前选择 |
| 设置属性 | `maya.attributes.set` | 设置属性引用列表的值 |
| 重命名节点 | `maya.nodes.rename` | 批量重命名 |
| 打组节点 | `maya.nodes.group` | 创建组 |
| 删除节点 | `maya.nodes.delete` | 删除节点 |
| 父子约束 | `maya.constraints.parent` | 创建 parentConstraint |
| 点约束 | `maya.constraints.point` | 创建 pointConstraint |
| 方向约束 | `maya.constraints.orient` | 创建 orientConstraint |
| 缩放约束 | `maya.constraints.scale` | 创建 scaleConstraint |
| 导入文件 | `maya.io.import_file` | 导入或引用文件 |
| 导出 FBX | `maya.io.export_fbx` | 导出 FBX |

## 第四类下一步建议节点

建议不要一口气做太多。先补最常用、最能和前面三类组成工作流的节点。

第一批推荐：

| 节点 | 输入 | 输出 | 说明 |
| --- | --- | --- | --- |
| 复制节点 | `节点: NODE_LIST` | `节点: NODE_LIST` | duplicate 输入节点，输出复制结果 |
| 父子层级设置 | `子节点: NODE_LIST`、`父节点: NODE_LIST` | `节点: NODE_LIST` | parent 到指定父对象下 |
| 解除父子层级 | `节点: NODE_LIST` | `节点: NODE_LIST` | parent 到 world |
| 冻结变换 | `节点: NODE_LIST` | `节点: NODE_LIST` | makeIdentity |
| 删除历史 | `节点: NODE_LIST` | `节点: NODE_LIST` | delete construction history |
| 居中轴心 | `节点: NODE_LIST` | `节点: NODE_LIST` | xform center pivots |

第二批推荐：

| 节点 | 输入 | 输出 | 说明 |
| --- | --- | --- | --- |
| 创建空组 | 可选名称 / 父节点 | `节点: NODE_LIST` | 创建空 transform group |
| 创建 Locator | 可选名称 / 位置 | `节点: NODE_LIST` | 创建 locator |
| 匹配变换 | `源节点: NODE_LIST`、`目标节点: NODE_LIST` | `节点: NODE_LIST` | 将目标匹配到源 |
| 连接属性 | `源属性: ATTR_LIST`、`目标属性: ATTR_LIST` | 无或报告 | connectAttr |
| 断开属性连接 | `属性: ATTR_LIST` | 无或报告 | disconnectAttr |
| 添加自定义属性 | `节点: NODE_LIST`、属性参数 | `属性引用: ATTR_LIST` | addAttr |

## 第四类节点设计注意点

### 复制节点

建议参数：

- `rename_children: bool`
- `input_connections: bool`
- `upstream_nodes: bool`

但第一版可以保守，只做简单 duplicate，避免复制依赖网络太复杂。

### 父子层级设置

Maya 习惯是：

```text
选中 child，再选 parent，然后 parent
```

蓝图节点里应更明确：

```text
子节点: NODE_LIST
父节点: NODE_LIST
```

如果父节点列表有多个，第一版建议只用第一个父节点。

### 冻结变换

建议参数：

- `translate: bool`
- `rotate: bool`
- `scale: bool`
- `normal: bool`

默认可以是：

```text
translate=False
rotate=True
scale=True
normal=False
```

是否默认冻结位移需要谨慎，因为 Maya 里冻结位移可能不符合 rig / layout 使用习惯。

### 删除历史

这是会修改场景的操作，不是“获取历史节点”。

节点名建议：

```text
删除历史
```

不要叫“获取历史节点”。

### 连接属性

输入应使用 `ATTR_LIST`，不要让用户手写 `node.attr`。

第一版规则：

- 源属性数量为 1，目标属性可以多个：一个源连多个目标。
- 源属性数量和目标属性数量相同：一一连接。
- 其他数量组合报错。

参数建议：

- `force: bool`

## 不要做的事

- 不要在第四类里做“按类型获取节点”。
- 不要在第四类里做“获取 Shape / 获取 SkinCluster / 获取材质”。
- 不要让 Maya 操作节点偷偷读取当前选择。
- 不要把 `cmds` 操作散落在 `executor.py`。
- 不要引入第三方库。
- 不要自动运行 Maya。
- 不要提交或删除无关文件。

## 测试建议

每新增一批第四类节点，建议同时生成一个测试工作流：

```text
examples/workflows/xxx_test.json
```

测试流程应该尽量用到：

- 常量节点
- 数据获取节点
- 数据转换节点
- 新增 Maya 操作节点
- 打印结果节点

例如复制节点测试：

```text
当前选择
-> 去重节点列表
-> 复制节点
-> 打印结果
```

例如连接属性测试：

```text
节点名称 / 当前选择
-> 创建属性引用
-> 连接属性
-> 打印结果
```

## 新聊天开始时建议先做的事

1. 读取本文件。
2. 读取 `docs/node_type_rules.md`。
3. 读取 `docs/node_types/03_data_transform.md`，理解第三类边界。
4. 确认目录是否已 `git init`；若已初始化，用 `git status --short` 检查未提交改动。
5. 先和用户确认第四类下一批要做哪些节点，再动代码。

## 当前优先建议

如果用户没有指定第四类第一批节点，推荐先做：

1. 复制节点
2. 父子层级设置
3. 解除父子层级
4. 冻结变换
5. 删除历史
6. 居中轴心

这 6 个最符合 Maya 日常操作习惯，也最容易和前面三类节点组成可测试工作流。
