"""Runtime language-pack support for Studio Library's hard-coded UI text."""

from __future__ import absolute_import

import io
import json
import os
import weakref

from studiovendor.Qt import QtCore, QtWidgets
from studiovendor import six


SETTINGS_ORGANIZATION = "StudioLibraryPlusPatch"
SETTINGS_APPLICATION = "StudioLibraryPlusPatch"
LANGUAGE_KEY = "language"
HISTORY_KEY = "showHistory"
DEFAULT_LANGUAGE = "en_US"
CHINESE_LANGUAGE = "zh_CN"
PACKAGE_PATH = os.path.dirname(__file__)
_translations = None
_translated_roots = []


def _settings():
    return QtCore.QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)


def language():
    value = _settings().value(LANGUAGE_KEY, DEFAULT_LANGUAGE)
    return str(value or DEFAULT_LANGUAGE)


def set_language(value):
    value = value if value in (DEFAULT_LANGUAGE, CHINESE_LANGUAGE) else DEFAULT_LANGUAGE
    _settings().setValue(LANGUAGE_KEY, value)
    return value


def history_enabled():
    value = _settings().value(HISTORY_KEY, False)
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("1", "true", "yes", "on")


def set_history_enabled(value):
    _settings().setValue(HISTORY_KEY, bool(value))


def _load_translations():
    global _translations
    if _translations is None:
        path = os.path.join(PACKAGE_PATH, "locales", "zh_CN.json")
        with io.open(path, "r", encoding="utf-8-sig") as stream:
            _translations = json.load(stream)
    return _translations


def source_text(text):
    text = str(text or "")
    reverse = dict((value, key) for key, value in _load_translations().items())
    return reverse.get(text, text)


def translate(text, selected_language=None):
    text = source_text(text)
    selected_language = selected_language or language()
    if selected_language == CHINESE_LANGUAGE:
        return _load_translations().get(text, text)
    return text


def translate_schema(schema):
    """Translate a copied FormWidget schema without mutating item classes."""
    def structural_copy(value):
        # Schema callbacks frequently contain bound LibraryItem/PoseItem
        # objects. Deep-copying them invokes pickle and fails in Maya. Only
        # copy mutable schema containers; preserve Qt/Maya/callback objects.
        if isinstance(value, dict):
            return dict((key, structural_copy(child))
                        for key, child in value.items())
        if isinstance(value, list):
            return [structural_copy(child) for child in value]
        if isinstance(value, tuple):
            return tuple(structural_copy(child) for child in value)
        return value

    result = structural_copy(schema)

    def visit(value):
        if isinstance(value, dict):
            for key, child in list(value.items()):
                if key in ("title", "toolTip", "placeholder") and isinstance(child, six.string_types):
                    value[key] = translate(child)
                elif key == "placeholder" and isinstance(child, (list, tuple)):
                    value[key] = type(child)(
                        translate(item) if isinstance(item, six.string_types) else item
                        for item in child
                    )
                elif key == "label" and isinstance(child, dict):
                    visit(child)
                elif isinstance(child, (dict, list)):
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        return value

    return visit(result)


def _translate_property(obj, getter_name, setter_name):
    getter = getattr(obj, getter_name, None)
    setter = getattr(obj, setter_name, None)
    if not callable(getter) or not callable(setter):
        return
    try:
        current = getter()
    except (RuntimeError, TypeError):
        return
    if not isinstance(current, six.string_types) or not current:
        return
    property_name = "_sl_plus_source_" + getter_name
    source = obj.property(property_name)
    if source is None:
        source = source_text(current)
        obj.setProperty(property_name, source)
    elif current not in (str(source), translate(source, CHINESE_LANGUAGE)):
        source = source_text(current)
        obj.setProperty(property_name, source)
    setter(translate(source))


def translate_object(obj):
    for getter, setter in (
            ("text", "setText"),
            ("title", "setTitle"),
            ("windowTitle", "setWindowTitle"),
            ("toolTip", "setToolTip"),
            ("statusTip", "setStatusTip"),
            ("placeholderText", "setPlaceholderText")):
        # Radio button text and combo-box items are also their data values in
        # Studio Library 2.x. Translating them would change load/save options.
        if getter == "text" and isinstance(obj, QtWidgets.QRadioButton):
            continue
        _translate_property(obj, getter, setter)

    if isinstance(obj, QtWidgets.QTabWidget):
        for index in range(obj.count()):
            obj.setTabText(index, translate(obj.tabText(index)))

    if isinstance(obj, QtWidgets.QTreeWidget):
        header = obj.headerItem()
        if header:
            for index in range(header.columnCount()):
                header.setText(index, translate(header.text(index)))


def _register_root(root):
    alive = []
    found = False
    for reference in _translated_roots:
        current = reference()
        if current is None:
            continue
        alive.append(reference)
        if current is root:
            found = True
    _translated_roots[:] = alive
    if not found:
        try:
            _translated_roots.append(weakref.ref(root))
        except TypeError:
            pass


def translate_object_tree(root, register=True):
    if root is None:
        return
    if register:
        _register_root(root)
    translate_object(root)
    for child in root.findChildren(QtCore.QObject):
        translate_object(child)


def retranslate_windows(windows):
    roots = []
    seen = set()
    for reference in list(_translated_roots):
        root = reference()
        if root is not None and id(root) not in seen:
            roots.append(root)
            seen.add(id(root))
    for window in windows:
        if window is not None and id(window) not in seen:
            roots.append(window)
            seen.add(id(window))
    for root in roots:
        try:
            translate_object_tree(root, register=False)
        except RuntimeError:
            # PySide wrappers can outlive their deleted C++ QObject.
            continue
