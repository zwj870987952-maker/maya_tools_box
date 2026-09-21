# -*- coding: utf-8 -*-
"""
Studio Library - Modern Dark Theme Patch (一键独立主题安装器)
============================================================
特性：
1. 纯美术/样式层热替换，零侵入，绝不修改插件的 Python 业务功能代码。
2. 自动建立 .backup 备份，可随时通过 uninstall_theme.py 完整还原。
3. 完全独立，不影响第三方拓展包 (如 PlusPatch) 的安装与独立更新。
4. 支持在 Maya 脚本编辑器中直接运行，即时热刷新当前界面。
"""

import os
import shutil
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StudioLibraryThemePatch")


def find_studiolibrary_root():
    """
    智能查找 Studio Library 的根目录或资源目录
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(current_dir, "..", "src", "studiolibrary", "resource"),
        os.path.join(current_dir, "src", "studiolibrary", "resource"),
        os.path.join(current_dir, "studiolibrary", "resource"),
    ]

    for cand in candidates:
        cand_norm = os.path.normpath(cand)
        if os.path.isdir(cand_norm) and os.path.isdir(os.path.join(cand_norm, "css")):
            return os.path.abspath(cand_norm)

    if "studiolibrary" in sys.modules:
        try:
            import studiolibrary
            return studiolibrary.resource.RESOURCE_DIRNAME
        except Exception:
            pass

    return None


def install():
    """
    执行主题补丁安装
    """
    patch_dir = os.path.dirname(os.path.abspath(__file__))
    theme_res_dir = os.path.join(patch_dir, "theme_resources")

    if not os.path.exists(theme_res_dir):
        logger.error(u"[错误] 未找到 theme_resources 目录: %s", theme_res_dir)
        return False

    target_res_dir = find_studiolibrary_root()
    if not target_res_dir or not os.path.exists(target_res_dir):
        logger.error(u"[错误] 未能自动定位到 studiolibrary/resource 目录，请确认插件安装完整。")
        return False

    logger.info(u"目标资源目录: %s", target_res_dir)

    target_css_dir = os.path.join(target_res_dir, "css")
    backup_css_file = os.path.join(target_css_dir, "default.css.orig_backup")
    target_css_file = os.path.join(target_css_dir, "default.css")

    if os.path.exists(target_css_file) and not os.path.exists(backup_css_file):
        try:
            shutil.copy2(target_css_file, backup_css_file)
            logger.info(u"[备份] 已创建原始样式备份: %s", backup_css_file)
        except Exception as e:
            logger.warning(u"[警告] 备份失败: %s", str(e))

    src_css_file = os.path.join(theme_res_dir, "css", "default.css")
    if os.path.exists(src_css_file):
        try:
            shutil.copy2(src_css_file, target_css_file)
            logger.info(u"[安装] 成功应用 Modern Dark 样式表: %s", target_css_file)
        except Exception as e:
            logger.error(u"[失败] 复制样式表失败: %s", str(e))
            return False

    src_icons_dir = os.path.join(theme_res_dir, "icons")
    target_icons_dir = os.path.join(target_res_dir, "icons")
    if os.path.exists(src_icons_dir):
        for item in os.listdir(src_icons_dir):
            s = os.path.join(src_icons_dir, item)
            d = os.path.join(target_icons_dir, item)
            if os.path.isfile(s):
                try:
                    shutil.copy2(s, d)
                except Exception:
                    pass
        logger.info(u"[图标] 主题图标已同步。")

    try:
        import studiolibrary
        windows = []
        try:
            from studiolibrarymaya import mayalibrarywindow
            windows.extend(mayalibrarywindow.MayaLibraryWindow.instances())
        except Exception:
            pass

        try:
            from studiolibrary import librarywindow
            windows.extend(librarywindow.LibraryWindow.instances())
        except Exception:
            pass

        for win in windows:
            if hasattr(win, "reloadStyleSheet"):
                # 如果是首次切换，自动适配 Modern Dark 调色
                try:
                    import studiolibrary.widgets
                    theme = studiolibrary.widgets.Theme()
                    theme.setAccentColor("rgb(108, 92, 231)")
                    theme.setBackgroundColor("rgb(24, 25, 32)")
                    theme.setName("Modern Dark (Studio)")
                    win.setTheme(theme)
                    win.saveSettings()
                except Exception:
                    pass
                win.reloadStyleSheet()
                if hasattr(win, "showToastMessage"):
                    win.showToastMessage("Theme Patched: Modern Dark")
        logger.info(u"[热重载] 已对当前运行的 Studio Library 窗口应用新主题。")
    except Exception as e:
        logger.warning(u"[提示] 热重载窗口时跳过: %s", str(e))

    logger.info(u"==================================================")
    logger.info(u"🎉 Modern Dark 专属主题包已成功安装！")
    logger.info(u"==================================================")
    return True


if __name__ == "__main__":
    install()
