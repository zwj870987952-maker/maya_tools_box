# Maya 场景记录点与撤销恢复工具 (Maya Undo Checkpoint Tool)

一款轻量、安全、高效的 Maya 操作记录点管理工具。
允许你在操作 Maya 场景时随时创建**操作标记点（记录点）**，在进行多次复杂操作后，一键自动批量 Undo 精确回退到指定记录点。

---

## 📁 脚本列表与说明

| 脚本文件 | 说明 | 适用场景 |
| :--- | :--- | :--- |
| **`create_checkpoint.py`** | **生成记录点（独立脚本）**：插入唯一记录点，已有则直接覆盖。 | 适合绑定快捷键、Shelf 按钮或脚本调用 |
| **`restore_checkpoint.py`** | **恢复记录点（独立脚本）**：批量快速 Undo 精准回到记录点。 | 适合绑定快捷键、Shelf 按钮或脚本调用 |
| **`clear_checkpoints.py`** | **清空记录点（独立脚本）**：清空记录点标记。 | 适合快捷重置 |
| **`maya_undo_checkpoint.py`** | **主程序与 GUI 管理面板**：包含多记录点可视化管理、双击回退等功能。 | 复杂场景多记录点管理 |
| **`install_shelf.py`** | **工具架一键安装脚本**：一键在 Maya 当前 Shelf 上生成 4 个快捷图标按钮。 | 快捷安装配置 |

---

## 🚀 3 个独立脚本的使用方法

### 1. 生成记录点 (`create_checkpoint.py`)
在 Maya Python 中执行以下代码（或将其保存为 Shelf 按钮 / 绑定快捷键）：
```python
import sys
tool_path = r"d:/jiaoben/jiaoben2026/Google/mayaUndo"
if tool_path not in sys.path: sys.path.insert(0, tool_path)

import create_checkpoint
create_checkpoint.main()
```
- **特性**：自动在视口上方显示提示信息。如果之前已有记录点，会自动直接覆盖为最新记录点。

---

### 2. 恢复记录点 (`restore_checkpoint.py`)
在 Maya Python 中执行以下代码：
```python
import sys
tool_path = r"d:/jiaoben/jiaoben2026/Google/mayaUndo"
if tool_path not in sys.path: sys.path.insert(0, tool_path)

import restore_checkpoint
restore_checkpoint.main()
```
- **特性**：自动挂起视口重绘以毫秒级速度批量 Undo，直到精确回到记录点，完成后视口提示共回退了多少步。

---

### 3. 清空记录点 (`clear_checkpoints.py`)
在 Maya Python 中执行以下代码：
```python
import sys
tool_path = r"d:/jiaoben/jiaoben2026/Google/mayaUndo"
if tool_path not in sys.path: sys.path.insert(0, tool_path)

import clear_checkpoints
clear_checkpoints.main()
```

---

## 🛠️ 一键将所有按钮安装到 Maya 工具架 (Shelf)

在 Maya 脚本编辑器中执行：
```python
import sys
tool_path = r"d:/jiaoben/jiaoben2026/Google/mayaUndo"
if tool_path not in sys.path: sys.path.insert(0, tool_path)

import install_shelf
install_shelf.install_to_shelf()
```
运行后，当前 Shelf 会自动生成 4 个彩色标签按钮：
1. **`CP面板`**：打开完整可视化图形面板。
2. **`设记录`**：一键生成/覆盖记录点。
3. **`回记录`**：一键回退到记录点。
4. **`清记录`**：一键清空记录点。
