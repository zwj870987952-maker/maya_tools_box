"""World-space pose capture, matching, blending, mirroring, and loading."""

from __future__ import absolute_import

import collections
import io
import json
import math
import os

import maya.cmds
import maya.api.OpenMaya as maya_open_maya

import mutils

from .worldanimation import WORLD_ATTRIBUTES, _long_names, _unlocked_attributes


SCHEMA_VERSION = 1
WORLD_POSE_FILENAME = "world_pose.json"


def _matrix_multiply(left, right):
    result = [0.0] * 16
    for row in range(4):
        for column in range(4):
            result[row * 4 + column] = sum(
                float(left[row * 4 + index]) * float(right[index * 4 + column])
                for index in range(4)
            )
    return result


def _axis_matrix(values):
    return [
        float(values[0]), 0.0, 0.0, 0.0,
        0.0, float(values[1]), 0.0, 0.0,
        0.0, 0.0, float(values[2]), 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]


def _mirrored_matrix(matrix, local_axis, world_plane):
    # Maya transform matrices use row-vector convention. Multiplying the
    # local-axis reflection on the left and world-plane reflection on the
    # right preserves a right-handed transform while reflecting its position.
    return _matrix_multiply(
        _matrix_multiply(_axis_matrix(local_axis), matrix),
        _axis_matrix(world_plane),
    )


def _matrix_components(matrix):
    transform = maya_open_maya.MTransformationMatrix(
        maya_open_maya.MMatrix(matrix)
    )
    translation = transform.translation(maya_open_maya.MSpace.kWorld)
    rotation = transform.rotation(asQuaternion=True)
    return [translation.x, translation.y, translation.z], rotation


def _rotation_values(quaternion, destination):
    rotation = quaternion.asEulerRotation()
    try:
        order = int(maya.cmds.getAttr(destination + ".rotateOrder"))
        rotation.reorderIt(order)
    except (RuntimeError, ValueError):
        pass
    return [
        math.degrees(rotation.x),
        math.degrees(rotation.y),
        math.degrees(rotation.z),
    ]


def _blend_components(base_matrix, target_matrix, blend, additive, destination):
    base_position, base_rotation = _matrix_components(base_matrix)
    target_position, target_rotation = _matrix_components(target_matrix)
    factor = float(blend) / 100.0

    if additive:
        position = [
            base_position[index] + target_position[index] * factor
            for index in range(3)
        ]
        delta = maya_open_maya.MQuaternion.slerp(
            maya_open_maya.MQuaternion(), target_rotation, factor
        )
        rotation = base_rotation * delta
    else:
        position = [
            base_position[index] +
            (target_position[index] - base_position[index]) * factor
            for index in range(3)
        ]
        rotation = maya_open_maya.MQuaternion.slerp(
            base_rotation, target_rotation, factor
        )
    return position, _rotation_values(rotation, destination)


def _source_lookup(objects, name):
    if name in objects:
        return name
    stripped = name.lstrip("|")
    for candidate in objects:
        if candidate.lstrip("|") == stripped:
            return candidate
    short_name = stripped.rsplit("|", 1)[-1]
    matches = [candidate for candidate in objects
               if candidate.rsplit("|", 1)[-1] == short_name]
    return matches[0] if len(matches) == 1 else None


def _mirror_axis(mirror_table, name, world_plane):
    keys = list(mirror_table.objects().keys())
    candidate = _source_lookup(dict((key, None) for key in keys), name)
    if candidate:
        try:
            return mirror_table.mirrorAxis(candidate)
        except (KeyError, RuntimeError):
            pass
    return list(world_plane)


