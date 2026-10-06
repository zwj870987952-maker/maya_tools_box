from __future__ import division, absolute_import

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import os
import json
import copy
import time

try:
    from PySide6.QtCore import QTimer, QEvent, QObject
    from PySide6.QtWidgets import QApplication
except ImportError:
    from PySide2.QtCore import QTimer, QEvent, QObject
    from PySide2.QtWidgets import QApplication


_prefs_path = None
_offsets_cache = None
_cache_valid = False

PIVOT_NULL = "Animo_Pivot"
PIVOT_SET = "Animo_Pivot_objects"


def get_prefs_path():
    global _prefs_path
    if _prefs_path:
        return _prefs_path

    if os.name == 'nt':
        docs = os.path.join(os.environ['USERPROFILE'], "Documents", "maya", "scripts", "Animo_Data", "Animo_Prefs")
    else:
        docs = os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts", "Animo_Data", "Animo_Prefs")
    if not os.path.exists(docs):
        os.makedirs(docs)
    _prefs_path = os.path.join(docs, "temp_pivot.json")
    return _prefs_path


def load_offsets():
    global _offsets_cache, _cache_valid
    if _cache_valid and _offsets_cache is not None:
        return _offsets_cache

    path = get_prefs_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            _offsets_cache = json.load(f)
    else:
        _offsets_cache = {"single_offsets": {}, "multi_offsets": [], "last_selection": []}

    if "last_selection" not in _offsets_cache:
        _offsets_cache["last_selection"] = []

    _cache_valid = True
    return _offsets_cache


def save_offsets(data):
    global _offsets_cache, _cache_valid
    path = get_prefs_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    _offsets_cache = data
    _cache_valid = True


def get_mobject(name):
    sel = om.MSelectionList()
    try:
        sel.add(name)
        return sel.getDependNode(0)
    except:
        return None


def obj_exists(name):
    sel = om.MSelectionList()
    try:
        sel.add(name)
        return True
    except:
        return False


def get_current_time():
    return oma.MAnimControl.currentTime().value


def set_current_time(frame):
    oma.MAnimControl.setCurrentTime(om.MTime(frame, om.MTime.uiUnit()))


def set_selection(names):
    sel = om.MSelectionList()
    for name in names:
        try:
            sel.add(name)
        except:
            pass
    om.MGlobal.setActiveSelectionList(sel)


def has_keyframes(name, attrs):
    if not obj_exists(name):
        return False
    for attr in attrs:
        try:
            keys = cmds.keyframe(name + '.' + attr, q=True, keyframeCount=True) or 0
            if keys > 0:
                return True
        except:
            pass
    return False


def get_all_keyframes(name, attrs):
    keyframes = set()
    if not obj_exists(name):
        return []
    for attr in attrs:
        try:
            keys = cmds.keyframe(name + '.' + attr, q=True, timeChange=True)
            if keys:
                keyframes.update(keys)
        except:
            pass
    return sorted(keyframes)


def get_key_count(name, attrs):
    count = 0
    if not obj_exists(name):
        return 0
    for attr in attrs:
        try:
            keys = cmds.keyframe(name + '.' + attr, q=True, keyframeCount=True) or 0
            count += keys
        except:
            pass
    return count


def has_key_at_time(name, attrs, time):
    if not obj_exists(name):
        return False
    for attr in attrs:
        try:
            keys = cmds.keyframe(name + '.' + attr, q=True, time=(time, time), keyframeCount=True) or 0
            if keys > 0:
                return True
        except:
            pass
    return False


def remove_keys_at_time(name, attrs, time):
    if not obj_exists(name):
        return
    for attr in attrs:
        try:
            cmds.cutKey(name, attribute=attr, time=(time, time))
        except:
            pass


def is_attr_locked(name, attr):
    obj = get_mobject(name)
    if not obj:
        return True
    fn = om.MFnDependencyNode(obj)
    try:
        plug = fn.findPlug(attr, False)
        return plug.isLocked
    except:
        return True


