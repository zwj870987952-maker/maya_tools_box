"""
Icon provider for animBot UI clone.
Loads icons from local animBot installation when present,
and provides procedural vector drawing via QPainter as fallback.
"""

import os
from PySide6 import QtGui, QtCore, QtWidgets

ANIMBOT_RESOURCES_DIR = r"D:\Users\zhongweijie\Documents\maya\scripts\animBot\_resources\img"
ANIMBOT_ICONS_DIR = os.path.join(ANIMBOT_RESOURCES_DIR, "icons")
ANIMBOT_SHELF_ICONS_DIR = os.path.join(ANIMBOT_RESOURCES_DIR, "icons_shelf")

class AnimBotIconProvider:
    _cache = {}

    @classmethod
    def get_icon(cls, name, color_category="white", tint_color=None, size=QtCore.QSize(28, 28)):
        """
        Get QIcon by name and color category.
        e.g. name='auto_tangent.png' or 'nudge_left'
        """
        if not name.endswith(".png"):
            name = name + ".png"
            
        cache_key = f"{color_category}_{name}_{tint_color}_{size.width()}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        # Draw crisp procedural vector logo for logo/animBot
        if name in ["logo.png", "animBot.png", "animBot_logo.png", "animBot_shelf.png", "main_logo.png"]:
            pix = cls.draw_procedural_icon("logo", "#FFFFFF", size)
            icon = QtGui.QIcon(pix)
            cls._cache[cache_key] = icon
            return icon

        # Try specified color directory first
        icon_path = os.path.join(ANIMBOT_ICONS_DIR, color_category, name)
        if os.path.isfile(icon_path):
            pix = QtGui.QPixmap(icon_path)
            if not pix.isNull() and pix.width() > 0:
                if tint_color:
                    pix = cls.tint_pixmap(pix, tint_color)
                icon = QtGui.QIcon(pix)
                cls._cache[cache_key] = icon
                return icon

        # If not found in requested category, search across all categories
        for cat in ["green", "yellow", "orange", "purple", "pink", "red", "turquoise", "blue", "misc", "white", "dialog"]:
            alt_path = os.path.join(ANIMBOT_ICONS_DIR, cat, name)
            if os.path.isfile(alt_path):
                pix = QtGui.QPixmap(alt_path)
                if not pix.isNull() and pix.width() > 0:
                    if tint_color:
                        pix = cls.tint_pixmap(pix, tint_color)
                    icon = QtGui.QIcon(pix)
                    cls._cache[cache_key] = icon
                    return icon

        # Procedural fallback
        pix = cls.draw_procedural_icon(name.replace(".png", ""), tint_color or "#E0E0E0", size)
        icon = QtGui.QIcon(pix)
        cls._cache[cache_key] = icon
        return icon

    @staticmethod
    def tint_pixmap(pixmap, color_str):
        tinted = QtGui.QPixmap(pixmap.size())
        tinted.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(tinted)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), QtGui.QColor(color_str))
        painter.end()
        return tinted

    @staticmethod
    def draw_procedural_icon(symbol, color_str, size=QtCore.QSize(28, 28)):
        """Draw clean vector icon using QPainter."""
        pixmap = QtGui.QPixmap(size)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        w, h = size.width(), size.height()
        
        if symbol in ["logo", "animBot", "animBot_shelf"]:
            # animBot 'u' robot logo with green & orange eye dots
            pen = QtGui.QPen(QtGui.QColor("#EFEFEF"), 2.4, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
            painter.setPen(pen)
            path = QtGui.QPainterPath()
            path.moveTo(7, 8)
            path.lineTo(7, 16)
            path.arcTo(7, 8, 14, 15, 180, 180)
            path.lineTo(21, 8)
            painter.drawPath(path)
            
            # Left eye dot (Green #84F296)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor("#84F296"))
            painter.drawEllipse(QtCore.QPointF(7, 5.5), 2.2, 2.2)
            
            # Right eye dot (Orange #F2A785)
            painter.setBrush(QtGui.QColor("#F2A785"))
            painter.drawEllipse(QtCore.QPointF(21, 5.5), 2.2, 2.2)
            
        elif symbol in ["plus", "add"]:
            pen = QtGui.QPen(QtGui.QColor(color_str), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(w//2, 7, w//2, h-7)
            painter.drawLine(7, h//2, w-7, h//2)
            
        elif symbol in ["minus", "subtract"]:
            pen = QtGui.QPen(QtGui.QColor(color_str), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(7, h//2, w-7, h//2)
            
        elif symbol in ["arrow_left", "nudge_left"]:
            pen = QtGui.QPen(QtGui.QColor(color_str), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(w-8, h//2, 8, h//2)
            painter.drawLine(8, h//2, 13, h//2 - 4)
            painter.drawLine(8, h//2, 13, h//2 + 4)
            
        elif symbol in ["arrow_right", "nudge_right"]:
            pen = QtGui.QPen(QtGui.QColor(color_str), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap)
            painter.setPen(pen)
            painter.drawLine(8, h//2, w-8, h//2)
            painter.drawLine(w-8, h//2, w-13, h//2 - 4)
            painter.drawLine(w-8, h//2, w-13, h//2 + 4)
            
        else:
            painter.setFont(QtGui.QFont("Segoe UI", 8, QtGui.QFont.Bold))
            painter.setPen(QtGui.QColor(color_str))
            painter.drawText(QtCore.QRect(0, 0, w, h), QtCore.Qt.AlignCenter, symbol[:2].upper())

        painter.end()
        return pixmap
