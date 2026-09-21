# TheKeyMachine 中文补丁

这个补丁用于将TheKeyMachine的英文界面汉化为中文界面，方便中文用户使用。

## 安装说明

### 方法1: 使用安装脚本安装（推荐）

1. 将补丁文件复制到TheKeyMachine的安装目录下
2. 在Maya中打开脚本编辑器（Script Editor）
3. 执行以下Python代码：

```python
import TheKeyMachine.chinese_installer
TheKeyMachine.chinese_installer.install_chinese_patch()
```

4. 补丁将自动安装并重新加载TheKeyMachine工具栏

### 方法2: 手动安装

如果自动安装不成功，可以尝试手动安装：

1. 将补丁文件复制到TheKeyMachine的安装目录下
2. 在Maya中打开脚本编辑器（Script Editor）
3. 执行以下Python代码：

```python
import TheKeyMachine.core.toolbar_patch as patch
patch.apply_chinese_patch()
```

## 恢复英文界面

如果你想恢复为原始的英文界面：

1. 在Maya中打开脚本编辑器（Script Editor）
2. 执行安装代码后，会出现一个对话框
3. 选择"恢复英文"选项

## 补丁文件说明

- `TheKeyMachine/mods/styleMod.py` - 翻译字典，包含界面文本的中文翻译
- `TheKeyMachine/core/toolbar_patch.py` - 补丁主程序，负责替换界面文本
- `TheKeyMachine/chinese_installer.py` - 安装脚本，简化安装过程

## 注意事项

- 首次安装补丁时，会自动备份原始文件，文件名为`toolbar_backup.py`
- 如果安装失败，请检查文件权限，确保有写入权限
- 安装补丁后，如遇到界面显示问题，请重启Maya

## 补丁更新

如需更新补丁，只需重新运行安装脚本即可应用最新版本的补丁。

## 联系方式

如有问题或建议，请联系作者。 