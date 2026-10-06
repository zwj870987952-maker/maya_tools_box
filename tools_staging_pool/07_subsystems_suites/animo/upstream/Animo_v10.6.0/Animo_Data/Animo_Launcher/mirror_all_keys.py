import os
import sys
import importlib.util

import maya.cmds as cmds

def _resolveIconsDir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass

    for path in sys.path:
        candidate = os.path.join(path, "mirror_launcher.py")
        if os.path.exists(candidate):
            return path

    try:
        version_script_dir = cmds.internalVar(userScriptDir=True)
        script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts", "Animo_Data"))
        return os.path.join(script_dir, "Animo_Launcher")
    except Exception:
        return os.getcwd()


_THIS_DIR = _resolveIconsDir()
_MIRROR_LAUNCHER_PATH = os.path.join(_THIS_DIR, "mirror_launcher.py")


try:
    import builtins
except ImportError:
    import __builtin__ as builtins


def _loadMirrorLauncherCore():
    if not os.path.exists(_MIRROR_LAUNCHER_PATH):
        cmds.warning("mirror_launcher.py not found next to mirror_all_keys.py or on sys.path.")
        return None

    flagName = "_ANIMO_MIRROR_LAUNCHER_SUPPRESS_AUTORUN"
    previousFlag = getattr(builtins, flagName, False)
    setattr(builtins, flagName, True)

    try:
        spec = importlib.util.spec_from_file_location("mirror_launcher_core", _MIRROR_LAUNCHER_PATH)
        module = importlib.util.module_from_spec(spec)
        sys.modules["mirror_launcher_core"] = module
        spec.loader.exec_module(module)
    finally:
        setattr(builtins, flagName, previousFlag)

    return module


ML = _loadMirrorLauncherCore()


def _getFullKeyRange(objects):
    allTimes = []
    for obj in objects:
        times = cmds.keyframe(obj, q=True, timeChange=True) or []
        allTimes.extend(times)
    if not allTimes:
        return None, None
    return min(allTimes), max(allTimes)


def applyMirrorAllKeys(objects, tableObjects):
    partnerOf = {}
    for obj in objects:
        storedPartner = tableObjects.get(obj, {}).get("partner")
        if storedPartner and cmds.objExists(storedPartner):
            partnerOf[obj] = storedPartner
        else:
            partnerOf[obj] = obj

    startRange, endRange = _getFullKeyRange(objects)
    if startRange is None:
        ML._warn("No keys were found on the selected control(s) to mirror.")
        return

    touchedSrc = set()

    cmds.undoInfo(openChunk=True, chunkName="mirrorAllKeysApply")
    try:
        mirroredKeys, touchedSrc, cancelled = ML.mirrorTimeRange(
            objects, partnerOf, tableObjects, startRange, endRange)

        dirtyObjs = set(partnerOf.get(src, src) for src in touchedSrc)
        if dirtyObjs:
            try:
                cmds.dgdirty(list(dirtyObjs))
            except (RuntimeError, TypeError):
                pass

        if dirtyObjs:
            try:
                cmds.select(list(dirtyObjs), replace=True)
            except (RuntimeError, TypeError):
                pass
    finally:
        cmds.undoInfo(closeChunk=True)
        cmds.setFocus("MayaWindow")

    cmds.refresh(force=True)

    if mirroredKeys == 0 and not cancelled:
        ML._warn("No keys were found on the selected control(s) to mirror.")
    elif cancelled:
        ML._warn("Mirroring stopped early (Esc) - mirrored {0} key(s) before stopping.".format(mirroredKeys))


def mirrorAllKeysTool():
    if ML is None:
        return

    userSelection = cmds.ls(selection=True) or []
    if not userSelection:
        ML._warn("Select the source control(s) you want to mirror from and try again.")
        return

    table = ML.loadTable()

    if not ML.tableCoversSelection(table, userSelection):
        table = ML.resetPoseAndSaveMirrorTable(userSelection, existingTable=table)
        if not table:
            return

    tableObjects = table.get("controls", {})
    applyMirrorAllKeys(userSelection, tableObjects)


mirrorAllKeysTool()