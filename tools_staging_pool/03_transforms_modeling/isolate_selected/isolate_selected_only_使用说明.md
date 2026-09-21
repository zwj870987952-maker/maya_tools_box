# Maya工具 - 只显示选中物体(不含子层级)

## 功能说明

这个工具可以帮助你在Maya中只显示当前选中的物体本身,而不会显示其子层级下的物体。这在处理复杂层级结构时非常有用。

## 主要功能

1. **只显示选中物体(不含子物体)** - 隔离显示选中的物体,同时隐藏所有子物体
2. **恢复显示所有物体** - 关闭隔离模式并恢复所有物体的可见性

## 使用方法

### 方法一: 使用UI界面

1. 在Maya的Script Editor中执行以下代码:

```python
import sys
sys.path.append(r'd:\jiaoben')
import isolate_selected_only
isolate_selected_only.main()
```

2. 会弹出一个工具窗口,包含两个按钮:
   - **只显示选中物体(不含子物体)**: 点击后隔离显示选中的物体
   - **恢复显示所有物体**: 点击后恢复正常显示

### 方法二: 直接调用函数

如果你只想快速执行,可以在Script Editor中运行:

```python
import sys
sys.path.append(r'd:\jiaoben')
import isolate_selected_only

# 只显示选中的物体(不含子物体)
isolate_selected_only.isolate_selected_only()

# 恢复所有物体的可见性
# isolate_selected_only.restore_visibility()
```

### 方法三: 添加到Maya工具架

1. 打开Maya的Script Editor
2. 在Python标签页中输入以下代码:

```python
import sys
if r'd:\jiaoben' not in sys.path:
    sys.path.append(r'd:\jiaoben')
import isolate_selected_only
isolate_selected_only.main()
```

3. 选中这段代码
4. 按住鼠标中键(滚轮)拖动到工具架上
5. 以后只需点击工具架上的按钮即可快速启动

## 使用步骤

1. 在Maya场景中选择你想要隔离显示的物体
2. 运行工具或点击"只显示选中物体(不含子物体)"按钮
3. 工具会:
   - 隐藏选中物体下的所有子物体
   - 开启视图的隔离显示模式
   - 只显示你选中的物体本身
4. 当需要恢复时,点击"恢复显示所有物体"按钮

## 应用场景

- 当你有一个复杂的父物体,但只想看到父物体本身的形状
- 处理带有大量子物体的群组时,只想看到群组节点
- 在调整父物体的变换时,不想被子物体干扰
- 检查父物体的属性或连接,而不需要看到整个层级结构

## 注意事项

1. 此工具会暂时隐藏子物体的可见性
2. 使用"恢复显示所有物体"功能会恢复所有物体的可见性
3. 工具自动在当前激活的视图面板中工作
4. 如果没有选中物体,会提示"请先选择要隔离显示的物体!"

## 技术特点

- 自动检测当前激活的视图面板
- 智能处理物体的长名称和短名称
- 安全的错误处理机制
- 支持多个物体同时隔离显示
- 完整的可见性恢复功能

## 版本信息

- 版本: 1.0
- 兼容Maya版本: 2017及以上
- 语言: Python 2.7 / Python 3.x

---

如有问题或建议,欢迎反馈!