def _matches(world_pose, objects=None, namespaces=None, search_replace=None):
    search = None
    replace = None
    if search_replace:
        search, replace = search_replace
    matches = mutils.matchNames(
        list(world_pose.objects.keys()),
        dstObjects=objects or [],
        dstNamespaces=namespaces or [],
        search=search,
        replace=replace,
    )
    result = []
    for source_node, destination_node in matches:
        source_name = source_node.name()
        destinations = maya.cmds.ls(destination_node.name(), long=True) or []
        source_name = _source_lookup(world_pose.objects, source_name)
        if source_name and destinations:
            result.append((source_name, destinations[0]))
    result.sort(key=lambda pair: pair[1].count("|"))
    return result


class WorldPose(object):
    """Serializable world matrices for a single Maya pose."""

    def __init__(self, data=None):
        self._data = data or collections.OrderedDict()
        self._cache_key = None
        self._base_matrices = {}

    @property
    def data(self):
        return self._data

    @property
    def objects(self):
        return self._data.get("objects", collections.OrderedDict())

    @classmethod
    def capture(cls, objects):
        objects = _long_names(objects)
        if not objects:
            raise ValueError("No valid Maya objects were supplied")
        data = collections.OrderedDict()
        data["schemaVersion"] = SCHEMA_VERSION
        data["objects"] = collections.OrderedDict()
        for obj in objects:
            data["objects"][obj] = collections.OrderedDict([
                ("name", obj.rsplit("|", 1)[-1]),
                ("matrix", list(maya.cmds.xform(
                    obj, query=True, worldSpace=True, matrix=True
                ))),
                ("position", list(maya.cmds.xform(
                    obj, query=True, worldSpace=True, translation=True
                ))),
                ("rotation", list(maya.cmds.xform(
                    obj, query=True, worldSpace=True, rotation=True
                ))),
            ])
        return cls(data)

    @classmethod
    def from_path(cls, path):
        with io.open(path, "r", encoding="utf-8-sig") as stream:
            data = json.load(stream, object_pairs_hook=collections.OrderedDict)
        if int(data.get("schemaVersion", 0)) != SCHEMA_VERSION:
            raise ValueError("Unsupported WPose world-pose schema")
        return cls(data)

    def save(self, path):
        temporary = path + ".tmp"
        with io.open(temporary, "w", encoding="utf-8") as stream:
            json.dump(self.data, stream, indent=2, ensure_ascii=False)
            stream.write(u"\n")
        if os.path.exists(path):
            os.remove(path)
        os.rename(temporary, path)

    def _target_matrix(self, source_name, mirror=False, mirror_table=None):
        target_source = source_name
        matrix = self.objects[source_name]["matrix"]
        if not mirror or not mirror_table:
            return matrix

        mirrored_name = mirror_table.mirrorObject(source_name)
        mirrored_source = _source_lookup(self.objects, mirrored_name) if mirrored_name else None
        if mirrored_source:
            target_source = mirrored_source
            matrix = self.objects[target_source]["matrix"]
        world_plane = mirror_table.mirrorPlane() or [-1, 1, 1]
        local_axis = _mirror_axis(mirror_table, target_source, world_plane)
        return _mirrored_matrix(matrix, local_axis, world_plane)

    def apply(self, objects=None, namespaces=None, blend=100.0, key=False,
              mirror=False, additive=False, mirror_table=None,
              search_replace=None, clear_cache=False, max_attempts=3):
        matches = _matches(
            self,
            objects=objects,
            namespaces=namespaces,
            search_replace=search_replace,
        )
        if not matches:
            raise mutils.NoMatchFoundError(
                "No objects match when loading WPose data"
            )

        cache_key = (
            tuple(matches), bool(mirror), str(search_replace),
            tuple(namespaces or []), tuple(objects or []),
        )
        if clear_cache or cache_key != self._cache_key:
            self._cache_key = cache_key
            self._base_matrices = dict(
                (destination, list(maya.cmds.xform(
                    destination, query=True, worldSpace=True, matrix=True
                )))
                for _source, destination in matches
            )

        editable = {}
        for _source, destination in matches:
            editable[destination] = _unlocked_attributes(
                destination, WORLD_ATTRIBUTES
            )

        report = {"matched": len(matches), "failed": []}
        for source_name, destination in matches:
            attributes = editable[destination]
            paste_position = any(name.startswith("translate") for name in attributes)
            paste_rotation = any(name.startswith("rotate") for name in attributes)
            if not paste_position and not paste_rotation:
                report["failed"].append({
                    "object": destination,
                    "reason": "No unlocked transform channels",
                })
                continue

            target_matrix = self._target_matrix(
                source_name, mirror=mirror, mirror_table=mirror_table
            )
            position, rotation = _blend_components(
                self._base_matrices[destination],
                target_matrix,
                blend,
                additive,
                destination,
            )
            failure = None
            for _attempt in range(max(1, int(max_attempts))):
                try:
                    if paste_position:
                        maya.cmds.xform(
                            destination, worldSpace=True, translation=position
                        )
                    if paste_rotation:
                        maya.cmds.xform(
                            destination, worldSpace=True, rotation=rotation
                        )
                    failure = None
                    break
                except RuntimeError as error:
                    failure = str(error)
            if failure:
                report["failed"].append({
                    "object": destination,
                    "reason": failure,
                })
                continue

            if key and attributes:
                try:
                    maya.cmds.setKeyframe(destination, attribute=attributes)
                except RuntimeError as error:
                    report["failed"].append({
                        "object": destination,
                        "reason": str(error),
                    })
        return report


