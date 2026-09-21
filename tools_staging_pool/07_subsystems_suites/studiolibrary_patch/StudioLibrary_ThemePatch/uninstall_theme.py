# -*- coding: utf-8 -*-
"""
Studio Library - Modern Dark Theme Patch (一键独立主题卸载器)
============================================================
将 Studio Library 恢复为官方初始样式。
"""

import os
import shutil
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StudioLibraryThemePatch")


def find_studiolibrary_root():
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


def uninstall():
    target_res_dir = find_studiolibrary_root()
    if not target_res_dir or not os.path.exists(target_res_dir):
        logger.error(u"[错误] 未能定位到资源目录。")
        return False

    target_css_dir = os.path.join(target_res_dir, "css")
    backup_css_file = os.path.join(target_css_dir, "default.css.orig_backup")
    target_css_file = os.path.join(target_css_dir, "default.css")

    if os.path.exists(backup_css_file):
        try:
            shutil.copy2(backup_css_file, target_css_file)
            logger.info(u"[还原] 已成功恢复原始样式表: %s", target_css_file)
        except Exception as e:
            logger.error(u"[失败] 恢复样式表失败: %s", str(e))
            return False
    else:
        logger.warning(u"[提示] 未检测到原始备份文件，无需还原。")

    try:
        import studiolibrary
        for win in studiolibrary.LibraryWindow.instances():
            if hasattr(win, "reloadStyleSheet"):
                win.reloadStyleSheet()
                if hasattr(win, "showToastMessage"):
                    win.showToastMessage("Restored Default Theme")
    except Exception:
        pass

    logger.info(u"==================================================")
    logger.info(u"✅ 已成功恢复官方默认主题样式！")
    logger.info(u"==================================================")
    return True


if __name__ == "__main__":
    uninstall()
