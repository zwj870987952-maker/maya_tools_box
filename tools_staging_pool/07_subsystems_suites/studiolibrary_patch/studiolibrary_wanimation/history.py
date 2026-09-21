"""Non-destructive asset history stored inside each Studio Library item."""

from __future__ import absolute_import, print_function

import copy
import datetime
import io
import json
import os
import re
import shutil
import tempfile
import time


HISTORY_FOLDER = ".history"
ENTRY_FILENAME = "history_entry.json"
VIRTUAL_FIELD = "__plus_history__"
VERSION_PATTERN = re.compile(r"^v(\d+)$", re.IGNORECASE)


def _norm(path):
    return os.path.normcase(os.path.abspath(path))


def is_history_path(path):
    """Return whether *path* is located inside a PlusPatch history folder."""
    token = os.sep + HISTORY_FOLDER + os.sep
    value = _norm(path) + os.sep
    return token in value


def history_path(asset_path):
    return os.path.join(asset_path, HISTORY_FOLDER)


def _class_path(item):
    cls = item.__class__
    return cls.__module__ + "." + cls.__name__


def _write_json(path, data):
    with io.open(path, "w", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.write(u"\n")


def _read_json(path):
    try:
        with io.open(path, "r", encoding="utf-8-sig") as stream:
            return json.load(stream)
    except (IOError, OSError, ValueError):
        return {}


def _next_version(folder):
    latest = 0
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            match = VERSION_PATTERN.match(name)
            if match:
                latest = max(latest, int(match.group(1)))
    return "v{0:04d}".format(latest + 1)


def _copy_asset(source, destination):
    """Copy the current asset payload without recursively copying history."""
    def ignore(_root, names):
        return [name for name in names if name == HISTORY_FOLDER]

    shutil.copytree(source, destination, ignore=ignore)


def stage_existing_asset(asset_path, item):
    """Stage an existing asset before Studio Library replaces it.

    The stage folder is created beside the asset so moving an existing history
    tree is normally an atomic operation on the same volume.
    """
    if not os.path.isdir(asset_path):
        return None
    if not getattr(item, "EXTENSION", ""):
        return None
    if is_history_path(asset_path):
        return None

    parent = os.path.dirname(asset_path)
    stage = tempfile.mkdtemp(prefix=".studiolibrary_plus_history_", dir=parent)
    staged_history = os.path.join(stage, "history")
    snapshot = os.path.join(stage, "snapshot")
    source_history = history_path(asset_path)

    try:
        if os.path.isdir(source_history):
            shutil.move(source_history, staged_history)
        _copy_asset(asset_path, snapshot)
    except Exception:
        if os.path.isdir(staged_history) and not os.path.exists(source_history):
            shutil.move(staged_history, source_history)
        shutil.rmtree(stage, ignore_errors=True)
        raise

    return {
        "stage": stage,
        "snapshot": snapshot,
        "history": staged_history,
        "assetPath": asset_path,
        "class": _class_path(item),
        "createdEpoch": time.time(),
        "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def restore_stage(stage_data):
    """Restore history after a cancelled/failed overwrite when possible."""
    if not stage_data:
        return True
    stage = stage_data["stage"]
    asset_path = stage_data["assetPath"]
    staged_history = stage_data["history"]
    target_history = history_path(asset_path)

    if os.path.isdir(staged_history):
        if not os.path.isdir(asset_path):
            return False
        if os.path.exists(target_history):
            shutil.rmtree(target_history)
        shutil.move(staged_history, target_history)

    shutil.rmtree(stage, ignore_errors=True)
    return True


def _merge_history(source, destination):
    if not os.path.isdir(source):
        return
    if not os.path.isdir(destination):
        os.makedirs(destination)
    for name in os.listdir(source):
        source_path = os.path.join(source, name)
        destination_path = os.path.join(destination, name)
        if os.path.exists(destination_path):
            if os.path.isdir(destination_path):
                shutil.rmtree(destination_path)
            else:
                os.remove(destination_path)
        shutil.move(source_path, destination_path)


def commit_stage(stage_data, asset_path):
    """Attach the staged asset as the next version of the newly saved item."""
    if not stage_data:
        return None
    if not os.path.isdir(asset_path):
        raise IOError("The saved asset directory does not exist: {0}".format(asset_path))

    destination_history = history_path(asset_path)
    if not os.path.isdir(destination_history):
        os.makedirs(destination_history)
    _merge_history(stage_data["history"], destination_history)

    version = _next_version(destination_history)
    version_path = os.path.join(destination_history, version)
    shutil.move(stage_data["snapshot"], version_path)

    entry = {
        "version": version,
        "created": stage_data["created"],
        "createdEpoch": stage_data["createdEpoch"],
        "sourcePath": stage_data["assetPath"],
        "sourceClass": stage_data["class"],
    }
    _write_json(os.path.join(version_path, ENTRY_FILENAME), entry)
    os.utime(version_path, (stage_data["createdEpoch"], stage_data["createdEpoch"]))
    shutil.rmtree(stage_data["stage"], ignore_errors=True)
    return version_path


def history_versions(asset_path):
    folder = history_path(asset_path)
    if not os.path.isdir(folder):
        return []
    result = []
    for name in os.listdir(folder):
        if VERSION_PATTERN.match(name):
            path = os.path.join(folder, name)
            if os.path.isdir(path):
                result.append(path)
    return sorted(result, reverse=True)


def _history_item(parent_item, version_path, library):
    cls = parent_item.__class__
    item = cls(
        version_path,
        library=library,
        libraryWindow=getattr(library, "_libraryWindow", None),
    )
    item.setPath(version_path)
    if hasattr(item, "setReadOnly"):
        item.setReadOnly(True)

    parent_data = copy.deepcopy(parent_item.itemData())
    entry = _read_json(os.path.join(version_path, ENTRY_FILENAME))
    version = os.path.basename(version_path)
    created = entry.get("created") or datetime.datetime.fromtimestamp(
        os.path.getmtime(version_path)
    ).strftime("%Y-%m-%d %H:%M:%S")
    created_epoch = entry.get("createdEpoch") or os.path.getmtime(version_path)
    source_name = parent_data.get("name") or os.path.basename(parent_item.path())

    parent_data.update({
        "name": u"{0} · {1} · {2}".format(source_name, version, created),
        "path": version_path,
        "folder": parent_item.itemData().get("folder"),
        "category": parent_item.itemData().get("category"),
        "modified": created_epoch,
        "historyVersion": version,
        "historySource": parent_item.path(),
        VIRTUAL_FIELD: True,
        "__class__": _class_path(parent_item),
    })
    item.setItemData(parent_data)
    return item


def inject_history_items(library, items):
    """Return base items plus read-only virtual history items."""
    base_items = [
        item for item in items
        if not item.itemData().get(VIRTUAL_FIELD)
    ]
    result = list(base_items)
    for parent_item in base_items:
        if not getattr(parent_item, "EXTENSION", ""):
            continue
        if is_history_path(parent_item.path()):
            continue
        for version_path in history_versions(parent_item.path()):
            try:
                result.append(_history_item(parent_item, version_path, library))
            except Exception:
                # One damaged snapshot must not prevent normal assets loading.
                continue
    return result
