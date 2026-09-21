"""
TheKeyMachine 直接汉化工具

此工具可以直接修改TheKeyMachine的源代码，将界面标签从英文替换为中文，
无需额外的补丁和安装步骤。
"""

import os
import re
import shutil
import importlib
import sys

def prepare_translation():
    """准备翻译环境，确保styleMod_cn.py已复制到styleMod.py"""
    try:
        # 引入配置
        from TheKeyMachine.mods.generalMod import config
        
        # 获取安装路径
        INSTALL_PATH = config["INSTALL_PATH"]
        
        # 检查是否存在扩展翻译文件
        styleMod_cn_path = os.path.join(INSTALL_PATH, "TheKeyMachine/styleMod_cn.py")
        styleMod_path = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/styleMod.py")
        
        if os.path.exists(styleMod_cn_path):
            # 备份原始styleMod.py文件
            styleMod_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/styleMod_original.py")
            if not os.path.exists(styleMod_backup):
                shutil.copy2(styleMod_path, styleMod_backup)
            
            # 复制扩展翻译文件到mods目录
            shutil.copy2(styleMod_cn_path, styleMod_path)
            
            # 重新加载styleMod模块以获取更新的翻译
            if "TheKeyMachine.mods.styleMod" in sys.modules:
                importlib.reload(sys.modules["TheKeyMachine.mods.styleMod"])
        
        # 现在导入翻译字典
        from TheKeyMachine.mods.styleMod import chinese_translation
        return chinese_translation
    
    except Exception as e:
        print(f"准备翻译环境时出错: {str(e)}")
        return {}

def direct_translate():
    """直接将TheKeyMachine的界面文本翻译为中文"""
    try:
        # 引入配置
        from TheKeyMachine.mods.generalMod import config
        
        # 获取安装路径
        INSTALL_PATH = config["INSTALL_PATH"]
        
        # 准备翻译字典
        chinese_translation = prepare_translation()
        
        # 如果翻译字典为空，则从现有的模块中导入
        if not chinese_translation:
            from TheKeyMachine.mods.styleMod import chinese_translation
        
        # 定义文件路径
        toolbar_path = os.path.join(INSTALL_PATH, "TheKeyMachine/core/toolbar.py")
        barmod_path = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/barMod.py")
        uimod_path = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/uiMod.py")
        helpermod_path = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/helperMod.py")
        keytools_path = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/keyToolsMod.py")
        selsets_path = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/selSetsMod.py")
        media_path = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/mediaMod.py")
        hotkeys_path = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/hotkeysMod.py")
        customgraph_path = os.path.join(INSTALL_PATH, "TheKeyMachine/core/customGraph.py")
        
        # 备份文件
        toolbar_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/core/toolbar_original.py")
        barmod_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/barMod_original.py")
        uimod_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/uiMod_original.py")
        helpermod_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/helperMod_original.py")
        keytools_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/keyToolsMod_original.py")
        selsets_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/selSetsMod_original.py")
        media_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/mediaMod_original.py")
        hotkeys_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/mods/hotkeysMod_original.py")
        customgraph_backup = os.path.join(INSTALL_PATH, "TheKeyMachine/core/customGraph_original.py")
        
        # 备份主要文件
        if not os.path.exists(toolbar_backup):
            shutil.copy2(toolbar_path, toolbar_backup)
        
        if not os.path.exists(barmod_backup):
            shutil.copy2(barmod_path, barmod_backup)
            
        # 备份其他模块文件
        if os.path.exists(uimod_path) and not os.path.exists(uimod_backup):
            shutil.copy2(uimod_path, uimod_backup)
            
        if os.path.exists(helpermod_path) and not os.path.exists(helpermod_backup):
            shutil.copy2(helpermod_path, helpermod_backup)
            
        if os.path.exists(keytools_path) and not os.path.exists(keytools_backup):
            shutil.copy2(keytools_path, keytools_backup)
            
        if os.path.exists(selsets_path) and not os.path.exists(selsets_backup):
            shutil.copy2(selsets_path, selsets_backup)
            
        if os.path.exists(media_path) and not os.path.exists(media_backup):
            shutil.copy2(media_path, media_backup)
            
        if os.path.exists(hotkeys_path) and not os.path.exists(hotkeys_backup):
            shutil.copy2(hotkeys_path, hotkeys_backup)
            
        if os.path.exists(customgraph_path) and not os.path.exists(customgraph_backup):
            shutil.copy2(customgraph_path, customgraph_backup)
            
        # 修改所有文件
        files_translated = 0
        
        # 主核心文件
        if os.path.exists(toolbar_path):
            translate_file(toolbar_path, chinese_translation)
            files_translated += 1
            
        if os.path.exists(barmod_path):
            translate_file(barmod_path, chinese_translation)
            files_translated += 1
        
        # 其他模块文件
        if os.path.exists(uimod_path):
            translate_file(uimod_path, chinese_translation)
            files_translated += 1
            
        if os.path.exists(helpermod_path):
            translate_file(helpermod_path, chinese_translation)
            files_translated += 1
            
        if os.path.exists(keytools_path):
            translate_file(keytools_path, chinese_translation)
            files_translated += 1
            
        if os.path.exists(selsets_path):
            translate_file(selsets_path, chinese_translation)
            files_translated += 1
            
        if os.path.exists(media_path):
            translate_file(media_path, chinese_translation)
            files_translated += 1
            
        if os.path.exists(hotkeys_path):
            translate_file(hotkeys_path, chinese_translation)
            files_translated += 1
            
        if os.path.exists(customgraph_path):
            translate_file(customgraph_path, chinese_translation)
            files_translated += 1
        
        # 返回成功消息
        return f"汉化成功！已汉化{files_translated}个文件。TheKeyMachine界面已改为中文。"
    
    except Exception as e:
        return f"汉化过程出错: {str(e)}"

