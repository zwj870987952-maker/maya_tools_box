"""Runtime compatibility patches shared by every Studio Library asset type."""

from __future__ import absolute_import, print_function

import logging
import os

from studiovendor.Qt import QtWidgets

import studioqt.menu
import studiolibrary
import studiolibrary.library
import studiolibrary.libraryitem
import studiolibrary.librarywindow
import studiolibrary.widgets.formwidget
import studiolibrary.widgets.menubarwidget
import studiolibrary.widgets.sortbymenu

from . import history
from . import localization


logger = logging.getLogger(__name__)
_installed = False


def _find_action_by_source(actions, text, case_sensitive=True):
    """Find a translated action by the original English source text."""
    expected = str(text or "")
    if not case_sensitive:
        expected = expected.lower()
    for action in actions:
        source = action.property("_sl_plus_source_text")
        if source is None:
            source = localization.source_text(action.text())
        source = str(source or "")
        if not case_sensitive:
            source = source.lower()
        if source == expected:
            return action
    return None


def _warning(message):
    try:
        import maya.cmds
        maya.cmds.warning(message)
    except (ImportError, RuntimeError):
        logger.warning(message)


def _asset_destination(item):
    path = item.path()
    extension = getattr(item, "EXTENSION", "")
    if path and extension and not path.endswith(extension):
        path += extension
    return path


def _patch_safe_save():
    cls = studiolibrary.libraryitem.LibraryItem
    original = cls.safeSave

    def safe_save_with_history(self, *args, **kwargs):
        destination = _asset_destination(self)
        stage = None
        eligible = (
            destination and
            os.path.isdir(destination) and
            getattr(self, "EXTENSION", "") and
            not history.is_history_path(destination) and
            not studiolibrary.isVersionPath(destination)
        )
        if eligible:
            stage = history.stage_existing_asset(destination, self)

        try:
            result = original(self, *args, **kwargs)
        except Exception:
            if stage and not history.restore_stage(stage):
                _warning(
                    "Studio Library PlusPatch kept a recovery copy at: {0}"
                    .format(stage["stage"])
                )
            raise

        if stage:
            try:
                version_path = history.commit_stage(stage, self.path())
                if version_path and hasattr(self, "syncItemData"):
                    self.syncItemData()
            except Exception as error:
                _warning(
                    "The asset was saved, but history finalization failed: {0}. "
                    "Recovery data: {1}".format(error, stage["stage"])
                )
        return result

    safe_save_with_history._studio_library_plus_original = original
    cls.safeSave = safe_save_with_history


def _patch_library_items():
    cls = studiolibrary.library.Library
    original = cls.createItems

    def create_items_with_history(self):
        items = original(self)
        items = [item for item in items
                 if not item.itemData().get(history.VIRTUAL_FIELD)]
        if localization.history_enabled():
            items = history.inject_history_items(self, items)
        self._items = items
        return self._items

    create_items_with_history._studio_library_plus_original = original
    cls.createItems = create_items_with_history

    fields = cls.Fields
    if not any(field.get("name") == "modified" for field in fields):
        fields.append({
            "name": "modified",
            "sortable": True,
            "groupable": False,
        })


def _set_show_history(enabled):
    localization.set_history_enabled(enabled)
    for window in studiolibrary.librarywindow.LibraryWindow.instances():
        window.library().search()


def _set_language(value):
    localization.set_language(value)
    windows = list(studiolibrary.librarywindow.LibraryWindow.instances())
    for window in windows:
        window.updatePreviewWidget()
    localization.retranslate_windows(windows)


def _language_menu(parent):
    menu = QtWidgets.QMenu(localization.translate("Language"), parent)
    selected = localization.language()
    for label, value in (("English", "en_US"), (u"简体中文", "zh_CN")):
        action = QtWidgets.QAction(label, menu)
        action.setCheckable(True)
        action.setChecked(selected == value)
        action.triggered.connect(lambda _checked=False, code=value: _set_language(code))
        menu.addAction(action)
    return menu


def _patch_library_window():
    cls = studiolibrary.librarywindow.LibraryWindow
    original_init = cls.__init__
    original_settings_menu = cls.createSettingsMenu
    original_new_menu = cls.createNewItemMenu
    original_context_menu = cls.createItemContextMenu
    original_set_preview = cls.setPreviewWidget

    def init_with_localization(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        localization.translate_object_tree(self)

    def create_settings_menu(self):
        menu = original_settings_menu(self)
        menu.addSeparator()

        action = QtWidgets.QAction(localization.translate("Show History"), menu)
        action.setCheckable(True)
        action.setChecked(localization.history_enabled())
        action.triggered[bool].connect(_set_show_history)
        menu.addAction(action)
        menu.addMenu(_language_menu(menu))
        localization.translate_object_tree(menu)
        return menu

    def create_new_menu(self):
        menu = original_new_menu(self)
        localization.translate_object_tree(menu)
        return menu

    def create_context_menu(self, items):
        menu = original_context_menu(self, items)
        localization.translate_object_tree(menu)
        return menu

    def set_preview_widget(self, widget):
        result = original_set_preview(self, widget)
        localization.translate_object_tree(widget)
        return result

    cls.__init__ = init_with_localization
    cls.createSettingsMenu = create_settings_menu
    cls.createNewItemMenu = create_new_menu
    cls.createItemContextMenu = create_context_menu
    cls.setPreviewWidget = set_preview_widget


def _patch_form_schema():
    cls = studiolibrary.widgets.formwidget.FormWidget
    original = cls.setSchema

    def set_schema_translated(self, schema, *args, **kwargs):
        result = original(
            self, localization.translate_schema(schema), *args, **kwargs
        )
        localization.translate_object_tree(self)
        return result

    cls.setSchema = set_schema_translated


def _patch_action_lookup():
    """Keep Studio Library's text-based action lookup working in Chinese."""
    cls = studiolibrary.widgets.menubarwidget.MenuBarWidget
    original_find_action = cls.findAction
    original_find_tool_button = cls.findToolButton

    def find_action(self, text):
        action = original_find_action(self, text)
        if action:
            return action
        return _find_action_by_source(self.actions(), text)

    def find_tool_button(self, text):
        widget = original_find_tool_button(self, text)
        if widget:
            return widget
        action = _find_action_by_source(self.actions(), text)
        return self.widgetForAction(action) if action else None

    cls.findAction = find_action
    cls.findToolButton = find_tool_button

    menu_cls = studioqt.menu.Menu
    original_menu_find_action = menu_cls.findAction

    def menu_find_action(self, text):
        action = original_menu_find_action(self, text)
        if action:
            return action
        return _find_action_by_source(
            self.actions(), text, case_sensitive=False
        )

    menu_cls.findAction = menu_find_action


def _patch_sort_menu():
    cls = studiolibrary.widgets.sortbymenu.SortByMenu
    original = cls.populateMenu

    def populate_menu(self):
        result = original(self)
        for action in self.actions():
            if action.text() == "Modified":
                action.setText("Last Modified")
        localization.translate_object_tree(self)
        return result

    cls.populateMenu = populate_menu


def install():
    """Install all runtime hooks once per Maya process."""
    global _installed
    if _installed:
        return
    _installed = True
    _patch_safe_save()
    _patch_library_items()
    _patch_form_schema()
    _patch_action_lookup()
    _patch_sort_menu()
    _patch_library_window()
