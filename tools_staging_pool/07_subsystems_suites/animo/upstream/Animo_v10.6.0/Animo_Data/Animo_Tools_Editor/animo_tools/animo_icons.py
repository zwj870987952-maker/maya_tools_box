from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
import sys

def _get_this_dir():
    if hasattr(sys, '_animo_tools_path') and sys._animo_tools_path:
        return sys._animo_tools_path
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    try:
        import maya.cmds as cmds
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
        return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")
    except:
        return ""

_this_dir = _get_this_dir()
if _this_dir and _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

import maya.cmds as cmds

import animo_compat as compat
QtCore = compat.QtCore
QtGui = compat.QtGui
QSvgRenderer = compat.QSvgRenderer

import icon_data as icon_data
AVAILABLE_ICONS = icon_data.AVAILABLE_ICONS
AVAILABLE_COLORS = icon_data.AVAILABLE_COLORS

import icon_svg_data as icon_svg_data
SVG_ICONS = icon_svg_data.SVG_ICONS

import icon_svg_data2 as icon_svg_data2
SVG_ICONS_2 = icon_svg_data2.SVG_ICONS_2

import icon_svg_data3 as icon_svg_data3
SVG_ICONS_3 = icon_svg_data3.SVG_ICONS_3

class IconManager(object):
    
    def __init__(self):
        self.icons_dir = self.get_icons_directory()
        self.ensure_icons_exist()
        self.available_icons = AVAILABLE_ICONS
        self.available_colors = AVAILABLE_COLORS
        self.raster_extensions = self._get_supported_raster_extensions()
        self.custom_extensions = set(['.svg']) | self.raster_extensions
    
    def _get_supported_raster_extensions(self):
        fallback_extensions = set([
            '.png', '.ico', '.jpg', '.jpeg', '.bmp', '.gif',
            '.ppm', '.pgm', '.pbm', '.xpm', '.tif', '.tiff', '.webp'
        ])
        
        try:
            detected_extensions = set()
            for fmt in QtGui.QImageReader.supportedImageFormats():
                try:
                    text = bytes(fmt).decode('utf-8').lower()
                except Exception:
                    text = str(fmt).lower()
                if text:
                    detected_extensions.add('.' + text)
            
            if detected_extensions:
                return detected_extensions | fallback_extensions
        except Exception:
            pass
        
        return fallback_extensions
    
    def get_icons_directory(self):
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        animo_data_root = self._get_animo_tools_editor_root()
        icons_dir = os.path.join(animo_data_root, "icons")
        
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
        
        custom_icons_dir = os.path.join(icons_dir, "custom")
        if not os.path.exists(custom_icons_dir):
            os.makedirs(custom_icons_dir)
        
        self._migrate_legacy_custom_icons(maya_scripts_dir, animo_data_root, icons_dir, custom_icons_dir)
        
        return icons_dir
    
    def _get_animo_tools_editor_root(self):
        try:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.normpath(os.path.join(this_dir, ".."))
        except NameError:
            pass
        
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
        return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor")
    
    def _copy_missing_files(self, source_dir, target_dir, files_only=False):
        if not source_dir or not target_dir or not os.path.exists(source_dir):
            return
        
        if os.path.normcase(os.path.normpath(source_dir)) == os.path.normcase(os.path.normpath(target_dir)):
            return
        
        try:
            for filename in os.listdir(source_dir):
                source_path = os.path.join(source_dir, filename)
                if files_only and not os.path.isfile(source_path):
                    continue
                if not os.path.isfile(source_path):
                    continue
                
                target_path = os.path.join(target_dir, filename)
                if not os.path.exists(target_path):
                    shutil.copyfile(source_path, target_path)
        except Exception:
            pass
    
    def _migrate_legacy_custom_icons(self, maya_scripts_dir, animo_data_root, icons_dir, custom_icons_dir):
        # Icons that were saved per Maya version, before storage became shared.
        per_version_custom_dir = os.path.join(maya_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "icons", "custom")
        self._copy_missing_files(per_version_custom_dir, custom_icons_dir, files_only=True)
        
        # Icons that were briefly nested inside tools_library, where they were
        # mistaken for a category folder by the tools library scan.
        stray_icons_dir = os.path.join(animo_data_root, "tools_library", "icons")
        stray_custom_dir = os.path.join(stray_icons_dir, "custom")
        self._copy_missing_files(stray_custom_dir, custom_icons_dir, files_only=True)
        self._copy_missing_files(stray_icons_dir, icons_dir, files_only=True)
        
        if os.path.exists(stray_icons_dir):
            try:
                shutil.rmtree(stray_icons_dir)
            except Exception:
                pass
    
    def get_custom_icons_directory(self):
        return os.path.join(self.icons_dir, "custom")
    
    def get_icon_path(self, icon_name):
        custom_dir = self.get_custom_icons_directory()
        
        for extension in self.custom_extensions:
            custom_path = os.path.join(custom_dir, icon_name + extension)
            if os.path.exists(custom_path):
                return custom_path
        
        return os.path.join(self.icons_dir, icon_name + '.svg')
    
    def get_available_icons(self):
        icons = []
        
        custom_dir = self.get_custom_icons_directory()
        if os.path.exists(custom_dir):
            for filename in os.listdir(custom_dir):
                name, extension = os.path.splitext(filename)
                if extension.lower() in self.custom_extensions and name not in icons:
                    icons.append(name)
        
        for icon_name in self.available_icons:
            if icon_name not in icons:
                icon_path = os.path.join(self.icons_dir, icon_name + '.svg')
                if os.path.exists(icon_path):
                    icons.append(icon_name)
        
        return sorted(icons)
    
    def sanitize_icon_key(self, name):
        if not name:
            return "custom_icon"
        
        invalid_chars = '<>:"/\\|?*'
        cleaned = ''.join(ch for ch in name if ch not in invalid_chars and ord(ch) >= 32)
        cleaned = cleaned.strip().strip('.').strip()
        
        return cleaned or "custom_icon"
    
    def remove_custom_icon(self, icon_name):
        custom_dir = self.get_custom_icons_directory()
        
        for extension in self.custom_extensions:
            existing_path = os.path.join(custom_dir, icon_name + extension)
            if os.path.exists(existing_path):
                try:
                    os.remove(existing_path)
                except Exception:
                    pass
    
    def rename_custom_icon(self, old_icon_name, new_icon_name):
        if old_icon_name == new_icon_name:
            return new_icon_name
        
        custom_dir = self.get_custom_icons_directory()
        
        for extension in self.custom_extensions:
            old_path = os.path.join(custom_dir, old_icon_name + extension)
            if os.path.exists(old_path):
                self.remove_custom_icon(new_icon_name)
                new_path = os.path.join(custom_dir, new_icon_name + extension)
                try:
                    shutil.move(old_path, new_path)
                    return new_icon_name
                except Exception:
                    return old_icon_name
        
        return old_icon_name
    
    def import_custom_icon(self, source_path, icon_name):
        if not source_path or not os.path.exists(source_path):
            return None
        
        extension = os.path.splitext(source_path)[1].lower()
        if extension not in self.custom_extensions:
            return None
        
        custom_dir = self.get_custom_icons_directory()
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir)
        
        icon_name = self.sanitize_icon_key(icon_name)
        
        self.remove_custom_icon(icon_name)
        
        target_path = os.path.join(custom_dir, icon_name + extension)
        
        try:
            shutil.copyfile(source_path, target_path)
        except Exception:
            return None
        
        return icon_name
    
    def create_pixmap(self, icon_name, size=20):
        icon_path = self.get_icon_path(icon_name)
        
        if not os.path.exists(icon_path):
            return QtGui.QPixmap()
        
        extension = os.path.splitext(icon_path)[1].lower()
        
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtGui.QColor(0, 0, 0, 0))
        
        if extension == '.svg':
            renderer = QSvgRenderer(icon_path)
            painter = QtGui.QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return pixmap
        
        source_pixmap = QtGui.QPixmap(icon_path)
        if source_pixmap.isNull():
            return QtGui.QPixmap()
        
        scaled_pixmap = source_pixmap.scaled(
            size, size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        
        painter = QtGui.QPainter(pixmap)
        offset_x = (size - scaled_pixmap.width()) // 2
        offset_y = (size - scaled_pixmap.height()) // 2
        painter.drawPixmap(offset_x, offset_y, scaled_pixmap)
        painter.end()
        
        return pixmap
    
    def ensure_icons_exist(self):
        all_svg_icons = {}
        all_svg_icons.update(SVG_ICONS)
        all_svg_icons.update(SVG_ICONS_2)
        all_svg_icons.update(SVG_ICONS_3)
        
        for filename, svg_content in all_svg_icons.items():
            filepath = os.path.join(self.icons_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(svg_content)
