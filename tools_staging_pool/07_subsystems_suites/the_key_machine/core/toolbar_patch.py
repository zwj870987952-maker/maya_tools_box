"""
TheKeyMachine 中文化补丁程序

此补丁文件将原始的英文界面替换为中文界面。
使用方法：
1. 将此文件放在TheKeyMachine/core目录下
2. 在Maya中运行以下代码：
   import TheKeyMachine.core.toolbar_patch as patch
   patch.apply_chinese_patch()
"""

import os
import re
import maya.cmds as cmds
import maya.mel as mel
import importlib

# 导入翻译字典
import TheKeyMachine.mods.styleMod as style

def apply_chinese_patch():
    """应用中文补丁到TheKeyMachine工具"""
    try:
        # 导入必要的模块
        import TheKeyMachine.core.toolbar as toolbar
        import TheKeyMachine.mods.generalMod as general
        from TheKeyMachine.mods.generalMod import config
        
        # 获取安装路径
        INSTALL_PATH = config["INSTALL_PATH"]
        
        # 备份原始文件
        original_file = os.path.join(INSTALL_PATH, "TheKeyMachine/core/toolbar.py")
        backup_file = os.path.join(INSTALL_PATH, "TheKeyMachine/core/toolbar_backup.py")
        
        if not os.path.exists(backup_file):
            # 如果备份不存在，创建备份
            with open(original_file, 'r', encoding='utf-8') as src:
                content = src.read()
                with open(backup_file, 'w', encoding='utf-8') as dest:
                    dest.write(content)
            
            # 修改原始文件中的文本标签
            patch_toolbar_file(original_file)
            
            # 重新加载界面
            import TheKeyMachine
            reload_toolbar()
            
            # 提示完成
            cmds.confirmDialog(title='成功', message='中文化补丁已成功应用！\n重新加载界面后即可生效。', button=['确定'])
        else:
            # 已经安装过补丁，询问是否重新安装
            result = cmds.confirmDialog(
                title='提示', 
                message='中文化补丁已安装过。\n点击"重新安装"将重新应用补丁\n点击"恢复英文"将恢复为英文界面', 
                button=['重新安装', '恢复英文', '取消'], 
                defaultButton='重新安装',
                cancelButton='取消',
                dismissString='取消'
            )
            
            if result == '重新安装':
                patch_toolbar_file(original_file)
                reload_toolbar()
                cmds.confirmDialog(title='成功', message='中文化补丁已重新应用！', button=['确定'])
            elif result == '恢复英文':
                # 恢复英文界面
                with open(backup_file, 'r', encoding='utf-8') as src:
                    content = src.read()
                    with open(original_file, 'w', encoding='utf-8') as dest:
                        dest.write(content)
                reload_toolbar()
                cmds.confirmDialog(title='成功', message='已恢复为英文界面！', button=['确定'])
    except Exception as e:
        cmds.confirmDialog(title='错误', message=f'应用补丁时出错：\n{str(e)}', button=['确定'])

def patch_toolbar_file(file_path):
    """对toolbar.py文件应用中文补丁"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 添加翻译函数的导入
        if "from TheKeyMachine.mods.styleMod import translate" not in content:
            import_section = "import TheKeyMachine.mods.styleMod as style"
            translated_import = import_section + "\nfrom TheKeyMachine.mods.styleMod import translate"
            content = content.replace(import_section, translated_import)
        
        # 替换菜单项标签
        content = patch_labels(content)
        
        # 替换按钮标签
        content = patch_button_labels(content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True
    except Exception as e:
        cmds.warning(f"修改文件时出错: {str(e)}")
        return False

def patch_labels(content):
    """将标签文本替换为中文"""
    # 替换 cmds.menuItem(label="English Text", ...) 格式的标签
    pattern = r'cmds\.menuItem\(label="([^"]+)"'
    
    def replace_label(match):
        original_text = match.group(1)
        translated_text = f'translate("{original_text}")'
        return f'cmds.menuItem(label={translated_text}'
    
    content = re.sub(pattern, replace_label, content)
    
    # 替换 cmds.menuItem(l="English Text", ...) 格式的标签
    pattern = r'cmds\.menuItem\(l="([^"]+)"'
    
    def replace_l_label(match):
        original_text = match.group(1)
        translated_text = f'translate("{original_text}")'
        return f'cmds.menuItem(l={translated_text}'
    
    content = re.sub(pattern, replace_l_label, content)
    
    return content

def patch_button_labels(content):
    """将按钮标签替换为中文"""
    # 替换 cmds.button(label="English Text", ...) 格式的标签
    pattern = r'cmds\.button\(label="([^"]+)"'
    
    def replace_button_label(match):
        original_text = match.group(1)
        translated_text = f'translate("{original_text}")'
        return f'cmds.button(label={translated_text}'
    
    content = re.sub(pattern, replace_button_label, content)
    
    # 特殊标签 "SET"
    content = content.replace('l=" SET "', 'l=f" {translate("SET")} "')
    
    return content

def reload_toolbar():
    """重新加载工具栏"""
    try:
        # 重新加载相关模块
        importlib.reload(importlib.import_module('TheKeyMachine.mods.styleMod'))
        importlib.reload(importlib.import_module('TheKeyMachine.core.toolbar'))
        
        # 重新启动UI
        import TheKeyMachine
        TheKeyMachine.reload()
    except Exception as e:
        cmds.warning(f"重新加载工具栏时出错: {str(e)}")

# 自动运行补丁
if __name__ == "__main__":
    apply_chinese_patch() 