def _non_world_attributes(pose, requested=None):
    attributes = set()
    for object_data in pose.objects().values():
        attributes.update(object_data.get("attrs", {}).keys())
    attributes.difference_update(WORLD_ATTRIBUTES)
    if requested:
        attributes.intersection_update(requested)
    return sorted(attributes)


def load_wpose(path, objects=None, namespaces=None, attrs=None, blend=100.0,
               key=False, mirror=False, additive=False, refresh=True,
               batchMode=False, clearCache=False, mirrorTable=None,
               onlyConnected=False, clearSelection=True,
               ignoreConnected=False, searchAndReplace=None, maxAttempts=3,
               pose=None, worldPose=None, **_kwargs):
    """Load WPose attributes and world transforms as one undo operation."""
    pose = pose or mutils.Pose.fromPath(os.path.join(path, "pose.json"))
    world_pose = worldPose or WorldPose.from_path(
        os.path.join(path, WORLD_POSE_FILENAME)
    )
    if mirror and not mirrorTable:
        mirror = False
    if batchMode:
        key = False

    non_world = _non_world_attributes(pose, requested=attrs)
    if non_world:
        pose.updateCache(
            objects=objects,
            namespaces=namespaces,
            attrs=non_world,
            ignoreConnected=ignoreConnected,
            onlyConnected=onlyConnected,
            mirrorTable=mirrorTable,
            batchMode=batchMode,
            clearCache=clearCache,
            searchAndReplace=searchAndReplace,
        )

    pose.beforeLoad(clearSelection=clearSelection)
    failed = True
    try:
        if non_world:
            pose.loadCache(
                blend=blend, key=key, mirror=mirror, additive=additive
            )
        world_requested = not attrs or any(name in WORLD_ATTRIBUTES for name in attrs)
        if world_requested:
            report = world_pose.apply(
                objects=objects,
                namespaces=namespaces,
                blend=blend,
                key=key,
                mirror=mirror,
                additive=additive,
                mirror_table=mirrorTable,
                search_replace=searchAndReplace,
                clear_cache=clearCache,
                max_attempts=maxAttempts,
            )
        else:
            report = {"matched": 0, "failed": []}
        failed = False
        return report
    finally:
        if not batchMode or failed:
            pose.afterLoad()
            try:
                maya.cmds.setFocus("MayaWindow")
            except RuntimeError:
                pass
            if refresh:
                maya.cmds.refresh(cv=True)
