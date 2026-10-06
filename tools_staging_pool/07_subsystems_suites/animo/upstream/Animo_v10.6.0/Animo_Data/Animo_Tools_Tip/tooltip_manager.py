from __future__ import absolute_import, division, print_function, unicode_literals

import inspect
import os
import sys

import compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

import tooltip_widget
from tooltip_data import get_tooltip_data


def _get_accepted_params(func):
    try:
        sig = inspect.signature(func)
        return set(sig.parameters.keys())
    except (AttributeError, ValueError, TypeError):
        pass
    try:
        spec = inspect.getfullargspec(func)
    except AttributeError:
        spec = inspect.getargspec(func)
    return set(spec.args)


class TooltipEventFilter(QtCore.QObject):
    
    def __init__(self, manager):
        super(TooltipEventFilter, self).__init__()
        self._manager = manager
        self._hover_timer = QtCore.QTimer()
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._on_hover_timeout)
        self._default_delay = 500
        self._current_widget = None
        self._widget_delays = {}
    
    def set_widget_delay(self, widget, delay_ms):
        self._widget_delays[widget] = delay_ms
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            self._current_widget = obj
            delay = self._widget_delays.get(obj, self._default_delay)
            self._hover_timer.start(delay)
        elif event.type() == QtCore.QEvent.Leave:
            self._hover_timer.stop()
            self._current_widget = None
        elif event.type() == QtCore.QEvent.MouseButtonPress:
            self._hover_timer.stop()
            self._manager.hide_current_tooltip()
        
        return False
    
    def _on_hover_timeout(self):
        if self._current_widget:
            self._manager.show_tooltip_for_widget(self._current_widget)


class TooltipManager(QtCore.QObject):
    
    def __init__(self, animo_data_path):
        super(TooltipManager, self).__init__()
        
        self._animo_data_path = animo_data_path
        self._gif_folder = os.path.join(animo_data_path, "Animo_Tools_Tip", "gif")
        self._icons_path = os.path.join(animo_data_path, "icons")
        
        self._event_filter = TooltipEventFilter(self)
        self._current_tooltip = None
        self._widget_data = {}
        self._enabled = True
    
    def set_enabled(self, enabled):
        self._enabled = enabled
        if not enabled:
            self.hide_current_tooltip()
    
    def is_enabled(self):
        return self._enabled
    
    def register_button(self, widget, launcher_name, icon_path=None, hover_delay=None):
        widget.installEventFilter(self._event_filter)
        self._widget_data[widget] = (launcher_name, icon_path)
        
        if hover_delay is not None:
            self._event_filter.set_widget_delay(widget, hover_delay)
        
        widget.setToolTip("")
    
    def unregister_button(self, widget):
        widget.removeEventFilter(self._event_filter)
        if widget in self._widget_data:
            del self._widget_data[widget]
    
    def show_tooltip_for_widget(self, widget):
        if not self._enabled:
            return
        
        if widget not in self._widget_data:
            return
        
        self.hide_current_tooltip()
        
        launcher_name, icon_path = self._widget_data[widget]
        data = get_tooltip_data(launcher_name)
        
        gif_name = data.get("gif", "")
        gif_paths = []
        if gif_name:
            main_gif = os.path.join(self._gif_folder, gif_name + ".gif")
            if os.path.exists(main_gif):
                gif_paths.append(main_gif)
            
            for i in range(1, 100):
                numbered_gif = os.path.join(self._gif_folder, gif_name + str(i) + ".gif")
                if os.path.exists(numbered_gif):
                    gif_paths.append(numbered_gif)
        
        icon_pixmap = None
        if icon_path and os.path.exists(icon_path):
            icon_pixmap = QtGui.QPixmap(icon_path)
        
        self._current_tooltip = tooltip_widget.AnimoTooltip()
        self._current_tooltip.set_source_widget(widget)
        self._current_tooltip.set_trigger_button(widget)
        
        content_kwargs = {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "gif_paths": gif_paths,
            "info_lines": data.get("info_lines", []),
            "shortcut": data.get("shortcut", ""),
            "icon_pixmap": icon_pixmap,
            "title_color": data.get("title_color", "#4aa3df")
        }
        accepted_params = _get_accepted_params(self._current_tooltip.set_content)
        filtered_kwargs = dict((k, v) for k, v in content_kwargs.items() if k in accepted_params)
        
        self._current_tooltip.set_content(**filtered_kwargs)
        
        self._current_tooltip.show_at_widget(widget)
    
    def hide_current_tooltip(self):
        if self._current_tooltip:
            try:
                self._current_tooltip.hide_tooltip()
            except RuntimeError:
                pass
            self._current_tooltip = None
    
    def set_hover_delay(self, milliseconds):
        self._event_filter._hover_delay = milliseconds


_tooltip_manager = None


def get_tooltip_manager():
    return _tooltip_manager


def init_tooltip_manager(animo_data_path):
    global _tooltip_manager
    _tooltip_manager = TooltipManager(animo_data_path)
    return _tooltip_manager