import os
import sys
import json

import maya.cmds as cmds
import maya.mel as mel


def _resolveDocumentsDir():
    if sys.platform.startswith("win"):
        home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        return os.path.join(home, "Documents", "Documents")

    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Documents"),
        os.path.join(home, "My Documents"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    try:
        os.makedirs(candidates[0])
        return candidates[0]
    except Exception:
        return home


MIRROR_SETTINGS_DIR = os.path.join(_resolveDocumentsDir(), "Animo_Mirror_Settings")
MIRROR_TABLE_PATH = os.path.join(MIRROR_SETTINGS_DIR, "animo_mirror_settings.json")

AXIS_INDEX = {"X": 0, "Y": 1, "Z": 2}
FLIPPABLE_ATTR_PREFIXES = ("translate", "rotate", "scale")


def _warn(message):
    cmds.warning(message)


def _showNoChannelBoxSelectionMessage():
    cmds.inViewMessage(
        amg="<hl>Please select an attribute in the Channel Box first.</hl>",
        pos="midCenter",
        fade=True,
        fadeStayTime=2000,
        fadeInTime=100,
        fadeOutTime=300,
        dragKill=True,
    )


def _showAxisFlippedMessage():
    cmds.inViewMessage(
        amg="<hl>Axis Flipped</hl>",
        pos="midCenter",
        fade=True,
        fadeStayTime=2000,
        fadeInTime=100,
        fadeOutTime=300,
        dragKill=True,
    )


def _getChannelBoxName():
    try:
        return mel.eval("$tempFlipAxisCbName = $gChannelBoxName")
    except Exception:
        return "mainChannelBox"


def _getSelectedChannelBoxAttrs():
    channelBox = _getChannelBoxName()

    try:
        if not cmds.channelBox(channelBox, exists=True):
            return []
    except Exception:
        return []

    attrs = []
    for flag in ("selectedMainAttributes", "selectedShapeAttributes",
                 "selectedHistoryAttributes", "selectedOutputAttributes"):
        try:
            result = cmds.channelBox(channelBox, query=True, **{flag: True})
        except Exception:
            result = None
        if result:
            attrs.extend(result)

    return attrs


def _axisFromAttr(obj, attr):
    longName = attr
    try:
        if cmds.attributeQuery(attr, node=obj, exists=True):
            longName = cmds.attributeQuery(attr, node=obj, longName=True) or attr
    except Exception:
        longName = attr

    if not longName.startswith(FLIPPABLE_ATTR_PREFIXES):
        return None

    axisLetter = longName[-1].upper()
    return AXIS_INDEX.get(axisLetter)


def _loadTable():
    if not os.path.exists(MIRROR_TABLE_PATH):
        return None
    try:
        with open(MIRROR_TABLE_PATH, "r") as f:
            content = f.read().strip()
            return json.loads(content) if content else None
    except Exception:
        return None


def _saveTable(table):
    outputDir = os.path.dirname(MIRROR_TABLE_PATH)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    with open(MIRROR_TABLE_PATH, "w") as f:
        json.dump(table, f, indent=2)


def flipSelectedAxes():
    selectedAttrs = _getSelectedChannelBoxAttrs()
    if not selectedAttrs:
        _showNoChannelBoxSelectionMessage()
        return

    objects = cmds.ls(selection=True) or []
    if not objects:
        _warn("Select the control(s) you want to flip axes for and try again.")
        return

    table = _loadTable()
    if not table or not table.get("controls"):
        _warn("No mirror table was found. Run the mirror setup first.")
        return

    controls = table["controls"]
    flippedControls = []
    skippedControls = []
    processedFlips = set()

    for obj in objects:
        entry = controls.get(obj)
        if not entry or "axis" not in entry:
            skippedControls.append(obj)
            continue

        axisIndices = set()
        for attr in selectedAttrs:
            axisIndex = _axisFromAttr(obj, attr)
            if axisIndex is not None:
                axisIndices.add(axisIndex)

        if not axisIndices:
            skippedControls.append(obj)
            continue

        partner = entry.get("partner")
        partnerEntry = controls.get(partner) if partner else None

        flippedAny = False
        for axisIndex in axisIndices:
            pairKey = (frozenset((obj, partner)) if partner else obj, axisIndex)
            if pairKey in processedFlips:
                continue
            processedFlips.add(pairKey)

            entry["axis"][axisIndex] *= -1
            if partnerEntry and "axis" in partnerEntry:
                partnerEntry["axis"][axisIndex] *= -1
            flippedAny = True

        if flippedAny:
            flippedControls.append(obj)
        else:
            skippedControls.append(obj)

    if not flippedControls:
        _warn("None of the selected control(s) had a matching axis entry to flip.")
        return

    _saveTable(table)

    _showAxisFlippedMessage()

    if skippedControls:
        preview = ", ".join(o.split("|")[-1] for o in skippedControls[:5])
        if len(skippedControls) > 5:
            preview += ", +{0} more".format(len(skippedControls) - 5)
        _warn("Flipped {0} control(s). Skipped {1} control(s) with no matching "
              "entry ({2}).".format(len(flippedControls), len(skippedControls), preview))


flipSelectedAxes()