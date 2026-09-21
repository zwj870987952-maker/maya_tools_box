"""Studio Library WAnimation asset item."""

from __future__ import absolute_import

import os
import shutil

import maya.cmds

import mutils

from studiolibrarymaya import animitem
from studiolibrarymaya import baseitem

from .savewidget import WAnimationSaveWidget
from .worldanimation import WORLD_FILENAME, WorldAnimation, load_wanimation
from .worldanimation import WORLD_ATTRIBUTES


PACKAGE_PATH = os.path.dirname(__file__)


class WAnimationItem(animitem.AnimItem):
    """Animation asset whose transforms are stored and pasted in world space."""

    NAME = "WAnimation"
    EXTENSION = ".wanim"
    TYPE = "WAnimation"
    ICON_PATH = os.path.join(PACKAGE_PATH, "icons", "world_animation.svg")
    TYPE_ICON_PATH = ICON_PATH
    SAVE_WIDGET_CLASS = WAnimationSaveWidget

    def loadSchema(self):
        schema = super(WAnimationItem, self).loadSchema()
        for field in schema:
            if field.get("name") == "connect":
                field["title"] = "Connect Custom Attributes"
                field["toolTip"] = (
                    "Connect applies to non-transform animation. World-space "
                    "translate and rotate channels are baked as local keys."
                )

        schema.extend([
            {
                "name": "worldOptionsGroup",
                "type": "group",
                "title": "World Space",
                "order": 3,
            },
            {
                "name": "pastePosition",
                "type": "bool",
                "title": "Paste Position",
                "default": True,
                "persistent": True,
            },
            {
                "name": "pasteRotation",
                "type": "bool",
                "title": "Paste Rotation",
                "default": True,
                "persistent": True,
            },
            {
                "name": "maxAttempts",
                "type": "int",
                "title": "Solve Attempts",
                "default": 3,
                "minimum": 1,
                "maximum": 50,
                "persistent": True,
            },
        ])
        return schema

    def saveValidator(self, **kwargs):
        fields = baseitem.BaseItem.saveValidator(self, **kwargs)
        start, end = kwargs.get("frameRange", (0, 0))
        if float(start) >= float(end):
            fields.append({
                "name": "frameRange",
                "error": "The start frame must be less than the end frame",
            })
        by_frame = kwargs.get("byFrame", 1)
        if by_frame == "" or int(by_frame) < 1:
            fields.append({
                "name": "byFrame",
                "error": "By frame must be greater than zero",
            })
        return fields

    def _save_pose_only(self, objects, frame_range, metadata=None):
        animation = mutils.Animation.fromObjects(objects)
        animation.setMetadata("startFrame", float(frame_range[0]))
        animation.setMetadata("endFrame", float(frame_range[1]))
        animation.updateMetadata(metadata or {})
        mutils.Pose.save(animation, os.path.join(self.path(), "pose.json"))

    @staticmethod
    def _has_non_world_animation(objects, frame_range, bake_connected=False):
        for obj in objects:
            attributes = maya.cmds.listAttr(
                obj, keyable=True, unlocked=True
            ) or []
            for attribute in attributes:
                if attribute in WORLD_ATTRIBUTES:
                    continue
                plug = "{0}.{1}".format(obj, attribute)
                try:
                    count = maya.cmds.keyframe(
                        plug,
                        query=True,
                        keyframeCount=True,
                        time=tuple(frame_range),
                    ) or 0
                except RuntimeError:
                    count = 0
                if count:
                    return True
                if bake_connected:
                    connections = maya.cmds.listConnections(
                        plug, source=True, destination=False
                    ) or []
                    if connections:
                        return True
        return False

    @staticmethod
    def _world_animation_from_data(data, objects, frame_range):
        if not data:
            return None
        animation = WorldAnimation(data)
        if (abs(animation.start_frame - float(frame_range[0])) > 0.0001 or
                abs(animation.end_frame - float(frame_range[1])) > 0.0001):
            return None
        if set(animation.objects.keys()) != set(objects):
            return None
        return animation

    def save(self, objects=None, sequencePath="", **kwargs):
        objects = maya.cmds.ls(objects or [], long=True) or []
        if not objects:
            raise ValueError("No valid Maya objects were supplied")

        frame_range = kwargs.get("frameRange")
        thumbnail = kwargs.get("thumbnail", "")
        metadata = {"description": kwargs.get("comment", "")}
        world_animation = self._world_animation_from_data(
            kwargs.pop("worldAnimationData", None), objects, frame_range
        )
        if world_animation is None:
            world_animation = WorldAnimation.capture(
                objects, frame_range, sample_by=1.0
            )
        baseitem.BaseItem.save(self, **kwargs)

        has_standard_animation = self._has_non_world_animation(
            objects,
            frame_range,
            bake_connected=bool(kwargs.get("bakeConnected")),
        )

        if has_standard_animation:
            mutils.saveAnim(
                objects,
                self.path(),
                time=frame_range,
                fileType=kwargs.get("fileType"),
                iconPath=thumbnail,
                metadata=metadata,
                sequencePath=sequencePath,
                bakeConnected=kwargs.get("bakeConnected"),
            )
        else:
            self._save_pose_only(objects, frame_range, metadata=metadata)
            if sequencePath and os.path.exists(sequencePath):
                destination = self.imageSequencePath()
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.move(sequencePath, destination)

        world_animation.save(os.path.join(self.path(), WORLD_FILENAME))

    def load(self, objects=None, namespaces=None, startFrame=None,
             sourceTime=None, option="replace", connect=False,
             currentTime=False, pastePosition=True, pasteRotation=True,
             maxAttempts=3, fullCheckAttempts=0, **kwargs):
        report = load_wanimation(
            self.path(),
            objects=objects,
            namespaces=namespaces,
            start_frame=startFrame,
            source_time=sourceTime,
            option=option,
            connect=connect,
            current_time=currentTime,
            paste_position=pastePosition,
            paste_rotation=pasteRotation,
            max_attempts=maxAttempts,
            full_check_attempts=fullCheckAttempts,
        )
        if report["failed"]:
            maya.cmds.warning(
                "WAnimation pasted {0} frames with {1} unresolved result(s)."
                .format(report["frames"], len(report["failed"]))
            )
        return report
