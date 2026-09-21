"""Animation workflow helpers for blueprint nodes."""

import json
import os
import tempfile

from ..core.types import TransformFrameData, normalize_node_list
from .common import MayaApiError, maya_modules
from .scene_nodes import existing_nodes


TRANSFORM_CHANNELS = [
    "translateX",
    "translateY",
    "translateZ",
    "rotateX",
    "rotateY",
    "rotateZ",
    "scaleX",
    "scaleY",
    "scaleZ",
]

TRANSLATE_CHANNELS = ["translateX", "translateY", "translateZ"]
ROTATE_CHANNELS = ["rotateX", "rotateY", "rotateZ"]
SCALE_CHANNELS = ["scaleX", "scaleY", "scaleZ"]

SHORT_CHANNELS = {
    "tx": "translateX",
    "ty": "translateY",
    "tz": "translateZ",
    "rx": "rotateX",
    "ry": "rotateY",
    "rz": "rotateZ",
    "sx": "scaleX",
    "sy": "scaleY",
    "sz": "scaleZ",
}


def current_frame(frame_value=None):
    """Return a single-frame list from input value or Maya current time."""
    cmds = maya_modules()
    if frame_value is None:
        frame = float(cmds.currentTime(query=True))
    else:
        frame = float(frame_value)
    print("Current Frame: {0}.".format(_format_frame(frame)))
    return [frame]


def frame_range(start_frame=None, end_frame=None, include_end=True):
    """Return playback range frames, or explicit start/end if connected."""
    cmds = maya_modules()
    if start_frame is None:
        start = float(cmds.playbackOptions(query=True, min=True))
    else:
        start = float(start_frame)

    if end_frame is None:
        end = float(cmds.playbackOptions(query=True, max=True))
    else:
        end = float(end_frame)

    if end < start:
        raise MayaApiError("End frame cannot be smaller than start frame.")

    frames = _frames_from_range(start, end, include_end=include_end)
    range_data = {
        "start": start,
        "end": end,
        "include_end": bool(include_end),
    }
    print(
        "Frame Range: {0}-{1}, {2} frame(s).".format(
            _format_frame(start),
            _format_frame(end),
            len(frames),
        )
    )
    return range_data, frames


def transform_channels(include_translate=True, include_rotate=True, include_scale=False):
    """Return standard transform channels from boolean switches."""
    channels = []
    if include_translate:
        channels.extend(TRANSLATE_CHANNELS)
    if include_rotate:
        channels.extend(ROTATE_CHANNELS)
    if include_scale:
        channels.extend(SCALE_CHANNELS)
    channels = normalize_channels(channels)
    print("Transform Channels: {0} channel(s).".format(len(channels)))
    return channels


def selected_channel_box_channels(default_transform=True):
    """Return transform channels selected in the Maya Channel Box."""
    cmds = maya_modules()
    selected_channels = []
    try:
        selected_channels = cmds.channelBox(
            "mainChannelBox",
            query=True,
            selectedMainAttributes=True,
        ) or []
    except Exception:
        selected_channels = []

    channels = []
    for channel in selected_channels:
        normalized = normalize_channel(channel)
        if normalized in TRANSFORM_CHANNELS:
            channels.append(normalized)

    channels = normalize_channels(channels)
    if not channels and default_transform:
        channels = transform_channels(include_translate=True, include_rotate=True, include_scale=False)
    else:
        print("Selected Channel Box Channels: {0} channel(s).".format(len(channels)))
    return channels


def copy_frame(nodes, frames, paste_channels=None, save_json=False, json_path="", record_short_name=True):
    """Capture world transform data for nodes at the given frames."""
    cmds = maya_modules()
    source_nodes = existing_nodes(normalize_node_list(nodes), label="copy frame nodes")
    frame_values = normalize_frames(frames)
    if not frame_values:
        frame_values = current_frame()

    requested_channels = normalize_channels(paste_channels)
    if not requested_channels:
        requested_channels = transform_channels(include_translate=True, include_rotate=True, include_scale=False)

    current_time = float(cmds.currentTime(query=True))
    samples = []
    try:
        for frame in frame_values:
            cmds.currentTime(frame)
            for node in source_nodes:
                sample = {
                    "node": node,
                    "frame": frame,
                    "values": _world_transform_values(node),
                }
                if record_short_name:
                    short_names = cmds.ls(node, shortNames=True) or [node]
                    sample["short_name"] = short_names[0]
                samples.append(sample)
    finally:
        cmds.currentTime(current_time)

    frame_data = TransformFrameData(
        source_nodes=source_nodes,
        frames=frame_values,
        recorded_channels=TRANSFORM_CHANNELS,
        paste_channels=requested_channels,
        samples=samples,
    )

    if save_json:
        resolved_path = save_frame_data_json(frame_data, json_path=json_path)
        frame_data.json_path = resolved_path

    print(
        "Copy Frame: {0} node(s), {1} frame(s), {2} sample(s).".format(
            len(source_nodes),
            len(frame_values),
            len(samples),
        )
    )
    return frame_data


def save_frame_data_json(frame_data, json_path=""):
    """Save TransformFrameData to JSON and return the file path."""
    if not json_path:
        json_path = os.path.join(tempfile.gettempdir(), "maya_blueprint_copy_frame.json")

    folder = os.path.dirname(json_path)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    with open(json_path, "w") as file_handle:
        json.dump(frame_data.to_dict(), file_handle, indent=2, sort_keys=True)

    print("Copy Frame JSON: {0}".format(json_path))
    return json_path


def normalize_frames(frames):
    """Convert frame input into a list of numeric frame values."""
    if frames is None:
        return []
    if isinstance(frames, dict):
        start = frames.get("start")
        end = frames.get("end")
        include_end = frames.get("include_end", True)
        if start is None or end is None:
            return []
        return _frames_from_range(float(start), float(end), include_end=include_end)
    if isinstance(frames, (list, tuple)):
        return [float(frame) for frame in frames]
    return [float(frames)]


def normalize_channels(channels):
    """Return unique long transform channel names."""
    if channels is None:
        return []
    if isinstance(channels, str):
        raw_channels = channels.replace("\n", ",").replace(";", ",").split(",")
    else:
        raw_channels = channels

    result = []
    seen = set()
    for raw_channel in raw_channels:
        channel = normalize_channel(raw_channel)
        if channel and channel in TRANSFORM_CHANNELS and channel not in seen:
            result.append(channel)
            seen.add(channel)
    return result


def normalize_channel(channel):
    """Normalize short transform aliases to long channel names."""
    text = str(channel or "").strip()
    return SHORT_CHANNELS.get(text, text)


def _frames_from_range(start, end, include_end=True):
    start_int = int(round(start))
    end_int = int(round(end))
    stop = end_int + 1 if include_end else end_int
    return [float(frame) for frame in range(start_int, stop)]


def _world_transform_values(node):
    cmds = maya_modules()
    translate = cmds.xform(node, query=True, worldSpace=True, translation=True)
    rotate = cmds.xform(node, query=True, worldSpace=True, rotation=True)
    scale = cmds.xform(node, query=True, relative=True, scale=True)
    return {
        "translateX": float(translate[0]),
        "translateY": float(translate[1]),
        "translateZ": float(translate[2]),
        "rotateX": float(rotate[0]),
        "rotateY": float(rotate[1]),
        "rotateZ": float(rotate[2]),
        "scaleX": float(scale[0]),
        "scaleY": float(scale[1]),
        "scaleZ": float(scale[2]),
    }


def _format_frame(frame):
    if float(frame).is_integer():
        return str(int(frame))
    return str(frame)
