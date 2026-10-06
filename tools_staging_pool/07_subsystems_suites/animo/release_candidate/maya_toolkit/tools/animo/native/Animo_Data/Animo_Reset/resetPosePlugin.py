import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
import maya.cmds as cmds
import maya.mel as mel
import json
import os
import sys

def maya_useNewAPI():
    pass

MARK_COLOR = "#32CD32"
MARK_OPACITY = 0.25

_documents_path = os.path.expanduser('~')
_user = _documents_path.split("/Documents")[0]
JSON_FILE_PATH = os.path.join(_user, 'Documents', 'animTools', 'channelbox_attributes.json')


def _get_maya_version():
    try:
        return cmds.about(version=True).split()[0]
    except:
        return "unknown"


def _load_marker_module():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
        parent_folder = os.path.dirname(folder)
        marker_folder = os.path.join(parent_folder, "Animo_Keys_Tangent")
    except NameError:
        marker_folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Keys_Tangent")
    v = _get_maya_version()
    n = "mark_frame"
    py = os.path.join(marker_folder, n + ".py")
    pyc = os.path.join(marker_folder, "{}_py{}.pyc".format(n, v))
    if not os.path.exists(py) and not os.path.exists(pyc):
        return None
    if marker_folder not in sys.path:
        sys.path.insert(0, marker_folder)
    if n in sys.modules:
        del sys.modules[n]
    try:
        import importlib
        return importlib.import_module(n)
    except:
        return None


