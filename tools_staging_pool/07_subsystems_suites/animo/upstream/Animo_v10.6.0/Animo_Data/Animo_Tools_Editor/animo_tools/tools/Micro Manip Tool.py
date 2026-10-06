import math
import maya.cmds as cmds
import maya.api.OpenMaya as om2


class MicroManupulation(object):

    DAMPING = 10.0
    SPIN_DAMPING = 5.0
    MAX_TICK_DEGREES = 8.0

    LOCAL_SPIN_DAMPING = 8.0
    LOCAL_MAX_TICK_DEGREES = 2.2

    CTX_MOVE = "Move"
    CTX_SPIN = "Rotate"
    CTX_SCALE = "Scale"

    PREF_KEY = "softTouchEngaged"

    TAG = "_animo_micro_manip"

    pending_move = {}
    pending_spin = {}
    pending_scale = {}

    move_hooks = {}
    spin_hooks = {}
    scale_hooks = {}

    applying = set()

    @classmethod
    def engaged(cls):
        return bool(cmds.optionVar(q=cls.PREF_KEY)) if cmds.optionVar(exists=cls.PREF_KEY) else False

    @staticmethod
    def writable(obj, attr):
        try:
            return cmds.getAttr("{}.{}".format(obj, attr), settable=True)
        except Exception:
            return False

    @staticmethod
    def to_mobject(name):
        sel = om2.MSelectionList()
        sel.add(name)
        return sel.getDependNode(0)

    @staticmethod
    def read_quat(obj):
        order = cmds.getAttr(obj + ".rotateOrder")
        rx, ry, rz = cmds.getAttr(obj + ".rotate")[0]
        euler = om2.MEulerRotation(math.radians(rx), math.radians(ry), math.radians(rz), order)
        return euler.asQuaternion()

    @staticmethod
    def quat_to_euler(quat, order):
        euler = quat.asEulerRotation()
        euler.reorderIt(order)
        return [math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z)]

    @classmethod
    def announce(cls, state):
        cmds.inViewMessage(
            amg="Micro Manip <hl>{}</hl>".format("ON" if state else "OFF"),
            pos="midCenter",
            fontSize=18,
            fade=True,
            fadeStayTime=1200,
        )

    @classmethod
    def live_selection(cls):
        selected = cmds.ls(selection=True, long=True) or []
        return [s for s in selected if cls.TAG not in s]


    @classmethod
    def on_move_tick(cls, msg, plug, other_plug, client_data):
        if not (msg & om2.MNodeMessage.kAttributeSet):
            return
        real_obj = client_data
        if real_obj in cls.applying:
            return
        data = cls.pending_move.get(real_obj)
        if not data or data.get("finishing"):
            return
        origin = data.get("origin")
        virtual = data.get("virtual")
        written = data.get("written")
        if origin is None or virtual is None or written is None:
            cls.pending_move.pop(real_obj, None)
            return
        if not cmds.objExists(real_obj):
            return

        raw = cmds.getAttr(real_obj + ".translate")[0]
        new_virtual = [v + (r - w) for v, r, w in zip(virtual, raw, written)]
        damped = [o + (nv - o) / cls.DAMPING for o, nv in zip(origin, new_virtual)]

        data["virtual"] = new_virtual
        data["written"] = damped

        cls.applying.add(real_obj)
        try:
            for axis, value in zip(("X", "Y", "Z"), damped):
                attr = "translate" + axis
                if cls.writable(real_obj, attr):
                    cmds.setAttr("{}.{}".format(real_obj, attr), value)
        finally:
            cls.applying.discard(real_obj)

    @classmethod
    def begin_move(cls, *_):
        if not cls.engaged():
            return
        cls.finish_move_now()

        selected = cls.live_selection()
        if not selected:
            return

        for real_obj in selected:
            origin = list(cmds.getAttr(real_obj + ".translate")[0])
            cls.pending_move[real_obj] = {
                "origin": origin,
                "virtual": list(origin),
                "written": list(origin),
                "finishing": False,
            }

            mobj = cls.to_mobject(real_obj)
            hook_id = om2.MNodeMessage.addAttributeChangedCallback(mobj, cls.on_move_tick, real_obj)
            cls.move_hooks[real_obj] = hook_id

    @classmethod
    def finish_move_now(cls):
        for hook_id in cls.move_hooks.values():
            om2.MMessage.removeCallback(hook_id)
        cls.move_hooks.clear()
        cls.pending_move.clear()

    @classmethod
    def finish_move(cls, *_):
        if not cls.pending_move:
            return
        for real_obj, data in cls.pending_move.items():
            data["finishing"] = True
            written = data.get("written")
            if written is None:
                continue
            if not cmds.objExists(real_obj):
                continue

            cls.applying.add(real_obj)
            try:
                for axis, value in zip(("X", "Y", "Z"), written):
                    attr = "translate" + axis
                    if cls.writable(real_obj, attr):
                        cmds.setAttr("{}.{}".format(real_obj, attr), value)
            finally:
                cls.applying.discard(real_obj)

        cmds.evalDeferred(cls.finish_move_now)


    @classmethod
    def on_scale_tick(cls, msg, plug, other_plug, client_data):
        if not (msg & om2.MNodeMessage.kAttributeSet):
            return
        real_obj = client_data
        if real_obj in cls.applying:
            return
        data = cls.pending_scale.get(real_obj)
        if not data or data.get("finishing"):
            return
        origin = data.get("origin")
        virtual = data.get("virtual")
        written = data.get("written")
        if origin is None or virtual is None or written is None:
            cls.pending_scale.pop(real_obj, None)
            return
        if not cmds.objExists(real_obj):
            return

        raw = cmds.getAttr(real_obj + ".scale")[0]
        new_virtual = [v + (r - w) for v, r, w in zip(virtual, raw, written)]
        damped = [o + (nv - o) / cls.DAMPING for o, nv in zip(origin, new_virtual)]

        data["virtual"] = new_virtual
        data["written"] = damped

        cls.applying.add(real_obj)
        try:
            for axis, value in zip(("X", "Y", "Z"), damped):
                attr = "scale" + axis
                if cls.writable(real_obj, attr):
                    cmds.setAttr("{}.{}".format(real_obj, attr), value)
        finally:
            cls.applying.discard(real_obj)

    @classmethod
    def begin_scale(cls, *_):
        if not cls.engaged():
            return
        cls.finish_scale_now()

        selected = cls.live_selection()
        if not selected:
            return

        for real_obj in selected:
            origin = list(cmds.getAttr(real_obj + ".scale")[0])
            cls.pending_scale[real_obj] = {
                "origin": origin,
                "virtual": list(origin),
                "written": list(origin),
                "finishing": False,
            }

            mobj = cls.to_mobject(real_obj)
            hook_id = om2.MNodeMessage.addAttributeChangedCallback(mobj, cls.on_scale_tick, real_obj)
            cls.scale_hooks[real_obj] = hook_id

    @classmethod
    def finish_scale_now(cls):
        for hook_id in cls.scale_hooks.values():
            om2.MMessage.removeCallback(hook_id)
        cls.scale_hooks.clear()
        cls.pending_scale.clear()

    @classmethod
    def finish_scale(cls, *_):
        if not cls.pending_scale:
            return
        for real_obj, data in cls.pending_scale.items():
            data["finishing"] = True
            written = data.get("written")
            if written is None:
                continue
            if not cmds.objExists(real_obj):
                continue

            cls.applying.add(real_obj)
            try:
                for axis, value in zip(("X", "Y", "Z"), written):
                    attr = "scale" + axis
                    if cls.writable(real_obj, attr):
                        cmds.setAttr("{}.{}".format(real_obj, attr), value)
            finally:
                cls.applying.discard(real_obj)

        cmds.evalDeferred(cls.finish_scale_now)


    @classmethod
    def ghost_name(cls, real_obj):
        short = real_obj.split("|")[-1]
        idx = short.find(cls.TAG)
        if idx != -1:
            short = short[:idx]
        return short + cls.TAG

    @classmethod
    def purge_spin_ghosts(cls):
        stale = cmds.ls("*{}*".format(cls.TAG), long=True, type="transform") or []
        for node in stale:
            if cmds.objExists(node):
                cmds.delete(node)

    @classmethod
    def on_spin_tick(cls, msg, plug, other_plug, client_data):
        try:
            if not (msg & om2.MNodeMessage.kAttributeSet):
                return
            real_obj = client_data
            data = cls.pending_spin.get(real_obj)
            if not data:
                return
            ghost = data.get("ghost")
            order = data.get("order")
            last_pose = data.get("last_pose")
            is_local = data.get("is_local", False)
            if ghost is None or order is None or last_pose is None:
                cls.pending_spin.pop(real_obj, None)
                return
            if not cmds.objExists(ghost):
                return

            pose_now = cls.read_quat(ghost)
            nudge = pose_now * last_pose.inverse()
            if nudge.w < 0.0:
                nudge = om2.MQuaternion(-nudge.x, -nudge.y, -nudge.z, -nudge.w)

            neutral = om2.MQuaternion()
            if nudge.isEquivalent(neutral, 1e-9):
                return

            if is_local:
                cls._apply_local_tick(real_obj, data, order, nudge, pose_now)
            else:
                cls._apply_standard_tick(real_obj, data, order, nudge, pose_now, neutral)
        except Exception:
            import traceback
            cmds.warning("[MicroManip] on_spin_tick error:\n" + traceback.format_exc())

    @classmethod
    def _apply_standard_tick(cls, real_obj, data, order, nudge, pose_now, neutral):
        blended = data.get("blended")
        if blended is None:
            cls.pending_spin.pop(real_obj, None)
            return

        angle = 2.0 * math.acos(min(1.0, max(-1.0, nudge.w)))
        max_angle = math.radians(cls.MAX_TICK_DEGREES)
        if angle > max_angle:
            axis, _ = nudge.asAxisAngle()
            half = max_angle / 2.0
            nudge = om2.MQuaternion(
                math.sin(half) * axis.x,
                math.sin(half) * axis.y,
                math.sin(half) * axis.z,
                math.cos(half),
            )

        soft_nudge = om2.MQuaternion.slerp(neutral, nudge, 1.0 / cls.SPIN_DAMPING)
        new_blended = soft_nudge * blended

        data["last_pose"] = pose_now
        data["blended"] = new_blended

        eulers = cls.quat_to_euler(new_blended, order)
        for axis_name, value in zip(("X", "Y", "Z"), eulers):
            attr = "rotate" + axis_name
            if cls.writable(real_obj, attr):
                cmds.setAttr("{}.{}".format(real_obj, attr), value)

    @classmethod
    def _apply_local_tick(cls, real_obj, data, order, nudge, pose_now):
        origin = data.get("origin")
        total_vec = data.get("total_vec")
        if origin is None or total_vec is None:
            cls.pending_spin.pop(real_obj, None)
            return

        axis, angle = nudge.asAxisAngle()
        max_angle = math.radians(cls.LOCAL_MAX_TICK_DEGREES)
        if angle > max_angle:
            angle = max_angle
        tick_vec = om2.MVector(axis.x, axis.y, axis.z) * angle

        new_total_vec = total_vec + tick_vec
        data["last_pose"] = pose_now
        data["total_vec"] = new_total_vec

        damped_vec = new_total_vec / cls.LOCAL_SPIN_DAMPING
        damped_angle = damped_vec.length()
        if damped_angle < 1e-9:
            return
        damped_axis = damped_vec.normal()
        half = damped_angle / 2.0
        damped_delta = om2.MQuaternion(
            math.sin(half) * damped_axis.x,
            math.sin(half) * damped_axis.y,
            math.sin(half) * damped_axis.z,
            math.cos(half),
        )

        new_orientation = damped_delta * origin

        eulers = cls.quat_to_euler(new_orientation, order)
        for axis_name, value in zip(("X", "Y", "Z"), eulers):
            attr = "rotate" + axis_name
            if cls.writable(real_obj, attr):
                cmds.setAttr("{}.{}".format(real_obj, attr), value)

    @classmethod
    def begin_spin(cls, *_):
        if not cls.engaged():
            return
        cls.finish_spin_now()
        cls.purge_spin_ghosts()

        selected = cls.live_selection()
        if not selected:
            return

        try:
            current_mode = cmds.manipRotateContext(cls.CTX_SPIN, query=True, mode=True)
        except Exception:
            current_mode = None
        is_local = (current_mode == 0)

        ghosts = []
        for real_obj in selected:
            order = cmds.getAttr(real_obj + ".rotateOrder")
            pose = cls.read_quat(real_obj)
            ghost = cmds.duplicate(real_obj, name=cls.ghost_name(real_obj), parentOnly=True)[0]
            try:
                cmds.setAttr(ghost + ".hiddenInOutliner", True)
                import maya.mel as mel
                mel.eval("AEdagNodeCommonRefreshOutliners()")
            except Exception:
                pass
            cls.pending_spin[real_obj] = {
                "ghost": ghost,
                "order": order,
                "last_pose": pose,
                "blended": pose,
                "origin": pose,
                "total_vec": om2.MVector(0.0, 0.0, 0.0),
                "is_local": is_local,
            }
            ghosts.append(ghost)

            mobj = cls.to_mobject(ghost)
            hook_id = om2.MNodeMessage.addAttributeChangedCallback(mobj, cls.on_spin_tick, real_obj)
            cls.spin_hooks[real_obj] = hook_id

        if ghosts:
            cmds.select(ghosts, replace=True)

    @classmethod
    def finish_spin_now(cls):
        for hook_id in cls.spin_hooks.values():
            om2.MMessage.removeCallback(hook_id)
        cls.spin_hooks.clear()

        real_objs = list(cls.pending_spin.keys())
        for real_obj, data in list(cls.pending_spin.items()):
            ghost = data.get("ghost")
            if ghost and cmds.objExists(ghost):
                cmds.delete(ghost)

        cls.pending_spin.clear()
        if real_objs:
            cmds.select(real_objs, replace=True)

    @classmethod
    def finish_spin(cls, *_):
        if not cls.pending_spin:
            return
        cmds.evalDeferred(cls.finish_spin_now)


    @staticmethod
    def spawn_ctx_if_missing(cmd_func, name):
        if not cmds.contextInfo(name, exists=True):
            cmd_func(name)

    @classmethod
    def wire_contexts(cls):
        cls.spawn_ctx_if_missing(cmds.manipMoveContext, cls.CTX_MOVE)
        cls.spawn_ctx_if_missing(cmds.manipRotateContext, cls.CTX_SPIN)
        cls.spawn_ctx_if_missing(cmds.manipScaleContext, cls.CTX_SCALE)

        cmds.manipMoveContext(cls.CTX_MOVE, e=True,
                               interactiveUpdate=True,
                               preDragCommand=(cls.begin_move, "transform"),
                               postDragCommand=(cls.finish_move, "transform"))
        cmds.manipRotateContext(cls.CTX_SPIN, e=True,
                                 preDragCommand=(cls.begin_spin, "transform"),
                                 postDragCommand=(cls.finish_spin, "transform"))
        cmds.manipScaleContext(cls.CTX_SCALE, e=True,
                                preDragCommand=(cls.begin_scale, "transform"),
                                postDragCommand=(cls.finish_scale, "transform"))

    @classmethod
    def flip(cls):
        cls.wire_contexts()
        cls.purge_spin_ghosts()
        was_on = cls.engaged()
        now_on = not was_on
        cmds.optionVar(intValue=(cls.PREF_KEY, 1 if now_on else 0))
        cls.announce(now_on)
        return now_on


