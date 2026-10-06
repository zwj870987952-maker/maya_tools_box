# 相对变换关系（Xform Relationships）

记录并应用对象之间的变换关系，可烘焙区间。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `xform_relationships.bake_xform_relationship_range_38be5d93` | Bake XForm Relationship Range | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Bake XForm Relationship.py` | 相对变换关系：Bake XForm Relationship Range。记录并应用对象之间的变换关系，可烘焙区间。；变换、关键帧或缓存文件 |
| `xform_relationships.copy_xform_relationship_169bff4b` | Copy XForm Relationship | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Copy XForm Relationship.py` | 相对变换关系：Copy XForm Relationship。记录并应用对象之间的变换关系，可烘焙区间。；变换、关键帧或缓存文件 |
| `xform_relationships.paste_xform_relationship_455b895c` | Paste XForm Relationship | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Paste XForm Relationship.py` | 相对变换关系：Paste XForm Relationship。记录并应用对象之间的变换关系，可烘焙区间。；变换、关键帧或缓存文件 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='xform_relationships.bake_xform_relationship_range_38be5d93')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='xform_relationships.bake_xform_relationship_range_38be5d93')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
