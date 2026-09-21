"""Studio Library WPose asset with world-space transform loading."""

from __future__ import absolute_import

import os

import maya.cmds

from studiolibrarymaya import poseitem

from .worldpose import WORLD_POSE_FILENAME, WorldPose, load_wpose


PACKAGE_PATH = os.path.dirname(__file__)


class WPoseLoadWidget(poseitem.PoseLoadWidget):
    """Pose-compatible blend UI backed by world-space transforms."""

    @classmethod
    def createFromPath(cls, path, theme=None):
        item = WPoseItem(path)
        widget = cls(item)
        if not theme:
            import studiolibrary.widgets
            theme = studiolibrary.widgets.Theme()
            widget.setStyleSheet(theme.styleSheet())
        widget.show()
        return widget

    def __init__(self, *args, **kwargs):
        super(WPoseLoadWidget, self).__init__(*args, **kwargs)
        self._world_pose = WorldPose.from_path(
            os.path.join(self.item().path(), WORLD_POSE_FILENAME)
        )

    def load(self, blend=100.0, refresh=True, batchMode=False,
             clearCache=False, clearSelection=True):
        if batchMode:
            self.formWidget().setValidatorEnabled(False)
        else:
            self.formWidget().setValidatorEnabled(True)

        if not self._options:
            self._options = self.formWidget().values()
            self._options["mirrorTable"] = self.item().mirrorTable()
            self._options["objects"] = maya.cmds.ls(selection=True) or []
            if not self._options["searchAndReplaceEnabled"]:
                self._options["searchAndReplace"] = None
            del self._options["namespaceOption"]
            del self._options["searchAndReplaceEnabled"]

        self.ui.blendEdit.blockSignals(True)
        self.ui.blendSlider.setValue(blend)
        self.ui.blendEdit.setText(str(int(blend)))
        self.ui.blendEdit.blockSignals(False)

        if self.item().libraryWindow():
            items_widget = self.item().libraryWindow().itemsWidget()
            items_widget.blockSignals(True)
            self.item().setSliderValue(blend)
            items_widget.blockSignals(False)
            if batchMode:
                self.item().libraryWindow().showToastMessage(
                    "Blend: {0}%".format(blend)
                )

        try:
            return load_wpose(
                self.item().path(),
                blend=blend,
                refresh=refresh,
                batchMode=batchMode,
                clearCache=clearCache,
                clearSelection=clearSelection,
                pose=self._pose,
                worldPose=self._world_pose,
                **self._options
            )
        finally:
            self.item().setSliderDown(batchMode)


class WPoseItem(poseitem.PoseItem):
    """Pose asset whose translate/rotate result is restored in world space."""

    NAME = "WPose"
    EXTENSION = ".wpose"
    TYPE = "WPose"
    ICON_PATH = os.path.join(PACKAGE_PATH, "icons", "world_pose.svg")
    TYPE_ICON_PATH = ICON_PATH
    LOAD_WIDGET_CLASS = WPoseLoadWidget

    def save(self, objects, **kwargs):
        objects = maya.cmds.ls(objects or [], long=True) or []
        if not objects:
            raise ValueError("No valid Maya objects were supplied")
        world_pose = WorldPose.capture(objects)
        super(WPoseItem, self).save(objects, **kwargs)
        world_pose.save(os.path.join(self.path(), WORLD_POSE_FILENAME))

    def load(self, objects=None, namespaces=None, **kwargs):
        report = load_wpose(
            self.path(), objects=objects, namespaces=namespaces, **kwargs
        )
        if report["failed"]:
            maya.cmds.warning(
                "WPose loaded with {0} unresolved result(s)."
                .format(len(report["failed"]))
            )
        return report