def run_euler_filter(name):
    if not obj_exists(name):
        return
    curves = []
    for attr in ['rx', 'ry', 'rz']:
        try:
            if cmds.keyframe(name + '.' + attr, q=True, keyframeCount=True):
                curves.append(name + '.' + attr)
        except:
            pass
    if curves:
        try:
            cmds.filterCurve(curves, filter='euler')
        except:
            pass


class _PivotMouseReleaseFilter(QObject):

    def __init__(self, controller):
        super(_PivotMouseReleaseFilter, self).__init__()
        self.controller = controller

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.controller.on_mouse_release()
        return False


class LiveTempPivot:

    def __init__(self):
        self.sel = []
        self.original_matrices = {}
        self.original_frame = None
        self.time_job = None
        self.selection_job = None
        self.locked_attrs = {}
        self.relationship_data = {}
        self.original_relationship_data = {}
        self.timer = None
        self.last_pivot_matrix = None
        self.pivot_to_ref_offset = None
        self.ref_obj = None
        self.objects_had_keys = False
        self.keys_set_this_session = False
        self.is_time_changing = False
        self.last_pivot_key_count = 0
        self.skip_next_update = False
        self.last_change_time = 0
        self.pending_reapply = False
        self.reapply_delay = 0.6
        self.time_change_cooldown = 0
        self.cooldown_duration = 0.1
        self.awaiting_real_manipulation = False
        self.original_timeline_connection = None
        self.manip_chunk_open = False
        self.event_filter = None
        self.undo_job = None
        self.redo_job = None

    def open_manip_chunk(self):
        if not self.manip_chunk_open:
            cmds.undoInfo(openChunk=True)
            self.manip_chunk_open = True

    def close_manip_chunk(self):
        if self.manip_chunk_open:
            cmds.undoInfo(closeChunk=True)
            self.manip_chunk_open = False

    def finalize_manip_chunk(self):
        if not self.manip_chunk_open:
            return
        if obj_exists(PIVOT_NULL):
            self.apply_xform_relationship()
            self.store_relationship()
        self.pending_reapply = False
        self.close_manip_chunk()

    def install_event_filter(self):
        self.remove_event_filter()
        app = QApplication.instance()
        if app:
            self.event_filter = _PivotMouseReleaseFilter(self)
            app.installEventFilter(self.event_filter)

    def remove_event_filter(self):
        if self.event_filter:
            app = QApplication.instance()
            if app:
                try:
                    app.removeEventFilter(self.event_filter)
                except:
                    pass
            self.event_filter = None

    def on_mouse_release(self):
        if self.manip_chunk_open:
            self.finalize_manip_chunk()

    def cleanup_setup(self):
        self.stop_timer()
        self.restore_timeline_connection()
        self.remove_event_filter()
        self.close_manip_chunk()

        try:
            if obj_exists(PIVOT_NULL):
                cmds.delete(PIVOT_NULL)
        except:
            pass

        try:
            if obj_exists(PIVOT_SET):
                cmds.delete(PIVOT_SET)
        except:
            pass

        try:
            if self.time_job and cmds.scriptJob(exists=self.time_job):
                cmds.scriptJob(kill=self.time_job)
        except:
            pass
        self.time_job = None

        try:
            if self.selection_job and cmds.scriptJob(exists=self.selection_job):
                cmds.scriptJob(kill=self.selection_job)
        except:
            pass
        self.selection_job = None

        try:
            if self.undo_job and cmds.scriptJob(exists=self.undo_job):
                cmds.scriptJob(kill=self.undo_job)
        except:
            pass
        self.undo_job = None

        try:
            if self.redo_job and cmds.scriptJob(exists=self.redo_job):
                cmds.scriptJob(kill=self.redo_job)
        except:
            pass
        self.redo_job = None

        self.original_matrices = {}
        self.original_frame = None
        self.locked_attrs = {}
        self.relationship_data = {}
        self.original_relationship_data = {}
        self.last_pivot_matrix = None
        self.pivot_to_ref_offset = None
        self.ref_obj = None
        self.objects_had_keys = False
        self.keys_set_this_session = False
        self.is_time_changing = False
        self.last_pivot_key_count = 0
        self.skip_next_update = False
        self.last_change_time = 0
        self.pending_reapply = False
        self.time_change_cooldown = 0
        self.awaiting_real_manipulation = False
        self.manip_chunk_open = False

    def start_timer(self):
        self.stop_timer()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start(16)

    def stop_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None

    def setup_timeline_connection(self):
        try:
            import maya.mel as mel

            time_control = mel.eval('$tmpVar=$gPlayBackSlider')

            if not time_control or not cmds.timeControl(time_control, exists=True):
                return

            self.original_timeline_connection = cmds.timeControl(
                time_control, q=True, mainListConnection=True
            )

            conn_name = "tempPivotKeysConnection"
            if cmds.selectionConnection(conn_name, exists=True):
                cmds.deleteUI(conn_name)

            cmds.selectionConnection(conn_name)

            for obj in self.sel:
                if obj_exists(obj):
                    cmds.selectionConnection(conn_name, e=True, object=obj)

            cmds.timeControl(time_control, e=True, mainListConnection=conn_name)

        except Exception as e:
            cmds.warning("Timeline connection setup failed: {}".format(str(e)))

    def restore_timeline_connection(self):
        try:
            import maya.mel as mel

            time_control = mel.eval('$tmpVar=$gPlayBackSlider')

            if not time_control or not cmds.timeControl(time_control, exists=True):
                return

            if self.original_timeline_connection:
                cmds.timeControl(time_control, e=True,
                                mainListConnection=self.original_timeline_connection)

            if cmds.selectionConnection("tempPivotKeysConnection", exists=True):
                cmds.deleteUI("tempPivotKeysConnection")

            self.original_timeline_connection = None
        except:
            pass

    def matrices_equal(self, m1, m2, tolerance=0.0001):
        if m1 is None or m2 is None:
            return False
        for i in range(16):
            if abs(m1[i] - m2[i]) > tolerance:
                return False
        return True

    def matrix_moved_significantly(self, m1, m2, threshold=0.01):
        if m1 is None or m2 is None:
            return False
        tx_diff = abs(m1[12] - m2[12])
        ty_diff = abs(m1[13] - m2[13])
        tz_diff = abs(m1[14] - m2[14])
        if tx_diff > threshold or ty_diff > threshold or tz_diff > threshold:
            return True
        rot_threshold = 0.005
        for i in range(12):
            if abs(m1[i] - m2[i]) > rot_threshold:
                return True
        return False

    def on_timer_tick(self):
        if not obj_exists(PIVOT_NULL):
            self.stop_timer()
            return

        if self.is_time_changing:
            return

        current_time_now = time.time()

        if current_time_now < self.time_change_cooldown:
            return

        current_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)

        if self.awaiting_real_manipulation:
            if self.matrix_moved_significantly(self.last_pivot_matrix, current_matrix):
                self.awaiting_real_manipulation = False
            else:
                self.last_pivot_matrix = current_matrix
                return

        matrix_changed = self.last_pivot_matrix is None or not self.matrices_equal(self.last_pivot_matrix, current_matrix, tolerance=0.0005)

        if matrix_changed:
            self.open_manip_chunk()
            self.last_pivot_matrix = current_matrix
            self.apply_xform_relationship()
            self.store_pivot_offset()
            self.last_change_time = current_time_now
            self.pending_reapply = True

        if self.pending_reapply:
            buttons_down = int(QApplication.mouseButtons()) != 0
            if not buttons_down:
                self.finalize_manip_chunk()
            elif (current_time_now - self.last_change_time) >= self.reapply_delay:
                self.finalize_manip_chunk()

        current_key_count = get_key_count(PIVOT_NULL, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        if current_key_count > self.last_pivot_key_count:
            self.open_manip_chunk()
            pivot_matrix_before = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)

            for obj in self.sel:
                if obj_exists(obj):
                    cmds.setKeyframe(obj, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

            self.keys_set_this_session = True

            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                try:
                    cmds.cutKey(PIVOT_NULL, attribute=attr, clear=True)
                except:
                    pass

            cmds.xform(PIVOT_NULL, ws=True, matrix=pivot_matrix_before)

            self.store_relationship()
            self.store_pivot_offset()

            self.last_pivot_matrix = pivot_matrix_before
            self.awaiting_real_manipulation = False
            self.pending_reapply = False
            self.last_pivot_key_count = 0

            self.close_manip_chunk()

    def cache_locked_attrs(self):
        self.locked_attrs = {}
        for obj in self.sel:
            locked = {}
            skip_t = []
            skip_r = []

            for axis in ['x', 'y', 'z']:
                if is_attr_locked(obj, 't' + axis):
                    locked['t' + axis] = True
                    skip_t.append(axis)
                if is_attr_locked(obj, 'r' + axis):
                    locked['r' + axis] = True
                    skip_r.append(axis)

            locked["skip_t"] = skip_t
            locked["skip_r"] = skip_r
            locked["all_locked"] = len(skip_t) == 3 and len(skip_r) == 3

            self.locked_attrs[obj] = locked

    def check_objects_had_keys(self):
        attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        for obj in self.sel:
            if has_keyframes(obj, attrs):
                self.objects_had_keys = True
                return
        self.objects_had_keys = False

    def store_pivot_offset(self):
        if not obj_exists(PIVOT_NULL) or not self.ref_obj or not obj_exists(self.ref_obj):
            return

        ref_matrix = om.MMatrix(cmds.xform(self.ref_obj, q=True, ws=True, matrix=True))
        pivot_matrix = om.MMatrix(cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True))

        ref_inverse = ref_matrix.inverse()
        self.pivot_to_ref_offset = pivot_matrix * ref_inverse

    def apply_pivot_from_ref(self):
        if not obj_exists(PIVOT_NULL) or not self.ref_obj or not obj_exists(self.ref_obj):
            return
        if self.pivot_to_ref_offset is None:
            return

        current_ref_matrix = om.MMatrix(cmds.xform(self.ref_obj, q=True, ws=True, matrix=True))
        new_pivot_matrix = self.pivot_to_ref_offset * current_ref_matrix

        cmds.xform(PIVOT_NULL, matrix=list(new_pivot_matrix), worldSpace=True)
        self.last_pivot_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)

    def store_relationship(self):
        if not obj_exists(PIVOT_NULL):
            return

        pivot_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)
        self.last_pivot_matrix = pivot_matrix

        self.relationship_data = {
            "pivot_matrix": pivot_matrix,
            "objects": []
        }

        for obj in self.sel:
            if not obj_exists(obj):
                continue

            obj_matrix = cmds.xform(obj, q=True, ws=True, matrix=True)
            locked_info = self.locked_attrs.get(obj, {})

            self.relationship_data["objects"].append({
                "name": obj,
                "matrix": obj_matrix,
                "locked": locked_info
            })

    def apply_xform_at_frame(self, objects):
        if not obj_exists(PIVOT_NULL):
            return
        if not self.original_relationship_data:
            return

        pivot_matrix = om.MMatrix(cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True))
        stored_pivot_matrix = om.MMatrix(self.original_relationship_data.get("pivot_matrix", []))
        stored_pivot_inverse = stored_pivot_matrix.inverse()

        for obj_data in self.original_relationship_data.get("objects", []):
            obj_name = obj_data.get("name")
            if not obj_name or not obj_exists(obj_name):
                continue
            if obj_name not in objects:
                continue

            locked_info = obj_data.get("locked", {})
            if locked_info.get("all_locked", False):
                continue

            stored_obj_matrix = om.MMatrix(obj_data.get("matrix", []))
            target_matrix = stored_obj_matrix * stored_pivot_inverse * pivot_matrix

            skip_t = locked_info.get("skip_t", [])
            skip_r = locked_info.get("skip_r", [])

            if len(skip_t) == 0 and len(skip_r) == 0:
                cmds.xform(obj_name, matrix=list(target_matrix), worldSpace=True)
            else:
                xform = om.MTransformationMatrix(target_matrix)

                if len(skip_t) < 3:
                    new_pos = xform.translation(om.MSpace.kWorld)
                    current_pos = cmds.xform(obj_name, q=True, ws=True, t=True)
                    final_pos = [
                        current_pos[0] if 'x' in skip_t else new_pos.x,
                        current_pos[1] if 'y' in skip_t else new_pos.y,
                        current_pos[2] if 'z' in skip_t else new_pos.z
                    ]
                    cmds.xform(obj_name, ws=True, t=final_pos)

                if len(skip_r) < 3:
                    euler = xform.rotation()
                    new_rot = [
                        om.MAngle(euler.x).asDegrees(),
                        om.MAngle(euler.y).asDegrees(),
                        om.MAngle(euler.z).asDegrees()
                    ]
                    current_rot = cmds.xform(obj_name, q=True, ws=True, ro=True)
                    final_rot = [
                        current_rot[0] if 'x' in skip_r else new_rot[0],
                        current_rot[1] if 'y' in skip_r else new_rot[1],
                        current_rot[2] if 'z' in skip_r else new_rot[2]
                    ]
                    cmds.xform(obj_name, ws=True, ro=final_rot)

            cmds.setKeyframe(obj_name, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

    def apply_xform_relationship(self):
        if not self.relationship_data or not obj_exists(PIVOT_NULL):
            return

        stored_pivot_matrix = om.MMatrix(self.relationship_data.get("pivot_matrix", []))
        stored_pivot_inverse = stored_pivot_matrix.inverse()
        current_pivot_matrix = om.MMatrix(cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True))

        for obj_data in self.relationship_data.get("objects", []):
            obj_name = obj_data.get("name")
            if not obj_name or not obj_exists(obj_name):
                continue

            locked_info = obj_data.get("locked", {})
            if locked_info.get("all_locked", False):
                continue

            stored_obj_matrix = om.MMatrix(obj_data.get("matrix", []))
            target_matrix = stored_obj_matrix * stored_pivot_inverse * current_pivot_matrix

            skip_t = locked_info.get("skip_t", [])
            skip_r = locked_info.get("skip_r", [])

            if len(skip_t) == 0 and len(skip_r) == 0:
                cmds.xform(obj_name, matrix=list(target_matrix), worldSpace=True)
            else:
                xform = om.MTransformationMatrix(target_matrix)

                if len(skip_t) < 3:
                    new_pos = xform.translation(om.MSpace.kWorld)
                    current_pos = cmds.xform(obj_name, q=True, ws=True, t=True)
                    final_pos = [
                        current_pos[0] if 'x' in skip_t else new_pos.x,
                        current_pos[1] if 'y' in skip_t else new_pos.y,
                        current_pos[2] if 'z' in skip_t else new_pos.z
                    ]
                    cmds.xform(obj_name, ws=True, t=final_pos)

                if len(skip_r) < 3:
                    euler = xform.rotation()
                    new_rot = [
                        om.MAngle(euler.x).asDegrees(),
                        om.MAngle(euler.y).asDegrees(),
                        om.MAngle(euler.z).asDegrees()
                    ]
                    current_rot = cmds.xform(obj_name, q=True, ws=True, ro=True)
                    final_rot = [
                        current_rot[0] if 'x' in skip_r else new_rot[0],
                        current_rot[1] if 'y' in skip_r else new_rot[1],
                        current_rot[2] if 'z' in skip_r else new_rot[2]
                    ]
                    cmds.xform(obj_name, ws=True, ro=final_rot)

    def on_time_changed(self):
        if not obj_exists(PIVOT_NULL):
            return

        self.is_time_changing = True

        self.pending_reapply = False

        autokey_state = cmds.autoKeyframe(q=True, state=True)
        if autokey_state:
            cmds.autoKeyframe(state=False)

        opened_here = not self.manip_chunk_open
        self.open_manip_chunk()

        try:
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                try:
                    cmds.cutKey(PIVOT_NULL, attribute=attr, clear=True)
                except:
                    pass

            self.apply_pivot_from_ref()

            self.store_relationship()
            self.store_pivot_offset()

        finally:
            if autokey_state:
                cmds.autoKeyframe(state=True)
            if opened_here:
                self.close_manip_chunk()

        self.last_pivot_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)

        self.last_pivot_key_count = 0

        self.time_change_cooldown = time.time() + self.cooldown_duration

        self.awaiting_real_manipulation = True

        self.is_time_changing = False

        self.time_job = cmds.scriptJob(runOnce=True, killWithScene=True, event=["timeChanged", time_changed])

    def save_relationship_to_disk(self):
        if not obj_exists(PIVOT_NULL):
            return
        if not self.original_matrices:
            return

        selection = list(self.original_matrices.keys())
        if not selection:
            return

        data = load_offsets()
        data["last_selection"] = selection

        pivot_pos = cmds.xform(PIVOT_NULL, q=True, ws=True, rp=True)
        pivot_rot = cmds.xform(PIVOT_NULL, q=True, ws=True, ro=True)

        ref_obj = selection[-1]
        ref_pos = cmds.xform(ref_obj, q=True, ws=True, t=True)
        ref_rot = cmds.xform(ref_obj, q=True, ws=True, ro=True)
        ref_matrix = om.MMatrix(cmds.xform(ref_obj, q=True, ws=True, matrix=True))

        world_offset = om.MVector(
            pivot_pos[0] - ref_pos[0],
            pivot_pos[1] - ref_pos[1],
            pivot_pos[2] - ref_pos[2]
        )

        ref_xform = om.MTransformationMatrix(ref_matrix)
        ref_xform.setTranslation(om.MVector(0, 0, 0), om.MSpace.kWorld)
        rot_matrix_inv = ref_xform.asMatrix().inverse()

        local_offset = world_offset * rot_matrix_inv

        offset_rot = [
            pivot_rot[0] - ref_rot[0],
            pivot_rot[1] - ref_rot[1],
            pivot_rot[2] - ref_rot[2]
        ]

        offset_data = {
            "offset_pos": [local_offset.x, local_offset.y, local_offset.z],
            "offset_rot": offset_rot,
            "ref_obj": ref_obj
        }

        if len(selection) == 1:
            data["single_offsets"][ref_obj] = offset_data
        else:
            sel_sorted = sorted(selection)
            found = False
            for group in data["multi_offsets"]:
                if sorted(group["objects"]) == sel_sorted:
                    group["offset_data"] = offset_data
                    found = True
                    break
            if not found:
                data["multi_offsets"].append({
                    "objects": list(selection),
                    "offset_data": offset_data
                })

        save_offsets(data)

    def apply_stored_offset(self, selection):
        if not obj_exists(PIVOT_NULL):
            return False

        path = get_prefs_path()
        if not os.path.exists(path):
            return False

        global _cache_valid
        _cache_valid = False
        data = load_offsets()
        offset_data = None

        if len(selection) == 1:
            obj = selection[0]
            single_offsets = data.get("single_offsets", {})
            if obj in single_offsets:
                offset_data = single_offsets[obj]
        else:
            multi_offsets = data.get("multi_offsets", [])
            sel_sorted = sorted(selection)
            for group in multi_offsets:
                if sorted(group.get("objects", [])) == sel_sorted:
                    if "offset_data" in group:
                        offset_data = group["offset_data"]
                    break

        if not offset_data or "offset_pos" not in offset_data:
            return False

        ref_obj = offset_data.get("ref_obj", selection[-1])
        if not obj_exists(ref_obj):
            ref_obj = selection[-1]

        ref_matrix = om.MMatrix(cmds.xform(ref_obj, q=True, ws=True, matrix=True))
        ref_pos = cmds.xform(ref_obj, q=True, ws=True, t=True)

        offset_pos = offset_data["offset_pos"]
        offset_rot = offset_data["offset_rot"]
        local_offset = om.MVector(offset_pos[0], offset_pos[1], offset_pos[2])

        ref_xform = om.MTransformationMatrix(ref_matrix)
        ref_xform.setTranslation(om.MVector(0, 0, 0), om.MSpace.kWorld)
        rot_matrix = ref_xform.asMatrix()

        world_offset = local_offset * rot_matrix

        new_pivot_pos = [
            ref_pos[0] + world_offset.x,
            ref_pos[1] + world_offset.y,
            ref_pos[2] + world_offset.z
        ]

        ref_rot = cmds.xform(ref_obj, q=True, ws=True, ro=True)
        new_pivot_rot = [
            ref_rot[0] + offset_rot[0],
            ref_rot[1] + offset_rot[1],
            ref_rot[2] + offset_rot[2]
        ]

        cmds.xform(PIVOT_NULL, ws=True, t=new_pivot_pos)
        cmds.xform(PIVOT_NULL, ws=True, ro=new_pivot_rot)

        return True

    def create(self):
        if obj_exists(PIVOT_NULL):
            self.clear()
            return

        self.sel = cmds.ls(selection=True)

        if not self.sel:
            data = load_offsets()
            last_sel = data.get("last_selection", [])
            valid_sel = [obj for obj in last_sel if obj_exists(obj)]

            if valid_sel:
                set_selection(valid_sel)
                self.sel = valid_sel
            else:
                return

        try:
            cmds.refresh(suspend=True)
            cmds.undoInfo(openChunk=True)
            try:
                self.ref_obj = self.sel[-1]
                cmds.sets(self.sel, name=PIVOT_SET)

                self.original_frame = get_current_time()

                self.original_matrices = {}
                for obj in self.sel:
                    self.original_matrices[obj] = cmds.xform(obj, q=True, ws=True, matrix=True)

                self.cache_locked_attrs()
                self.check_objects_had_keys()

                pivot_grp = cmds.group(empty=True, name=PIVOT_NULL)

                for attr in ['sx', 'sy', 'sz', 'v']:
                    cmds.setAttr(PIVOT_NULL + '.' + attr, lock=True, keyable=False, channelBox=False)

                cmds.matchTransform(pivot_grp, self.ref_obj, pos=True, rot=True)
                self.apply_stored_offset(self.sel)

                self.store_relationship()
                self.original_relationship_data = copy.deepcopy(self.relationship_data)
                self.store_pivot_offset()
                self.last_pivot_key_count = 0

                self.setup_timeline_connection()
            finally:
                cmds.undoInfo(closeChunk=True)

            self.start_timer()
            self.install_event_filter()

        except Exception as e:
            cmds.refresh(suspend=False)
            self.cleanup_setup()
            cmds.warning("Pivot tool error: {}".format(str(e)))
            return
        finally:
            cmds.refresh(suspend=False)

        cmds.select(PIVOT_NULL)
        cmds.setToolTo("moveSuperContext")
        cmds.ctxEditMode()

        self.selection_job = cmds.scriptJob(runOnce=True, killWithScene=True, event=["SelectionChanged", clear])
        self.time_job = cmds.scriptJob(runOnce=True, killWithScene=True, event=["timeChanged", time_changed])
        self.undo_job = cmds.scriptJob(killWithScene=True, event=["Undo", undo_redo_sync])
        self.redo_job = cmds.scriptJob(killWithScene=True, event=["Redo", undo_redo_sync])

    def resync_after_undo(self):
        if not obj_exists(PIVOT_NULL):
            self.cleanup_setup()
            return

        self.pending_reapply = False
        self.manip_chunk_open = False
        self.awaiting_real_manipulation = True

        if obj_exists(PIVOT_SET):
            current_members = cmds.sets(PIVOT_SET, q=True) or []
            if current_members:
                self.sel = current_members

        self.cache_locked_attrs()
        self.store_relationship()
        self.store_pivot_offset()

        if obj_exists(PIVOT_NULL):
            self.last_pivot_matrix = cmds.xform(PIVOT_NULL, q=True, ws=True, matrix=True)

        self.last_pivot_key_count = get_key_count(PIVOT_NULL, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

    def bake_keys_from_pivot(self, objects):
        if not obj_exists(PIVOT_NULL):
            return

        pivot_keyframes = get_all_keyframes(PIVOT_NULL, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        if not pivot_keyframes:
            return

        current_frame = get_current_time()

        try:
            cmds.undoInfo(openChunk=True)
            for frame in pivot_keyframes:
                set_current_time(frame)
                self.apply_xform_at_frame(objects)
        finally:
            cmds.undoInfo(closeChunk=True)
            set_current_time(current_frame)

    def clear(self):
        self.remove_event_filter()
        self.close_manip_chunk()

        objects = None
        transforms = {}

        if obj_exists(PIVOT_SET):
            objects = cmds.sets(PIVOT_SET, q=True) or []

        if objects:
            for obj in objects:
                if obj_exists(obj):
                    transforms[obj] = cmds.xform(obj, q=True, ws=True, matrix=True)

        try:
            cmds.refresh(suspend=True)
            cmds.undoInfo(openChunk=True)

            self.stop_timer()
            self.restore_timeline_connection()

            if objects and obj_exists(PIVOT_NULL):
                self.save_relationship_to_disk()

            if obj_exists(PIVOT_NULL):
                cmds.delete(PIVOT_NULL)

            if obj_exists(PIVOT_SET):
                cmds.delete(PIVOT_SET)

            for obj, mtx in transforms.items():
                if obj_exists(obj):
                    try:
                        cmds.xform(obj, ws=True, matrix=mtx)
                    except:
                        pass

            if self.objects_had_keys or self.keys_set_this_session:
                for obj in (objects or []):
                    if obj_exists(obj):
                        cmds.setKeyframe(obj, attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
                for obj in (objects or []):
                    if obj_exists(obj):
                        run_euler_filter(obj)

        except Exception as e:
            cmds.warning("Pivot tool error during clear: {}".format(str(e)))
            self.cleanup_setup()
        finally:
            cmds.undoInfo(closeChunk=True)
            cmds.refresh(suspend=False)

        self.original_matrices = {}
        self.original_frame = None
        self.relationship_data = {}
        self.original_relationship_data = {}
        self.last_pivot_key_count = 0
        self.last_change_time = 0
        self.pending_reapply = False
        self.time_change_cooldown = 0
        self.awaiting_real_manipulation = False
        self.keys_set_this_session = False

        try:
            if self.time_job and cmds.scriptJob(exists=self.time_job):
                cmds.scriptJob(kill=self.time_job)
        except:
            pass
        self.time_job = None

        try:
            if self.selection_job and cmds.scriptJob(exists=self.selection_job):
                cmds.scriptJob(kill=self.selection_job)
        except:
            pass
        self.selection_job = None

        try:
            if self.undo_job and cmds.scriptJob(exists=self.undo_job):
                cmds.scriptJob(kill=self.undo_job)
        except:
            pass
        self.undo_job = None

        try:
            if self.redo_job and cmds.scriptJob(exists=self.redo_job):
                cmds.scriptJob(kill=self.redo_job)
        except:
            pass
        self.redo_job = None

        if objects:
            set_selection(objects)


_pivot = LiveTempPivot()


def pivot():
    _pivot.create()


def clear():
    _pivot.clear()


def time_changed():
    _pivot.on_time_changed()


def undo_redo_sync():
    _pivot.resync_after_undo()


def save_pivot():
    _pivot.save_relationship_to_disk()


def reset_offsets():
    global _cache_valid
    _cache_valid = False
    save_offsets({"single_offsets": {}, "multi_offsets": [], "last_selection": []})


load_offsets()

pivot()