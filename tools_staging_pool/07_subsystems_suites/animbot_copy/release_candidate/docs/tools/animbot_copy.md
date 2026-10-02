# animBot Copy 工具栏与Workspace UI原型候选

原项目是自有UI复刻原型，完整主/Graph Editor工具栏、QPainter图标、右键预设菜单、各滑杆回弹/模式切换防重、独立main/graph配置、Workspace多列库/工具勾选、新预设、原子换行、左右居中/单行拖动滚轮、边缘大小调整和workspaceControl停靠均保留。源README声称动画工具库完整，但按钮与大多数菜单没有动画业务回调；本候选明确不提供烘焙、姿态复制、Mirror、Ease算法等，不把UI标签当可调用动画能力。原始源码与全部screenshots完整SHA归档，旧截图仅历史参考，不是本轮验收证据。来源未提供LICENSE，不推定第三方图标授权；候选使用自带完整程序绘图fallback，不读取原硬编码机器路径/商业安装，也不下载第三方素材。

AnimBotCopyTool继承Base/ToolResult/animation/JSON Schema，默认inspect给出current_preset、main/graph configs、preset_names和animation_algorithms_implemented=false。action configure配toolbar/config（active_tools精确已知唯一id、alignment left/center/right、single_row严格bool、location匹配main/graph选项），apply_preset/preset整套只在预检全部通过后更新；show_ui/floating、attach_graph_editor、open_workspace、close需真实Maya GUI主线程。dry_run/validate不import Qt、不开窗、不改配置、场景或文件，源码库常量在构建时提取到本地library.json。run专门用于UI/session配置，不开Undo chunk/不初始化Maya，不伪造scene Undo；配置不会由Maya Undo恢复，重新apply_preset可还原布局。全close清理自有三窗口/Graph Editor插入控件，配置仍驻session；Maya退出丢失，新workspace只存内存，不自动保存偏好/场景。

```python
from maya_toolkit.tools.animbot_copy import AnimBotCopyTool
tool=AnimBotCopyTool()
tool.run(dry_run=True, action='apply_preset', preset='Expert')
tool.run(action='configure', toolbar='main', config={'alignment':'right','single_row':True})
tool.show_ui()
tool.run(action='attach_graph_editor')
tool.run(action='open_workspace')
tool.run(action='close')
```

完整UI搬入自有native子包，relative imports无临时目录依赖；取消原每次launch广泛reload吞异常/重置配置。PySide6/shiboken6优先，PySide2/shiboken2 fallback，未保证所有老版本枚举/平台事件可用。singleton信号改bound Qt Slot，避免lambda保留已delete控件；自有UI对象名前缀MTB，与原独立脚本不混淆。关闭恢复记录的单独tab可见性/高度，不改多tab共享Maya样式；原会遍历祖先隐藏所有tab/改祖先高度，候选只隐藏唯一tab，多个共用tab可保留tabbar。原Viewport位置仍以TimeSlider映射，不承诺真实viewport上/下另有停靠；不同Maya面板控制名称/可关闭Graph Editor布局需实测。配置preset支持英文字对齐，修正原自建right/left预设被当center。新预设不覆盖已存在名称。

动画核心逻辑实际不存在，不能复用现有core几何/anim算法而声称补齐；共享Base/ToolResult并保持UI专用样式，无正式core修改。mayapy/offscreen构造和纯配置检查只验证有限功能，不算真实Maya docking、鼠标/滚轮、尺寸、menu、GUI验收。其UI工具标签不能作为其他动画候选的可组合API；可组合部分只有Workspace配置。真实验收通过后已有完整代码/资源/文档/tests/注册promotion，当前全部留在待整理池。