def translate_file(file_path, translation_dict):
    """将文件中的英文标签替换为中文"""
    if not os.path.exists(file_path):
        return
        
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 记录原始内容，用于比较是否有变化
    original_content = content
    
    # 替换菜单项标签
    # cmds.menuItem(label="English Text")
    pattern_label = r'cmds\.menuItem\(\s*label\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_label, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'label="{english_text}"', f'label="{chinese_text}"')
    
    # 替换菜单项简写形式 l=
    # cmds.menuItem(l="English Text")
    pattern_l = r'cmds\.menuItem\(\s*l\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_l, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'l="{english_text}"', f'l="{chinese_text}"')
    
    # 替换按钮标签
    # cmds.button(label="English Text")
    pattern_button = r'cmds\.button\(\s*label\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_button, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'label="{english_text}"', f'label="{chinese_text}"')
    
    # 替换iconTextButton标签
    # cmds.iconTextButton(l=" SET ")
    if 'l=" SET "' in content:
        content = content.replace('l=" SET "', f'l=" {translation_dict["SET"]} "')
    
    # 替换text标签
    # cmds.text(label="English Text")
    pattern_text = r'cmds\.text\(\s*label\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_text, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'label="{english_text}"', f'label="{chinese_text}"')
    
    # 替换带有annotation的提示
    # annotation="English Text"
    pattern_anno = r'annotation\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_anno, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'annotation="{english_text}"', f'annotation="{chinese_text}"')
    
    # 替换窗口标题
    # title="English Text"
    pattern_title = r'title\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_title, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'title="{english_text}"', f'title="{chinese_text}"')
    
    # 替换提示框文本
    # message="English Text"
    pattern_msg = r'message\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_msg, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'message="{english_text}"', f'message="{chinese_text}"')
    
    # 替换按钮文本数组
    # buttons=["English Text"]
    pattern_buttons = r'buttons\s*=\s*\[\s*"([^"]+)"\s*\]'
    for match in re.finditer(pattern_buttons, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'buttons=["{english_text}"]', f'buttons=["{chinese_text}"]')
    
    # 替换按钮文本
    # button=["English Text"]
    pattern_btn = r'button\s*=\s*\[\s*"([^"]+)"\s*\]'
    for match in re.finditer(pattern_btn, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'button=["{english_text}"]', f'button=["{chinese_text}"]')
    
    # 替换多按钮文本
    # button=["OK", "Cancel"]
    pattern_multi_btn = r'button\s*=\s*\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]'
    for match in re.finditer(pattern_multi_btn, content):
        eng_text1 = match.group(1)
        eng_text2 = match.group(2)
        chi_text1 = translation_dict.get(eng_text1, eng_text1)
        chi_text2 = translation_dict.get(eng_text2, eng_text2)
        content = content.replace(f'button=["{eng_text1}", "{eng_text2}"]', f'button=["{chi_text1}", "{chi_text2}"]')
    
    # 替换defaultButton文本
    # defaultButton="English Text"
    pattern_default_btn = r'defaultButton\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_default_btn, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'defaultButton="{english_text}"', f'defaultButton="{chinese_text}"')
    
    # 替换cancelButton文本
    # cancelButton="English Text"
    pattern_cancel_btn = r'cancelButton\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_cancel_btn, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'cancelButton="{english_text}"', f'cancelButton="{chinese_text}"')
    
    # 替换dismissString文本
    # dismissString="English Text"
    pattern_dismiss = r'dismissString\s*=\s*"([^"]+)"'
    for match in re.finditer(pattern_dismiss, content):
        english_text = match.group(1)
        if english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            content = content.replace(f'dismissString="{english_text}"', f'dismissString="{chinese_text}"')
    
    # 替换通用字符串 - 用于cmds.warning, print等
    # 在字符串引号内查找
    pattern_string = r'["\']([^"\'\n]{5,})["\']'
    for match in re.finditer(pattern_string, content):
        english_text = match.group(1)
        # 只替换较长的文本，避免替换变量名等短文本
        if len(english_text) > 4 and english_text in translation_dict:
            chinese_text = translation_dict[english_text]
            # 注意保留原始引号类型
            quote = match.group(0)[0]
            content = content.replace(f'{quote}{english_text}{quote}', f'{quote}{chinese_text}{quote}')
    
    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def restore_english():
    """恢复英文界面"""
    try:
        # 引入配置
        from TheKeyMachine.mods.generalMod import config
        
        # 获取安装路径
        INSTALL_PATH = config["INSTALL_PATH"]
        
        # 定义文件路径和备份
        files_to_restore = [
            ("TheKeyMachine/core/toolbar.py", "TheKeyMachine/core/toolbar_original.py"),
            ("TheKeyMachine/mods/barMod.py", "TheKeyMachine/mods/barMod_original.py"),
            ("TheKeyMachine/mods/styleMod.py", "TheKeyMachine/mods/styleMod_original.py"),
            ("TheKeyMachine/mods/uiMod.py", "TheKeyMachine/mods/uiMod_original.py"),
            ("TheKeyMachine/mods/helperMod.py", "TheKeyMachine/mods/helperMod_original.py"),
            ("TheKeyMachine/mods/keyToolsMod.py", "TheKeyMachine/mods/keyToolsMod_original.py"),
            ("TheKeyMachine/mods/selSetsMod.py", "TheKeyMachine/mods/selSetsMod_original.py"),
            ("TheKeyMachine/mods/mediaMod.py", "TheKeyMachine/mods/mediaMod_original.py"),
            ("TheKeyMachine/mods/hotkeysMod.py", "TheKeyMachine/mods/hotkeysMod_original.py"),
            ("TheKeyMachine/core/customGraph.py", "TheKeyMachine/core/customGraph_original.py"),
        ]
        
        # 恢复文件
        restored_count = 0
        for target, backup in files_to_restore:
            target_path = os.path.join(INSTALL_PATH, target)
            backup_path = os.path.join(INSTALL_PATH, backup)
            
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, target_path)
                restored_count += 1
        
        return f"已恢复{restored_count}个文件到英文界面。"
    
    except Exception as e:
        return f"恢复英文界面时出错: {str(e)}"

if __name__ == "__main__":
    import sys
    # 检查是否要恢复英文
    if len(sys.argv) > 1 and sys.argv[1] == '--restore':
        print(restore_english())
    else:
        print(direct_translate()) 