MicroManupulation.flip()


PREV_ROTATE_MODE_KEY = "microManipPrevRotateMode"
PREV_ROTATE_ORIENT_KEY = "microManipPrevRotateOrient"
PREV_ROTATE_STATE_FLAG = "microManipPrevRotateStateSet"


def capture_rotate_context_state():
    ctx = MicroManupulation.CTX_SPIN
    try:
        mode = cmds.manipRotateContext(ctx, query=True, mode=True)
    except Exception:
        mode = 0
    try:
        orient_obj = cmds.manipRotateContext(ctx, query=True, orientObject=True)
    except Exception:
        orient_obj = ""
    return mode, orient_obj


def store_rotate_context_state(mode, orient_obj):
    cmds.optionVar(intValue=(PREV_ROTATE_MODE_KEY, mode))
    cmds.optionVar(stringValue=(PREV_ROTATE_ORIENT_KEY, orient_obj or ""))
    cmds.optionVar(intValue=(PREV_ROTATE_STATE_FLAG, 1))


def restore_rotate_context_state():
    if not cmds.optionVar(exists=PREV_ROTATE_STATE_FLAG):
        return
    if not cmds.optionVar(query=PREV_ROTATE_STATE_FLAG):
        return

    mode = cmds.optionVar(query=PREV_ROTATE_MODE_KEY)
    orient_obj = cmds.optionVar(query=PREV_ROTATE_ORIENT_KEY)
    ctx = MicroManupulation.CTX_SPIN

    try:
        if orient_obj and cmds.objExists(orient_obj):
            cmds.manipRotateContext(ctx, edit=True, mode=mode, orientObject=orient_obj)
        else:
            cmds.manipRotateContext(ctx, edit=True, mode=mode)
    except Exception:
        pass

    cmds.optionVar(intValue=(PREV_ROTATE_STATE_FLAG, 0))


def manip_camera_mode(enable):
    if not enable:
        restore_rotate_context_state()
        return

    current_ctx = cmds.currentCtx()

    if current_ctx != "RotateSuperContext":
        return

    panel = cmds.getPanel(underPointer=True)

    if not panel or cmds.getPanel(typeOf=panel) != "modelPanel":
        panel = cmds.getPanel(withFocus=True)

    if not panel or cmds.getPanel(typeOf=panel) != "modelPanel":
        model_panels = cmds.getPanel(type="modelPanel")
        if model_panels:
            panel = model_panels[0]
        else:
            return

    camera = cmds.modelPanel(panel, query=True, camera=True)

    if cmds.nodeType(camera) == "camera":
        camera = cmds.listRelatives(camera, parent=True, fullPath=True)[0]

    prev_mode, prev_orient = capture_rotate_context_state()
    store_rotate_context_state(prev_mode, prev_orient)

    cmds.manipRotateContext(MicroManupulation.CTX_SPIN, edit=True, mode=3, orientObject=camera)


manip_camera_mode(MicroManupulation.engaged())