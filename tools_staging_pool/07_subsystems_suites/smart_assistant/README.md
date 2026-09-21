# Maya Smart Assistant

## 工具简介

Maya Smart Assistant 是一个智能化的Maya辅助工具，能够自动监测Maya的工作状态，并根据用户习惯优化和调整Maya的设置与文件操作流程。

### 主要功能
1. 储存并应用Maya首选项，实现多环境同步。
2. 智能处理拖拽文件到Maya窗口的行为：
   - 支持ma、mb、fbx、obj、abc等格式，弹窗选择"打开/导入/引用"。
   - 拖拽图片序列文件夹时，自动新建相机并导入序列。
3. 劫持Maya文件对话框，强制默认路径为当前Maya文件所在目录。

---

## 安装方法

1. 将整个 `maya_smart_assistant` 文件夹拷贝到 Maya 的脚本路径下（如 `~/Documents/maya/scripts/`）。
2. 在 Maya 的 Script Editor 中运行：

```python
import maya_smart_assistant.main as msa
msa.launch()
```

3. 可将上述命令添加到自定义菜单或 shelf。

---

## 目录结构说明

```
maya_smart_assistant/
│
├── __init__.py
├── main.py                # 工具主入口，负责UI和功能调度
├── config/
│   ├── __init__.py
│   ├── prefs_manager.py   # 首选项的导入/导出/应用
│   └── config.json        # 用户首选项配置文件
│
├── dragdrop/
│   ├── __init__.py
│   ├── dragdrop_handler.py    # 拖拽事件监听与分发
│   ├── file_actions.py        # 针对不同文件类型的处理逻辑
│   └── camera_imageplane.py   # 创建参考相机及图像平面
│
├── dialogs/
│   ├── __init__.py
│   ├── choose_action_dialog.py    # 选择"打开/导入/引用"的弹窗
│   ├── namespace_dialog.py        # 命名空间输入弹窗
│   └── utils.py                   # 通用对话框工具
│
├── file_dialog_patch/
│   ├── __init__.py
│   └── patch_file_dialog.py   # 劫持/重载文件对话框默认路径
│
├── utils/
│   ├── __init__.py
│   └── path_utils.py          # 路径、文件类型等通用工具
│
├── icons/                     # 可选，存放UI图标
│
└── README.md                  # 安装和使用说明
```

---

## 维护与扩展

- 所有功能均模块化，便于后续维护和扩展。
- 推荐使用git进行版本管理。
- 如需扩展新功能，建议在对应模块下新建py文件并在main.py中注册。 