class ResetPoseCmd(om2.MPxCommand):
    kPluginCmdName = "resetPose"

    def __init__(self):
        om2.MPxCommand.__init__(self)
        self._dg_modifier = None
        self._curve_changes = []
        self._marker_module = None
        self._marker_start = None
        self._marker_end = None

    @staticmethod
    def creator():
        return ResetPoseCmd()

    def isUndoable(self):
        return True

    def _get_mobj(self, node_name):
        sel = om2.MSelectionList()
        try:
            sel.add(node_name)
            return sel.getDependNode(0)
        except:
            return None

    def _get_plug(self, node_name, attr_name):
        mobj = self._get_mobj(node_name)
        if not mobj:
            return None
        fn = om2.MFnDependencyNode(mobj)
        try:
            return fn.findPlug(attr_name, False)
        except:
            return None

    def _get_plug_from_mobj(self, mobj, attr_name):
        fn = om2.MFnDependencyNode(mobj)
        try:
            return fn.findPlug(attr_name, False)
        except:
            return None

    def _get_default_value(self, mobj, attr_name):
        fn = om2.MFnDependencyNode(mobj)
        try:
            attr_obj = fn.attribute(attr_name)
            api_type = attr_obj.apiType()
            if api_type == om2.MFn.kNumericAttribute:
                return om2.MFnNumericAttribute(attr_obj).default
            elif api_type in (om2.MFn.kUnitAttribute, om2.MFn.kDoubleLinearAttribute, om2.MFn.kDoubleAngleAttribute):
                default_val = om2.MFnUnitAttribute(attr_obj).default
                if isinstance(default_val, om2.MAngle):
                    return default_val.asDegrees()
                elif isinstance(default_val, om2.MDistance):
                    return default_val.asUnits(om2.MDistance.uiUnit())
                elif isinstance(default_val, om2.MTime):
                    return default_val.asUnits(om2.MTime.uiUnit())
                return default_val
        except:
            pass
        try:
            default_value = cmds.attributeQuery(attr_name, ld=True, n=fn.name())
            if default_value:
                return default_value[0]
        except:
            pass
        return 0.0

    def _get_long_name(self, mobj, attr_name):
        fn = om2.MFnDependencyNode(mobj)
        try:
            return om2.MFnAttribute(fn.attribute(attr_name)).name
        except:
            return attr_name

    def _get_keyable_attrs(self, mobj):
        fn = om2.MFnDependencyNode(mobj)
        attrs = []
        for i in range(fn.attributeCount()):
            try:
                attr_obj = fn.attribute(i)
                plug = fn.findPlug(attr_obj, False)
                if plug.isKeyable and not plug.isLocked:
                    attrs.append(plug.partialName(useLongNames=False))
            except:
                continue
        return attrs

    def _get_anim_curve(self, plug):
        if plug is None or not plug.isConnected:
            return None
        try:
            src_plug = plug.source()
            if not src_plug.isNull:
                src_node = src_plug.node()
                if src_node.hasFn(om2.MFn.kAnimCurve):
                    return oma2.MFnAnimCurve(src_node)
        except:
            pass
        return None

    def _get_keys_in_range(self, plug, start_time, end_time):
        anim_curve = self._get_anim_curve(plug)
        if anim_curve is None:
            return []
        keys = []
        start_mtime = om2.MTime(start_time, om2.MTime.uiUnit())
        end_mtime = om2.MTime(end_time, om2.MTime.uiUnit())
        for i in range(anim_curve.numKeys):
            key_time = anim_curve.input(i)
            if start_mtime.value <= key_time.value <= end_mtime.value:
                keys.append((i, key_time.value))
        return keys

    def _is_graph_editor_active(self):
        try:
            return cmds.window("graphEditor1Window", exists=True) and cmds.window("graphEditor1Window", q=True, visible=True)
        except:
            return False

    def _get_selected_time_range(self):
        try:
            playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
            timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
            if timeRange and len(timeRange) >= 2:
                start_range = int(timeRange[0])
                end_range = int(timeRange[1] - 1)
                if end_range > start_range:
                    return start_range, end_range
        except:
            pass
        return None, None

    def _get_selected_graph_editor_keys(self):
        selected_curves = cmds.keyframe(q=True, selected=True, name=True)
        if not selected_curves:
            return []
        selected_keys_data = []
        for curve in selected_curves:
            try:
                connections = cmds.listConnections(curve + '.output', p=True)
                if connections:
                    obj, attr = connections[0].split('.', 1)
                    selected_times = cmds.keyframe(curve, q=True, selected=True, timeChange=True)
                    if selected_times:
                        for time_val in selected_times:
                            selected_keys_data.append({'object': obj, 'attribute': attr, 'time': time_val})
            except:
                continue
        return selected_keys_data

    def _get_reset_value(self, mobj, attr, data):
        fn = om2.MFnDependencyNode(mobj)
        node_name = fn.name()
        long_name = self._get_long_name(mobj, attr)
        if node_name in data:
            if attr in data[node_name]:
                return data[node_name][attr]
            elif long_name in data[node_name]:
                return data[node_name][long_name]
        return self._get_default_value(mobj, attr)

    def _set_plug_value(self, plug, value):
        if plug is None or plug.isLocked or plug.isDestination:
            return False
        try:
            attr_type = plug.attribute().apiType()
            if attr_type == om2.MFn.kDoubleAngleAttribute:
                self._dg_modifier.newPlugValueMAngle(plug, om2.MAngle(value, om2.MAngle.kDegrees))
            elif attr_type == om2.MFn.kDoubleLinearAttribute:
                self._dg_modifier.newPlugValueMDistance(plug, om2.MDistance(value, om2.MDistance.uiUnit()))
            elif attr_type == om2.MFn.kNumericAttribute:
                num_attr = om2.MFnNumericAttribute(plug.attribute())
                num_type = num_attr.numericType()
                if num_type == om2.MFnNumericData.kBoolean:
                    self._dg_modifier.newPlugValueBool(plug, bool(value))
                elif num_type in (om2.MFnNumericData.kShort, om2.MFnNumericData.kInt, om2.MFnNumericData.kLong):
                    self._dg_modifier.newPlugValueInt(plug, int(value))
                else:
                    self._dg_modifier.newPlugValueDouble(plug, float(value))
            else:
                self._dg_modifier.newPlugValueDouble(plug, float(value))
            return True
        except:
            return False

    def _set_key_value(self, anim_curve, key_index, value, curve_change):
        try:
            anim_curve.setValue(key_index, value, curve_change)
        except:
            pass

    def _add_key(self, anim_curve, time_val, value, curve_change):
        try:
            time_obj = om2.MTime(time_val, om2.MTime.uiUnit())
            anim_curve.addKey(time_obj, value, oma2.MFnAnimCurve.kTangentAuto, oma2.MFnAnimCurve.kTangentAuto, curve_change)
        except:
            pass

    def _set_key_tangent_auto(self, anim_curve, key_index, curve_change):
        try:
            anim_curve.setInTangentType(key_index, oma2.MFnAnimCurve.kTangentAuto, curve_change)
            anim_curve.setOutTangentType(key_index, oma2.MFnAnimCurve.kTangentAuto, curve_change)
        except:
            pass

    def _attr_has_anim_layer(self, node_name, attr_name):
        try:
            conns = cmds.listConnections(node_name + '.' + attr_name, type='animBlendNodeBase')
            return bool(conns)
        except:
            return False

    def _apply_reset_at_current_time(self, plug, value, current_time, node_name=None, attr_name=None):
        if plug is None or plug.isLocked:
            return
        if node_name and attr_name and self._attr_has_anim_layer(node_name, attr_name):
            try:
                cmds.setAttr(node_name + '.' + attr_name, value)
            except:
                pass
            return
        anim_curve = self._get_anim_curve(plug)
        if anim_curve is not None:
            key_index = anim_curve.find(current_time)
            curve_change = oma2.MAnimCurveChange()
            self._curve_changes.append(curve_change)
            if key_index is not None:
                self._set_key_value(anim_curve, key_index, value, curve_change)
                self._set_key_tangent_auto(anim_curve, key_index, curve_change)
            else:
                self._add_key(anim_curve, current_time.value, value, curve_change)
        elif not plug.isDestination:
            self._set_plug_value(plug, value)

    def _load_json_data(self, json_file):
        json_dir = os.path.dirname(json_file)
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        if not os.path.exists(json_file):
            with open(json_file, 'w') as file:
                json.dump({}, file, indent=4)
        with open(json_file, 'r') as file:
            return json.load(file)

    def _get_marker_range(self, selected_keys_data, graph_editor_active, start_range, end_range):
        if selected_keys_data and graph_editor_active:
            times = [k['time'] for k in selected_keys_data]
            return int(min(times)), int(max(times))
        elif start_range is not None and end_range is not None:
            return start_range, end_range
        else:
            ct = int(oma2.MAnimControl.currentTime().value)
            return ct, ct

    def doIt(self, args):
        self._dg_modifier = om2.MDGModifier()
        self._curve_changes = []

        sel_list = om2.MGlobal.getActiveSelectionList()
        if sel_list.length() == 0:
            return

        cmds.waitCursor(state=True)
        try:
            data = self._load_json_data(JSON_FILE_PATH)
            selected_keys_data = self._get_selected_graph_editor_keys()
            graph_editor_active = self._is_graph_editor_active()
            start_range, end_range = self._get_selected_time_range()
            selected_channels = cmds.channelBox('mainChannelBox', q=True, sma=True)

            self._marker_module = _load_marker_module()
            self._marker_start, self._marker_end = self._get_marker_range(selected_keys_data, graph_editor_active, start_range, end_range)

            if self._marker_module:
                if self._marker_start == self._marker_end:
                    self._marker_module.mark_current_frame(auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
                else:
                    self._marker_module.mark_range(self._marker_start, self._marker_end, auto_fade=False, color=MARK_COLOR, opacity=MARK_OPACITY)
                cmds.refresh(force=True)

            if selected_keys_data and graph_editor_active:
                self._process_graph_editor_keys(selected_keys_data, data)
            elif start_range is not None and end_range is not None:
                self._process_time_range(sel_list, selected_channels, start_range, end_range, data)
            else:
                self._process_current_frame(sel_list, selected_channels, data)

            try:
                self._dg_modifier.doIt()
            except:
                pass

            if self._marker_module:
                self._marker_module.trigger_fade(delay=500)
        finally:
            cmds.waitCursor(state=False)

    def _process_graph_editor_keys(self, selected_keys_data, data):
        for key_data in selected_keys_data:
            obj, attr, time_val = key_data['object'], key_data['attribute'], key_data['time']
            mobj = self._get_mobj(obj)
            if not mobj:
                continue
            plug = self._get_plug_from_mobj(mobj, attr)
            if plug is None:
                continue
            anim_curve = self._get_anim_curve(plug)
            if anim_curve is None:
                continue
            reset_value = self._get_reset_value(mobj, attr, data)
            time_obj = om2.MTime(time_val, om2.MTime.uiUnit())
            key_index = anim_curve.find(time_obj)
            if key_index is not None:
                curve_change = oma2.MAnimCurveChange()
                self._curve_changes.append(curve_change)
                self._set_key_value(anim_curve, key_index, reset_value, curve_change)
                self._set_key_tangent_auto(anim_curve, key_index, curve_change)

    def _process_time_range(self, sel_list, selected_channels, start_range, end_range, data):
        for i in range(sel_list.length()):
            try:
                mobj = sel_list.getDependNode(i)
            except:
                continue
            fn = om2.MFnDependencyNode(mobj)
            attrs_to_process = selected_channels if selected_channels else self._get_keyable_attrs(mobj)
            if not attrs_to_process:
                continue
            for attr in attrs_to_process:
                plug = self._get_plug_from_mobj(mobj, attr)
                if plug is None or plug.isLocked:
                    continue
                anim_curve = self._get_anim_curve(plug)
                if anim_curve is None:
                    continue
                keys_in_range = self._get_keys_in_range(plug, start_range, end_range)
                if not keys_in_range:
                    continue
                reset_value = self._get_reset_value(mobj, attr, data)
                curve_change = oma2.MAnimCurveChange()
                self._curve_changes.append(curve_change)
                for key_index, key_time in keys_in_range:
                    self._set_key_value(anim_curve, key_index, reset_value, curve_change)
                    self._set_key_tangent_auto(anim_curve, key_index, curve_change)

    def _process_current_frame(self, sel_list, selected_channels, data):
        current_time = oma2.MAnimControl.currentTime()
        for i in range(sel_list.length()):
            try:
                mobj = sel_list.getDependNode(i)
            except:
                continue
            fn = om2.MFnDependencyNode(mobj)
            node_name = fn.name()
            if selected_channels:
                for attr in selected_channels:
                    plug = self._get_plug_from_mobj(mobj, attr)
                    if plug is None or plug.isLocked:
                        continue
                    reset_value = self._get_reset_value(mobj, attr, data)
                    self._apply_reset_at_current_time(plug, reset_value, current_time, node_name, attr)
            else:
                if node_name in data:
                    for attr, value in data[node_name].items():
                        plug = self._get_plug_from_mobj(mobj, attr)
                        if plug is not None and not plug.isLocked:
                            self._apply_reset_at_current_time(plug, value, current_time, node_name, attr)
                else:
                    for attr in self._get_keyable_attrs(mobj):
                        plug = self._get_plug_from_mobj(mobj, attr)
                        if plug is None or plug.isLocked:
                            continue
                        default_val = self._get_default_value(mobj, attr)
                        self._apply_reset_at_current_time(plug, default_val, current_time, node_name, attr)

    def redoIt(self):
        self._dg_modifier.doIt()
        for curve_change in self._curve_changes:
            curve_change.redoIt()

    def undoIt(self):
        for curve_change in reversed(self._curve_changes):
            curve_change.undoIt()
        self._dg_modifier.undoIt()


def initializePlugin(plugin):
    vendor = "AnimTools"
    version = "1.0.0"
    fn_plugin = om2.MFnPlugin(plugin, vendor, version)
    try:
        fn_plugin.registerCommand(ResetPoseCmd.kPluginCmdName, ResetPoseCmd.creator)
    except:
        om2.MGlobal.displayError("Failed to register command: {}".format(ResetPoseCmd.kPluginCmdName))
        raise


def uninitializePlugin(plugin):
    fn_plugin = om2.MFnPlugin(plugin)
    try:
        fn_plugin.deregisterCommand(ResetPoseCmd.kPluginCmdName)
    except:
        om2.MGlobal.displayError("Failed to deregister command: {}".format(ResetPoseCmd.kPluginCmdName))
        raise


def run():
    plugin_name = "resetPosePlugin"
    if not cmds.pluginInfo(plugin_name, q=True, loaded=True):
        try:
            cmds.loadPlugin(__file__)
        except:
            pass
    cmds.resetPose()