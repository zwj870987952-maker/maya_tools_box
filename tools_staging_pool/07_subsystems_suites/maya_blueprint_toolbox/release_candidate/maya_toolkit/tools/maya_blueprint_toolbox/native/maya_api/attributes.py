"""Attribute helpers for blueprint Maya operations."""

from ..core.types import AttrPacket, AttrRef, TransformFrameData, normalize_attr_refs, normalize_node_list
from .common import MayaApiError, UndoChunk, maya_modules
from .scene_nodes import existing_nodes


COMMON_ATTRIBUTE_NAMES = [
    "translateX",
    "translateY",
    "translateZ",
    "rotateX",
    "rotateY",
    "rotateZ",
    "scaleX",
    "scaleY",
    "scaleZ",
    "visibility",
    "tx",
    "ty",
    "tz",
    "rx",
    "ry",
    "rz",
    "sx",
    "sy",
    "sz",
    "v",
]


def set_attribute(nodes, attribute, value, value_type="text"):
    """Set one attribute on each input node."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    if not attribute:
        raise MayaApiError("Attribute name is required.")

    converted_value = _convert_value(value, value_type)
    changed_attrs = []
    from ...workflow import writable_attrs
    writable_attrs([node+"."+attribute for node in source_nodes])
    with UndoChunk("Blueprint Set Attribute"):
        for node in source_nodes:
            attr_path = "{0}.{1}".format(node, attribute)
            if not cmds.objExists(attr_path):
                raise MayaApiError("Attribute does not exist: {0}".format(attr_path))
            if value_type == "text":
                cmds.setAttr(attr_path, converted_value, type="string")
            else:
                cmds.setAttr(attr_path, converted_value)
            changed_attrs.append(attr_path)

    print("Set Attribute: {0} attribute(s).".format(len(changed_attrs)))
    return changed_attrs


def make_attribute_refs(nodes, attribute):
    """Build attribute references for existing nodes."""
    cmds = maya_modules()
    source_nodes = existing_nodes(normalize_node_list(nodes))
    if not attribute:
        raise MayaApiError("Attribute name is required.")

    refs = []
    for node in source_nodes:
        attr_path = "{0}.{1}".format(node, attribute)
        if not cmds.objExists(attr_path):
            raise MayaApiError("Attribute does not exist: {0}".format(attr_path))
        refs.append(AttrRef(node, attribute))

    print("Make Attribute Ref: {0} attribute(s).".format(len(refs)))
    return refs


def make_attribute_refs_from_items(nodes, attribute_items):
    """Build attribute references from full attr paths or attr names."""
    cmds = maya_modules()
    items = parse_attribute_items(attribute_items)
    if not items:
        raise MayaApiError("Attribute item is required.")

    refs = []
    attribute_names = []
    for item in items:
        if "." in item:
            attr_ref = AttrRef.from_full_attr(item)
            if not cmds.objExists(attr_ref.full_attr):
                raise MayaApiError("Attribute does not exist: {0}".format(attr_ref.full_attr))
            refs.append(attr_ref)
        else:
            attribute_names.append(item)

    if attribute_names:
        source_nodes = existing_nodes(normalize_node_list(nodes))
        for node in source_nodes:
            for attribute in attribute_names:
                attr_path = "{0}.{1}".format(node, attribute)
                if not cmds.objExists(attr_path):
                    raise MayaApiError("Attribute does not exist: {0}".format(attr_path))
                refs.append(AttrRef(node, attribute))

    refs = _unique_attr_refs(refs)
    print("Make Attribute Ref: {0} attribute(s).".format(len(refs)))
    return refs


def parse_attribute_items(attribute_items):
    """Parse attribute item storage from list or legacy comma/newline text."""
    if not attribute_items:
        return []
    if isinstance(attribute_items, (list, tuple)):
        return _unique_text_items(attribute_items)

    normalized = str(attribute_items).replace("\n", ",").replace(";", ",")
    return _unique_text_items(normalized.split(","))


def common_attribute_names():
    """Return built-in common Maya attributes for search controls."""
    return list(COMMON_ATTRIBUTE_NAMES)


def selected_node_attribute_names():
    """Return attribute names available on the current Maya selection."""
    cmds = maya_modules()
    selected_nodes = cmds.ls(selection=True, long=True) or []
    names = []
    for node in selected_nodes:
        names.extend(cmds.listAttr(node) or [])
    return _unique_text_items(names)


def selected_channel_box_attribute_names():
    """Return attribute names selected in the Channel Box."""
    cmds = maya_modules()
    selected_nodes = cmds.ls(selection=True, long=True) or []
    if not selected_nodes:
        raise MayaApiError("No Maya selection found.")

    attr_names = []
    channel_box = "mainChannelBox"
    query_flags = [
        "selectedMainAttributes",
        "selectedShapeAttributes",
        "selectedHistoryAttributes",
        "selectedOutputAttributes",
    ]
    for flag in query_flags:
        try:
            attr_names.extend(cmds.channelBox(channel_box, query=True, **{flag: True}) or [])
        except Exception:
            pass

    attr_names = _unique_text_items(attr_names)
    if not attr_names:
        raise MayaApiError("No Channel Box attributes selected.")

    return attr_names


def inspect_attributes(attr_refs):
    """Return attribute packets with runtime Maya capability data."""
    refs = _existing_attr_refs(attr_refs)
    packets = []
    for attr_ref in refs:
        packets.append(_inspect_attr_ref(attr_ref))

    print("Inspect Attribute: {0} attribute(s).".format(len(packets)))
    return packets


def set_attribute_refs(attr_refs, value, value_type="auto"):
    """Set attributes from AttrRef values."""
    if isinstance(value, TransformFrameData):
        return _set_transform_frame_data_attr_refs(attr_refs, value)

    cmds = maya_modules()
    refs = _existing_attr_refs(attr_refs)
    changed_attrs = []

    from ...workflow import writable_attrs
    writable_attrs([r.full_attr for r in refs])
    converted_values=[_convert_value_for_attr(r,value,value_type) for r in refs]
    with UndoChunk("Blueprint Set Attribute Ref"):
        for attr_ref,converted_value in zip(refs,converted_values):
            if value_type == "text" or _attr_type(attr_ref) == "string":
                cmds.setAttr(attr_ref.full_attr, "" if converted_value is None else str(converted_value), type="string")
            else:
                cmds.setAttr(attr_ref.full_attr, converted_value)
            changed_attrs.append(attr_ref.full_attr)

    print("Set Attribute Ref: {0} attribute(s).".format(len(changed_attrs)))
    return changed_attrs


def _set_transform_frame_data_attr_refs(attr_refs,frame_data):
    import math
    from ...workflow import writable_attrs,writable_nodes
    from .animation import normalize_channel
    cmds=maya_modules();refs=_existing_attr_refs(attr_refs)
    channels=set(frame_data.paste_channels or frame_data.recorded_channels or [])
    refs=[r for r in refs if normalize_channel(r.attr) in channels]
    if not refs:raise MayaApiError("No matching paste channels")
    target_nodes=_unique_target_nodes(refs)
    if len(target_nodes)!=len(frame_data.source_nodes):raise MayaApiError("Source/target lists must match 1-to-1")
    writable_nodes(target_nodes)
    if any(not cmds.objectType(n,isAType='transform') for n in target_nodes):raise MayaApiError("Transform targets required")
    requested={n:{normalize_channel(r.attr) for r in refs if r.node==n} for n in target_nodes}
    affected={n:[] for n in target_nodes}
    for n in target_nodes:
        for group in ('translate','rotate'):
            if any(group+a in requested[n] for a in 'XYZ'):affected[n].extend(group+a for a in 'XYZ')
        affected[n].extend('scale'+a for a in 'XYZ' if 'scale'+a in requested[n])
    writable_attrs([n+'.'+c for n in target_nodes for c in affected[n]])
    samples={}
    for frame in frame_data.frames:
        if not math.isfinite(float(frame)):raise MayaApiError("Non-finite sample time")
        for n in target_nodes:
            source=frame_data.source_nodes[target_nodes.index(n)]
            rows=[r for r in frame_data.samples if r.get('node')==source and float(r.get('frame'))==float(frame)]
            if len(rows)!=1:raise MayaApiError("Missing/duplicate frame sample")
            values=rows[0].get('values') or {}
            if any(c not in values or type(values[c]) not in (int,float) or not math.isfinite(values[c]) for c in requested[n]):raise MayaApiError("Missing/non-finite channel sample")
            samples[(n,float(frame))]=values
    current_time=cmds.currentTime(query=True)
    keyed=[]
    with UndoChunk('Blueprint World Frame Paste'):
        try:
            for frame in frame_data.frames:
                cmds.currentTime(frame)
                for n in target_nodes:
                    values=samples[(n,float(frame))]
                    for group,flag in (('translate','translation'),('rotate','rotation')):
                        if any(group+a in requested[n] for a in 'XYZ'):
                            vector=cmds.xform(n,query=True,worldSpace=True,**{flag:True})
                            for i,a in enumerate('XYZ'):
                                if group+a in requested[n]:vector[i]=values[group+a]
                            cmds.xform(n,worldSpace=True,**{flag:vector})
                    for a in 'XYZ':
                        if 'scale'+a in requested[n]:cmds.setAttr(n+'.scale'+a,values['scale'+a])
                    for c in affected[n]:
                        plug=n+'.'+c;cmds.setKeyframe(plug,time=frame);keyed.append(plug)
        finally:cmds.currentTime(current_time)
    return _unique_text_items(keyed)


def _samples_for_frame(frame_data, frame):
    return [sample for sample in frame_data.samples if float(sample.get("frame")) == float(frame)]


def _sample_for_attr_ref(samples, attr_ref, frame_data, target_nodes):
    if not samples:
        return None

    try:
        target_index = target_nodes.index(attr_ref.node)
    except ValueError:
        return None

    source_node = frame_data.source_nodes[target_index]
    for sample in samples:
        if sample.get("node") == source_node:
            return sample
    return None


def _unique_target_nodes(attr_refs):
    target_nodes = []
    seen = set()
    for attr_ref in attr_refs or []:
        if attr_ref.node not in seen:
            target_nodes.append(attr_ref.node)
            seen.add(attr_ref.node)
    return target_nodes


def get_attribute_refs(attr_refs):
    """Read values from AttrRef values."""
    cmds = maya_modules()
    refs = _existing_attr_refs(attr_refs)
    values = []
    for attr_ref in refs:
        values.append(cmds.getAttr(attr_ref.full_attr))

    print("Get Attribute Ref: {0} value(s).".format(len(values)))
    if len(values) == 1:
        return values[0]
    return values


def get_attribute(nodes, attribute):
    """Get one attribute from each input node and return values as text."""
    cmds = maya_modules()
    source_nodes = existing_nodes(nodes)
    if not attribute:
        raise MayaApiError("Attribute name is required.")

    values = []
    for node in source_nodes:
        attr_path = "{0}.{1}".format(node, attribute)
        if not cmds.objExists(attr_path):
            raise MayaApiError("Attribute does not exist: {0}".format(attr_path))
        values.append(cmds.getAttr(attr_path))

    value_text = ", ".join(str(value) for value in values)
    print("Get Attribute: {0} value(s).".format(len(values)))
    return value_text


def packets_report(packets):
    """Return a compact, readable report for inspected attributes."""
    lines = []
    for packet in packets or []:
        lines.append(
            "{0} = {1} ({2}, keyable={3}, writable={4}, locked={5}, connected={6})".format(
                packet.attr_ref.full_attr,
                packet.value,
                packet.maya_attr_type or "unknown",
                packet.keyable,
                packet.writable,
                packet.locked,
                packet.connected,
            )
        )
    return "\n".join(lines)


def _existing_attr_refs(attr_refs):
    cmds = maya_modules()
    refs = normalize_attr_refs(attr_refs)
    if not refs:
        raise MayaApiError("No attribute references found.")
    for attr_ref in refs:
        if not cmds.objExists(attr_ref.full_attr):
            raise MayaApiError("Attribute does not exist: {0}".format(attr_ref.full_attr))
    return refs


def _unique_text_items(items):
    result = []
    seen = set()
    for item in items or []:
        text = str(item).strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _unique_attr_refs(attr_refs):
    result = []
    seen = set()
    for attr_ref in attr_refs or []:
        if attr_ref.full_attr not in seen:
            result.append(attr_ref)
            seen.add(attr_ref.full_attr)
    return result


def _inspect_attr_ref(attr_ref):
    cmds = maya_modules()
    value = None
    try:
        value = cmds.getAttr(attr_ref.full_attr)
    except Exception:
        value = None

    maya_attr_type = _attr_type(attr_ref)
    return AttrPacket(
        attr_ref,
        value=value,
        maya_attr_type=maya_attr_type,
        semantic=_semantic_for_attr(attr_ref.attr),
        axis=_axis_for_attr(attr_ref.attr),
        keyable=_attribute_query(attr_ref, "keyable"),
        writable=_attribute_query(attr_ref, "writable"),
        readable=_attribute_query(attr_ref, "readable"),
        connectable=_attribute_query(attr_ref, "connectable"),
        locked=bool(cmds.getAttr(attr_ref.full_attr, lock=True)),
        connected=bool(cmds.listConnections(attr_ref.full_attr, source=True, destination=True, plugs=True) or []),
        numeric=_is_numeric_attr_type(maya_attr_type),
    )


def _attribute_query(attr_ref, query_flag):
    cmds = maya_modules()
    try:
        return bool(cmds.attributeQuery(attr_ref.attr, node=attr_ref.node, **{query_flag: True}))
    except Exception:
        return False


def _attr_type(attr_ref):
    cmds = maya_modules()
    try:
        return cmds.getAttr(attr_ref.full_attr, type=True) or ""
    except Exception:
        return ""


def _semantic_for_attr(attr):
    clean_attr = attr.rsplit(".", 1)[-1]
    lower_attr = clean_attr.lower()
    if lower_attr.startswith("translate"):
        return "translate"
    if lower_attr.startswith("rotate"):
        return "rotate"
    if lower_attr.startswith("scale"):
        return "scale"
    if lower_attr == "visibility":
        return "visibility"
    return ""


def _axis_for_attr(attr):
    clean_attr = attr.rsplit(".", 1)[-1]
    if clean_attr and clean_attr[-1] in ("X", "Y", "Z"):
        return clean_attr[-1]
    return ""


def _is_numeric_attr_type(maya_attr_type):
    return maya_attr_type in (
        "bool",
        "byte",
        "short",
        "long",
        "float",
        "double",
        "doubleLinear",
        "doubleAngle",
        "enum",
        "time",
    )


def _convert_value_for_attr(attr_ref, value, value_type):
    if value_type and value_type != "auto":
        return _convert_value(value, value_type)

    maya_attr_type = _attr_type(attr_ref)
    if maya_attr_type == "string":
        return "" if value is None else str(value)
    if maya_attr_type == "bool":
        return _convert_value(value, "bool")
    if _is_numeric_attr_type(maya_attr_type):
        return _convert_value(value, "number")
    return value


def _convert_value(value, value_type):
    if value_type == "number":
        return float(value)
    if value_type == "bool":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")
    return "" if value is None else str(value)
