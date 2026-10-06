# 完整套件入口（Suite UI）

完整面板及媒体插件等补充入口。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `suite.toolbar` | 主工具栏 | `Animo_Data/Animo_Launcher/Animo_Launcher.py` | 完整原生工具栏，含停靠、滑块和工具设置。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.tools_editor` | 工具编辑器 | `Animo_Data/Animo_Launcher/tools_editor_launcher.py` | 搜索工具、配置快捷键与 Shelf。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.vectorify` | 路径重定向 | `Animo_Data/Animo_Launcher/vectorify_launcher.py` | 用临时控制器将动画重新沿路径行进，并可吸附地面。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.multi_camera_playblast` | 多摄像机预览 | `Animo_Data/Animo_Launcher/fast_multi_view_playblaster_launcher.py` | 从多个摄像机输出 Playblast，写入外部媒体文件。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.quick_export_import` | 快速对象导入导出 | `Animo_Data/Animo_Launcher/quick_exporer_launcher.py` | 保存和读取对象资产文件，可能覆盖磁盘文件。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.pickify` | 选择集面板 | `Animo_Data/Animo_Launcher/pickify_launcher.py` | 创建和管理竖排/横排选择集。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.spacify` | 空间工具面板 | `Animo_Data/Animo_Launcher/spacify_launcher.py` | 打开完整临时空间工具面板。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.transify` | 动画传递面板 | `Animo_Data/Animo_Launcher/transify_launcher.py` | 复制、插入、替换动画和姿态，处理命名空间。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.tracify_settings` | 运动弧线设置 | `Animo_Data/Animo_Launcher/tracify_launcher.py` | 管理轨迹颜色、帧范围和摄像机空间。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.tweenify` | 滑块面板 | `Animo_Data/Animo_Launcher/tweenify_launcher.py` | 弹出 19 个滑块的交互界面。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.twosify` | 风格化动画面板 | `Animo_Data/Animo_Launcher/twosify_launcher.py` | 动画层与步进风格配置。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.temp_pivot` | 临时轴心面板 | `Animo_Data/Animo_Launcher/temp_pivot_launcher.py` | 创建并配置临时轴心。；UI、偏好、插件；实际操作还可能写场景或文件 |
| `suite.reference_dropper` | 参考媒体拖放插件 | `Animo_Data/Animo_Reference_Dropper/load_anim_ref_dropper.py` | 加载拖放插件；后续媒体导入可能运行 FFmpeg 并生成图片序列。；UI、偏好、插件；实际操作还可能写场景或文件 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='suite.toolbar')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='suite.toolbar')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
