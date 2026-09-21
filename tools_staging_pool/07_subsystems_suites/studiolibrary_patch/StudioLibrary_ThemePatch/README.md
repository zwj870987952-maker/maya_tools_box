# Studio Library - Modern Dark 专属主题补丁包 (Theme Patch)

专为 Studio Library 打造的**独立、零侵入式**现代极简暗黑工坊主题包。

---

## ✨ 核心特性

1. **🎨 纯视觉层替换（零功能侵入）**：
   - 仅替换与管理 QSS 样式表与图标/字体等前端美术资源。
   - **完全不改动** Studio Library 的 Python 业务逻辑代码（`mutils`, `library.py`, `libraryitem.py` 等保持 100% 原始代码状态）。
2. **🧩 与拓展包（如 StudioLibrary_PlusPatch）完全独立**：
   - 主题包采用独立的安装与卸载脚本（`install_theme.py` / `uninstall_theme.py`）。
   - 样式规则基于 Qt 基础类与标准控件名选择器，能**自动兼容并美化 PlusPatch 所新增的 UI 控件**，且双方文件互不冲突，各自升级维护不受任何影响。
3. **⚡ 智能热重载与安全备份**：
   - 首次安装自动备份原始 `default.css.orig_backup`。
   - 在 Maya 中运行安装器时，会自动触发当前运行界面的即时热刷新，无需重启 Maya。

---

## 🚀 安装与使用方式

### 方式一：在 Maya 脚本编辑器 (Python) 中一键运行

```python
import sys
# 将主题包路径加入 sys.path (按实际路径修改)
sys.path.append(r"d:\jiaoben\jiaoben2026\Google\studiolibrary-main\StudioLibrary_ThemePatch")

import install_theme
install_theme.install()
```

### 方式二：命令行或外部 Python 安装

在 `StudioLibrary_ThemePatch` 目录下运行：
```bash
python install_theme.py
```

---

## 🔄 一键卸载与恢复官方默认

在 Maya 或命令行中运行：
```python
import uninstall_theme
uninstall_theme.uninstall()
```
即可安全还原为官方原始主题与样式。
