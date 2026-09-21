"""World-space animation capture and paste helpers for Maya.

The implementation deliberately lives outside Studio Library's core packages so
that the extension can be re-installed after Studio Library is upgraded.
"""

from __future__ import absolute_import

import collections
import io
import json
import os

import maya.cmds

try:
    import maya.api.OpenMaya as maya_open_maya
except ImportError:
    maya_open_maya = None

import mutils
import mutils.animation as animation_module


SCHEMA_VERSION = 1
WORLD_FILENAME = "world_transform.json"
WORLD_ATTRIBUTES = (
    "translateX", "translateY", "translateZ",
    "rotateX", "rotateY", "rotateZ",
)


def _frame_values(start, end, sample_by=1.0):
    """Return an inclusive list of sample times."""
    start = float(start)
    end = float(end)
    sample_by = float(sample_by)
    if sample_by <= 0:
        raise ValueError("sample_by must be greater than zero")
    if end < start:
        raise ValueError("End frame must not be less than start frame")

    values = []
    value = start
    epsilon = sample_by * 0.0001
    while value <= end + epsilon:
        values.append(round(value, 6))
        value += sample_by
    if values and values[-1] < end - epsilon:
        values.append(end)
    return values


def _angle_close(value1, value2, tolerance):
    delta = ((float(value1) - float(value2) + 180.0) % 360.0) - 180.0
    return abs(delta) <= tolerance


def _vector_close(value1, value2, tolerance, angular=False):
    if angular:
        return all(_angle_close(a, b, tolerance) for a, b in zip(value1, value2))
    return all(abs(float(a) - float(b)) <= tolerance for a, b in zip(value1, value2))


def _long_names(objects):
    result = []
    for obj in objects or []:
        matches = maya.cmds.ls(obj, long=True) or []
        if matches:
            result.append(matches[0])
    return result


def _unlocked_attributes(node, attributes):
    result = []
    for attribute in attributes:
        name = "{0}.{1}".format(node, attribute)
        if not maya.cmds.objExists(name):
            continue
        try:
            if maya.cmds.getAttr(name, lock=True):
                continue
        except (RuntimeError, ValueError):
            continue
        result.append(attribute)
    return result


def _has_animation_file(animation):
    return bool(animation.mayaPath() and os.path.exists(animation.mayaPath()))


