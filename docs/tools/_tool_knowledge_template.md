# TOOL_NAME

> 将本文件复制为 docs/tools/TOOL_ID.md。大写占位词由实际工具信息替换。此文档供人和大模型查阅；当前框架不会自动解析本文件。

## 身份与用途

- tool_id：TOOL_ID
- category：DOMAIN_KEY（六大业务领域之一）
- version：VERSION
- 状态：STATUS（待整理 / Maya 已直验 / 已转正）
- 一句话用途：PURPOSE
- 适用场景：USE_CASES
- 不适用场景：EXCLUSIONS

## 调用前提

- Maya 与 Python 实测版本：VERIFIED_VERSIONS
- 必需插件、场景节点或选择：PREREQUISITES
- 输入文件或输出目录条件：FILE_CONDITIONS

## API

调用入口：maya_toolkit.execute_tool("TOOL_ID", arguments={...}, dry_run=True/False)

| 参数 | 类型 | 必填 | 默认值 | 含义与限制 |
| --- | --- | --- | --- | --- |
| PARAMETER_NAME | TYPE | 是/否 | DEFAULT | DESCRIPTION |

### dry_run 会检查什么

写出实际检查的条件；不得写成尚未实现的保证。

### 返回结果

| data 字段 | 类型 | 含义 |
| --- | --- | --- |
| DATA_FIELD | TYPE | DESCRIPTION |

错误与警告：列出常见情况及含义。

## 操作影响与恢复

- 修改的 Maya 场景内容：列出或写“无”。
- 写入、覆盖或导出的文件：列出或写“无”。
- Maya Undo 可撤销的范围：准确描述。
- 失败时可能留下的状态与处理方法：准确描述。

## 调用示例

~~~python
import maya_toolkit

arguments = {}
preview = maya_toolkit.execute_tool("TOOL_ID", arguments, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("TOOL_ID", arguments)
    print(result.to_dict())
~~~

## 关联与组合

| 前置/后续 tool_id | 关系 | 传递的数据 | 顺序或条件 |
| --- | --- | --- | --- |
| RELATED_TOOL_ID | 前置/后续 | DATA_OR_SCENE_STATE | CONDITION |

## Maya 直验记录与已知限制

| Maya 版本 | 验证日期 | 场景与操作 | 结果 |
| --- | --- | --- | --- |
| MAYA_VERSION | DATE | STEPS | 通过/未通过 |

已知限制：列出或写“暂无记录”。
