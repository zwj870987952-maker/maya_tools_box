



'''

    TheKeyMachine - Animation Toolset for Maya Animators                                           
                                                                                                                                              
                                                                                                                                              
    This file is part of TheKeyMachine, an open source software for Autodesk Maya licensed under the GNU General Public License v3.0 (GPL-3.0).                                           
    You are free to use, modify, and distribute this code under the terms of the GPL-3.0 license.                                              
    By using this code, you agree to keep it open source and share any modifications.                                                          
    This code is provided "as is," without any warranty. For the full license text, visit https://www.gnu.org/licenses/gpl-3.0.html

    thekeymachine.xyz / x@thekeymachine.xyz                                                                                                                                        
                                                                                                                                              
    Developed by: Rodrigo Torres / rodritorres.com                                                                                             
                                                                                                                                             


'''



# TKM StyleSheet

QMenu_bg_color = "#333"
QMenu_border_color = "#333"
QMenu_border_size = "0px"
QMenu_padding_size = "2px"

QMenu_item_bg_color = "#333"
QMenu_item_border_color = "#333"
QMenu_item_border_size = "0px"
QMenu_item_padding_v_size = "7px"
QMenu_item_padding_h_size = "35px"

# ______________________________________________ Tool Bar style _______________________________________________ #

QMenu_bg_color = "#232323"
QMenu_padding_size = "0px"
customGraph_BG_color = "#202125"
customGraph_FG_color = "#323232"

# ______________________________________________ Text Translation _______________________________________________ #

# Add Chinese translation dictionary
chinese_translation = {
    # General UI
    "Small": "小",
    "Medium": "中",
    "Big": "大",
    "Reload": "重新加载",
    "Open config file": "打开配置文件",
    "Reload menu": "重新加载菜单",
    
    # Selection Sets
    "SET": "选集",
    "Export Sets": "导出选集",
    "Import Sets": "导入选集",
    "Rename Group": "重命名组",
    "Export Group": "导出组",
    "Delete Group": "删除组",
    "Add Selection": "添加选择",
    "Remove Selection": "移除选择",
    "Change Color": "更改颜色",
    "Rename Set": "重命名选集",
    "Delete Set": "删除选集",
    "Selector": "选择器",
    "Move to ...": "移动到...",
    
    # Bookmark UI
    "Bookmarks": "书签",
    "Down one level": "降一级",
    "Create": "创建",
    "Remove": "移除",
    "Isolate": "隔离",
    
    # Tools Menu
    "Mirror to opposite": "镜像到对面",
    "Add Excepction Invert": "添加反转例外",
    "Add Excepction Keep": "添加保持例外",
    "Remove Exception": "移除例外",
    "Copy Animation": "复制动画",
    "Paste Animation": "粘贴动画",
    "Copy Pose": "复制姿势",
    "Paste Pose": "粘贴姿势",
    
    # Camera Tools
    "Select temp locators": "选择临时定位器",
    "Remove temp locators": "移除临时定位器",
    "Remove followCam": "移除跟随相机",
    
    # Link Objects
    "Copy Link Position": "复制链接位置",
    "Paste Link Position": "粘贴链接位置",
    "Auto-link": "自动链接",
    
    # Blend UI
    "Blend": "混合",
    "Blend to Default": "混合到默认",
    "Blend to Frame": "混合到关键帧",
    "Pull / Push": "拉/推",
    
    # UI Labels
    "PP": "拉推",
    "BL": "混合",
    "BD": "默认",
    "BK": "帧混",
    "T": "处理",
    "TW": "补间",
    "TL": "补帧"
}

def translate(text):
    """返回文本的中文翻译，如果没有翻译则返回原文本"""
    return chinese_translation.get(text, text)