class WorldAnimation(object):
    """Serializable, per-frame world transform data."""

    def __init__(self, data=None):
        self._data = data or collections.OrderedDict()

    @property
    def data(self):
        return self._data

    @property
    def start_frame(self):
        return float(self._data.get("startFrame", 0.0))

    @property
    def end_frame(self):
        return float(self._data.get("endFrame", self.start_frame))

    @property
    def sample_by(self):
        return float(self._data.get("sampleBy", 1.0))

    @property
    def objects(self):
        return self._data.get("objects", collections.OrderedDict())

    @classmethod
    def capture(cls, objects, frame_range, sample_by=1.0):
        """Capture world translation and rotation for every requested frame."""
        collector = WorldAnimationCollector(objects, frame_range, sample_by)
        current_time = maya.cmds.currentTime(query=True)
        selection = maya.cmds.ls(selection=True, long=True) or []

        try:
            for frame in collector.expected_frames:
                maya.cmds.currentTime(frame, edit=True)
                collector.capture_frame(frame)
        finally:
            maya.cmds.currentTime(current_time, edit=True)
            maya.cmds.select(selection, replace=True) if selection else maya.cmds.select(clear=True)

        return collector.world_animation()

    @classmethod
    def from_path(cls, path):
        with io.open(path, "r", encoding="utf-8") as stream:
            data = json.load(stream, object_pairs_hook=collections.OrderedDict)
        if int(data.get("schemaVersion", 0)) != SCHEMA_VERSION:
            raise ValueError("Unsupported WAnimation schema version")
        return cls(data)

    def save(self, path):
        folder = os.path.dirname(path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        temporary_path = path + ".tmp"
        with io.open(temporary_path, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(self._data, stream, indent=2, ensure_ascii=False)
            stream.write(u"\n")
        if os.path.exists(path):
            os.remove(path)
        os.rename(temporary_path, path)

    def sample_map(self, source_start=None, source_end=None):
        source_start = self.start_frame if source_start is None else float(source_start)
        source_end = self.end_frame if source_end is None else float(source_end)
        result = collections.OrderedDict()
        for source_name, item in self.objects.items():
            frames = collections.OrderedDict()
            for sample in item.get("frames", []):
                frame = float(sample["time"])
                if source_start - 0.0001 <= frame <= source_end + 0.0001:
                    frames[frame] = sample
            result[source_name] = frames
        return result


class WorldAnimationCollector(object):
    """Collect world samples while another operation changes Maya's time."""

    def __init__(self, objects, frame_range, sample_by=1.0):
        self.objects = _long_names(objects)
        if not self.objects:
            raise ValueError("No valid Maya objects were supplied")
        self.start_frame = float(frame_range[0])
        self.end_frame = float(frame_range[1])
        self.sample_by = float(sample_by)
        self.expected_frames = _frame_values(
            self.start_frame, self.end_frame, self.sample_by
        )
        self._samples = collections.OrderedDict(
            (obj, {}) for obj in self.objects
        )
        self._callback_id = None

    def signature(self):
        return (
            tuple(self.objects),
            self.start_frame,
            self.end_frame,
            self.sample_by,
        )

    def _expected_frame(self, frame):
        frame = float(frame)
        for expected in self.expected_frames:
            if abs(expected - frame) <= 0.0001:
                return expected
        return None

    def capture_frame(self, frame=None):
        frame = maya.cmds.currentTime(query=True) if frame is None else frame
        frame = self._expected_frame(frame)
        if frame is None:
            return False
        if all(frame in values for values in self._samples.values()):
            return True

        for obj in self.objects:
            if frame in self._samples[obj] or not maya.cmds.objExists(obj):
                continue
            position = maya.cmds.xform(
                obj, query=True, worldSpace=True, translation=True
            )
            rotation = maya.cmds.xform(
                obj, query=True, worldSpace=True, rotation=True
            )
            self._samples[obj][frame] = {
                "time": float(frame),
                "position": [float(value) for value in position],
                "rotation": [float(value) for value in rotation],
            }
        return True

    def _time_changed(self, *args):
        try:
            self.capture_frame()
        except (RuntimeError, ValueError):
            # Playblast can briefly report an unavailable model state while it
            # switches render frames. Missing samples are handled by fallback.
            pass

    def start(self):
        if maya_open_maya is None or self._callback_id is not None:
            return False
        self._callback_id = maya_open_maya.MEventMessage.addEventCallback(
            "timeChanged", self._time_changed
        )
        self.capture_frame()
        return True

    def stop(self):
        if self._callback_id is not None and maya_open_maya is not None:
            maya_open_maya.MMessage.removeCallback(self._callback_id)
        self._callback_id = None

    def is_complete(self):
        expected = set(self.expected_frames)
        return all(set(values.keys()) == expected for values in self._samples.values())

    def world_animation(self):
        if not self.is_complete():
            raise ValueError("World transform collection is incomplete")
        data = collections.OrderedDict()
        data["schemaVersion"] = SCHEMA_VERSION
        data["startFrame"] = self.start_frame
        data["endFrame"] = self.end_frame
        data["sampleBy"] = self.sample_by
        data["objects"] = collections.OrderedDict()
        for obj in self.objects:
            data["objects"][obj] = collections.OrderedDict([
                ("name", obj.rsplit("|", 1)[-1]),
                ("frames", [self._samples[obj][frame]
                            for frame in self.expected_frames]),
            ])
        return WorldAnimation(data)


def _non_world_attributes(animation):
    attributes = set()
    for object_data in animation.objects().values():
        attributes.update(object_data.get("attrs", {}).keys())
    return sorted(attributes.difference(WORLD_ATTRIBUTES))


def _load_non_world_attributes(animation, objects=None, namespaces=None,
                               start_frame=None, source_time=None,
                               option="replace", connect=False,
                               current_time=False):
    """Load the standard payload without Animation.load's global flushUndo."""
    attributes = _non_world_attributes(animation)
    if not attributes:
        return []

    objects = objects or []
    namespaces = namespaces or []
    option = "replaceCompletely" if option == "replace all" else option

    if not _has_animation_file(animation):
        pose = mutils.Pose.fromPath(animation.poseJsonPath())
        return pose.load(
            objects=objects,
            namespaces=namespaces,
            attrs=attributes,
            clearSelection=False,
        )

    if not source_time:
        source_time = (animation.startFrame(), animation.endFrame())
    animation.validate(namespaces=namespaces)
    matches = list(mutils.matchNames(
        srcObjects=animation.objects().keys(),
        dstObjects=objects,
        dstNamespaces=namespaces,
    ))
    if not matches or not any(destination.exists() for _, destination in matches):
        raise mutils.NoMatchFoundError("No objects match when loading WAnimation data")
    source_curves = animation.open()
    loaded = []

    try:
        if current_time:
            start_frame = maya.cmds.currentTime(query=True)

        source_time = animation_module.findFirstLastKeyframes(source_curves, source_time)
        destination_time = animation_module.moveTime(source_time, start_frame)

        if option != "replaceCompletely":
            animation_module.insertKeyframe(source_curves, source_time)

        for source_node, destination_node in matches:
            destination_node.stripFirstPipe()
            for attribute in attributes:
                if attribute not in animation.attrs(source_node.name()):
                    continue
                destination_attribute = mutils.Attribute(
                    destination_node.name(), attribute
                )
                if not destination_attribute.exists():
                    continue
                source_curve = animation.animCurve(
                    source_node.name(), attribute, withNamespace=True
                )
                if source_curve:
                    destination_attribute.setAnimCurve(
                        source_curve,
                        time=destination_time,
                        option=option,
                        source=source_time,
                        connect=connect,
                    )
                    loaded.append(destination_attribute.fullname())
                else:
                    destination_attribute.setStaticKeyframe(
                        animation.attrValue(source_node.name(), attribute),
                        destination_time,
                        option,
                    )
                    loaded.append(destination_attribute.fullname())
    finally:
        animation.close()

    return loaded


def _match_world_objects(world_animation, objects=None, namespaces=None):
    source_names = list(world_animation.objects.keys())
    matches = mutils.matchNames(
        source_names,
        dstObjects=objects or [],
        dstNamespaces=namespaces or [],
    )
    result = []
    for source_node, destination_node in matches:
        source_name = source_node.name()
        destination_name = destination_node.name()
        destinations = maya.cmds.ls(destination_name, long=True) or []
        if source_name in world_animation.objects and destinations:
            result.append((source_name, destinations[0]))
    result.sort(key=lambda pair: pair[1].count("|"))
    return result


def _edit_destination_keys(matches, start, end, option, attributes):
    duration = max(0.0, float(end) - float(start))
    for _, destination in matches:
        editable = _unlocked_attributes(destination, attributes)
        for attribute in editable:
            plug = "{0}.{1}".format(destination, attribute)
            try:
                if option == "replace":
                    maya.cmds.cutKey(plug, time=(start, end), clear=True)
                elif option == "replace all":
                    maya.cmds.cutKey(plug, clear=True)
                elif option == "insert" and duration:
                    maya.cmds.keyframe(
                        plug,
                        edit=True,
                        relative=True,
                        time=(start, 1000000000.0),
                        timeChange=duration,
                    )
            except RuntimeError:
                # A missing curve during insert and non-keyable driven channels
                # are handled later by the xform/setKeyframe attempt.
                pass


def _progress_begin(total):
    if total <= 1 or maya.cmds.about(batch=True):
        return False
    try:
        maya.cmds.progressWindow(
            title="Paste WAnimation",
            progress=0,
            maximum=total,
            status="Preparing world transforms...",
            isInterruptable=True,
        )
        return True
    except RuntimeError:
        return False


def _progress_step(frame, index, update=False):
    if maya.cmds.progressWindow(query=True, isCancelled=True):
        return False
    if update:
        maya.cmds.progressWindow(
            edit=True,
            progress=index,
            status="Pasting frame {0:g}".format(frame),
        )
    return True


def _set_world_sample(destination, sample, paste_position, paste_rotation):
    if paste_position:
        maya.cmds.xform(
            destination,
            worldSpace=True,
            translation=sample["position"],
        )
    if paste_rotation:
        maya.cmds.xform(
            destination,
            worldSpace=True,
            rotation=sample["rotation"],
        )


def _position_error(destination, sample):
    actual = maya.cmds.xform(
        destination, query=True, worldSpace=True, translation=True
    )
    return max(abs(float(a) - float(b))
               for a, b in zip(actual, sample["position"]))


def paste_world_animation(world_animation, objects=None, namespaces=None,
                          start_frame=None, source_time=None, option="replace",
                          current_time=False, paste_position=True,
                          paste_rotation=True, max_attempts=10,
                          full_check_attempts=5, position_tolerance=0.001,
                          rotation_tolerance=0.01):
    """Paste world transforms and return a detailed operation report."""
    if not paste_position and not paste_rotation:
        raise ValueError("At least one world transform channel must be enabled")

    source_start = world_animation.start_frame
    source_end = world_animation.end_frame
    if source_time:
        source_start, source_end = [float(value) for value in source_time]
    source_start = max(source_start, world_animation.start_frame)
    source_end = min(source_end, world_animation.end_frame)
    if source_end < source_start:
        raise ValueError("The requested source range contains no WAnimation samples")

    if current_time:
        start_frame = maya.cmds.currentTime(query=True)
    if start_frame is None:
        start_frame = source_start
    start_frame = float(start_frame)

    matches = _match_world_objects(world_animation, objects, namespaces)
    if not matches:
        raise ValueError("No WAnimation objects matched the current scene")

    samples = world_animation.sample_map(source_start, source_end)
    source_frames = sorted(set(
        frame
        for source_name, _ in matches
        for frame in samples.get(source_name, {}).keys()
    ))
    if not source_frames:
        raise ValueError("The WAnimation asset contains no samples in this range")

    destination_end = start_frame + (source_frames[-1] - source_frames[0])
    attributes = []
    if paste_position:
        attributes.extend(WORLD_ATTRIBUTES[:3])
    if paste_rotation:
        attributes.extend(WORLD_ATTRIBUTES[3:])
    _edit_destination_keys(matches, start_frame, destination_end, option, attributes)

    editable_by_destination = collections.OrderedDict()
    key_groups = collections.OrderedDict()
    for _, destination in matches:
        editable = tuple(_unlocked_attributes(destination, attributes))
        editable_by_destination[destination] = editable
        if editable:
            key_groups.setdefault(editable, []).append(destination)

    report = {
        "matched": len(matches),
        "frames": 0,
        "failed": [],
        "cancelled": False,
    }
    failure_keys = set()

    def add_failure(frame, destination, reason):
        key = (float(frame), destination, reason)
        if key not in failure_keys:
            failure_keys.add(key)
            report["failed"].append({
                "frame": float(frame),
                "object": destination,
                "reason": reason,
            })

    for destination, editable in editable_by_destination.items():
        if not editable:
            add_failure(start_frame, destination, "No unlocked transform channels")

    progress = _progress_begin(len(source_frames))
    progress_interval = max(1, int(len(source_frames) / 50.0))

    try:
        for index, source_frame in enumerate(source_frames, 1):
            update_progress = (
                index == 1 or index == len(source_frames) or
                index % progress_interval == 0
            )
            if progress and not _progress_step(
                    source_frame, index, update=update_progress):
                report["cancelled"] = True
                break

            destination_frame = start_frame + (source_frame - source_frames[0])
            maya.cmds.currentTime(destination_frame, edit=True)
            unresolved = []
            previous_error = None

            for attempt in range(max(1, int(max_attempts))):
                unresolved = []
                apply_failed = set()
                for source_name, destination in matches:
                    sample = samples.get(source_name, {}).get(source_frame)
                    if not sample:
                        continue
                    try:
                        _set_world_sample(
                            destination, sample, paste_position, paste_rotation
                        )
                    except RuntimeError:
                        apply_failed.add(destination)
                        unresolved.append((source_name, destination))

                # Euler values can describe the same orientation in different
                # forms. Rechecking their component values caused most of the
                # old 5-6 redundant solve passes. Parent-first xform already
                # applies rotation correctly, so retry only positional misses.
                total_error = 0.0
                if paste_position:
                    for source_name, destination in matches:
                        if destination in apply_failed:
                            continue
                        sample = samples.get(source_name, {}).get(source_frame)
                        if not sample:
                            continue
                        try:
                            error = _position_error(destination, sample)
                        except RuntimeError:
                            error = float("inf")
                        if error > position_tolerance:
                            total_error += error
                            unresolved.append((source_name, destination))
                if not unresolved:
                    break

                # Stop retrying driven/locked rigs when another pass makes no
                # measurable improvement.
                if (previous_error is not None and
                        total_error >= previous_error - position_tolerance * 0.1):
                    break
                previous_error = total_error

            for editable, destinations in key_groups.items():
                try:
                    maya.cmds.setKeyframe(
                        destinations,
                        attribute=list(editable),
                        time=(destination_frame,),
                    )
                except RuntimeError as error:
                    # Isolate the one problematic object without penalizing
                    # the normal batch path.
                    for destination in destinations:
                        try:
                            maya.cmds.setKeyframe(
                                destination,
                                attribute=list(editable),
                                time=(destination_frame,),
                            )
                        except RuntimeError as object_error:
                            add_failure(
                                destination_frame, destination, str(object_error)
                            )

            for _, destination in unresolved:
                add_failure(
                    destination_frame,
                    destination,
                    "World transform did not converge",
                )
            report["frames"] += 1
    finally:
        if progress:
            maya.cmds.progressWindow(endProgress=True)

    return report


def load_wanimation(path, objects=None, namespaces=None, start_frame=None,
                    source_time=None, option="replace", connect=False,
                    current_time=False, paste_position=True,
                    paste_rotation=True, max_attempts=10,
                    full_check_attempts=5):
    """Load standard attributes and world transforms as one undoable action."""
    world_path = os.path.join(path, WORLD_FILENAME)
    world_animation = WorldAnimation.from_path(world_path)
    animation = mutils.Animation.fromPath(path)
    selection = maya.cmds.ls(selection=True, long=True) or []
    original_time = maya.cmds.currentTime(query=True)

    maya.cmds.undoInfo(openChunk=True, chunkName="Load WAnimation")
    try:
        _load_non_world_attributes(
            animation,
            objects=objects,
            namespaces=namespaces,
            start_frame=start_frame,
            source_time=source_time,
            option=option,
            connect=connect,
            current_time=current_time,
        )
        report = paste_world_animation(
            world_animation,
            objects=objects,
            namespaces=namespaces,
            start_frame=start_frame,
            source_time=source_time,
            option=option,
            current_time=current_time,
            paste_position=paste_position,
            paste_rotation=paste_rotation,
            max_attempts=max_attempts,
            full_check_attempts=full_check_attempts,
        )
    finally:
        maya.cmds.currentTime(original_time, edit=True)
        maya.cmds.select(selection, replace=True) if selection else maya.cmds.select(clear=True)
        maya.cmds.undoInfo(closeChunk=True)

    return report
