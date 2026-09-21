"""Startup compatibility helpers for PlusPatch asset cache records."""

from __future__ import absolute_import

import os

import maya.cmds
import maya.utils

import studiolibrary
import studiolibrary.librarywindow


ITEM_CLASSES = {
    ".wanim": "studiolibrary_wanimation.wanimationitem.WAnimationItem",
    ".wpose": "studiolibrary_wanimation.wposeitem.WPoseItem",
}
_scheduled = False


def _asset_paths(root, max_depth, extensions=None):
    result = []
    extensions = tuple(extensions or ITEM_CLASSES.keys())
    root = studiolibrary.normPath(root)
    start_depth = root.count("/")
    for current_root, directories, _files in os.walk(root):
        current_root = studiolibrary.normPath(current_root)
        for directory in list(directories):
            path = studiolibrary.normPath(os.path.join(current_root, directory))
            if directory.lower().endswith(extensions):
                result.append(path)
                directories.remove(directory)
            elif directory.startswith("."):
                directories.remove(directory)
        if current_root.count("/") - start_depth >= max_depth:
            del directories[:]
    return result


def _wanimation_paths(root, max_depth):
    """Backward-compatible helper retained for existing tests/tools."""
    return _asset_paths(root, max_depth, extensions=(".wanim",))


def _class_for_path(path):
    lower = path.lower()
    if lower.endswith(".wanim"):
        from .wanimationitem import WAnimationItem
        return WAnimationItem
    if lower.endswith(".wpose"):
        from .wposeitem import WPoseItem
        return WPoseItem


def repair_library_cache(library):
    """Repair missing or misclassified WAnimation and WPose cache rows."""
    if not library or not library.path() or not os.path.isdir(library.path()):
        return 0

    data = library.read() or {}
    candidate_paths = []
    for extension in ITEM_CLASSES:
        cached = [
            path for path in data.keys()
            if path.lower().endswith(extension) and os.path.isdir(path)
        ]
        candidate_paths.extend(cached)
        if not cached:
            candidate_paths.extend(_asset_paths(
                library.path(), library.recursiveDepth(),
                extensions=(extension,),
            ))

    repair_paths = []
    for path in sorted(set(candidate_paths)):
        expected = None
        for extension, class_path in ITEM_CLASSES.items():
            if path.lower().endswith(extension):
                expected = class_path
                break
        if expected and data.get(path, {}).get("__class__") != expected:
            repair_paths.append(path)

    if not repair_paths:
        return 0

    items = []
    for path in repair_paths:
        cls = _class_for_path(path)
        if not cls:
            continue
        item = cls(
            path,
            library=library,
            libraryWindow=getattr(library, "_libraryWindow", None),
        )
        item.setItemData(item.createItemData())
        items.append(item)
    library.saveItemData(items)
    return len(items)


def _repair_deferred(attempt=0):
    windows = list(studiolibrary.librarywindow.LibraryWindow.instances())
    if not windows and attempt < 8:
        maya.utils.executeDeferred(lambda: _repair_deferred(attempt + 1))
        return
    repaired = 0
    for window in windows:
        try:
            repaired += repair_library_cache(window.library())
        except Exception as error:
            maya.cmds.warning(
                "Studio Library PlusPatch cache check failed: {0}".format(error)
            )
    if repaired:
        print("Studio Library PlusPatch repaired {0} cache item(s).".format(
            repaired
        ))


def schedule_cache_repair():
    global _scheduled
    if _scheduled or maya.cmds.about(batch=True):
        return
    _scheduled = True
    maya.utils.executeDeferred(_repair_deferred)
