from maya import cmds

def offset_sequential_keys(offset):
    selection = cmds.ls(selection=True)
    if not selection:
        return

    selected_keyframes = cmds.keyframe(query=True, selected=True)

    def get_infinity(obj, attr):
        curves = cmds.listConnections("{}.{}".format(obj, attr), type="animCurve") or []
        if not curves:
            return None, None
        return cmds.getAttr(curves[0] + ".preInfinity"), cmds.getAttr(curves[0] + ".postInfinity")

    def set_infinity(obj, attr, pre, post):
        if pre is None:
            return
        curves = cmds.listConnections("{}.{}".format(obj, attr), type="animCurve") or []
        if curves:
            cmds.setAttr(curves[0] + ".preInfinity", pre)
            cmds.setAttr(curves[0] + ".postInfinity", post)

    try:
        cmds.undoInfo(openChunk=True, chunkName="Offset Sequentially")
        num_objs = len(selection)

        if selected_keyframes:
            key_selection_map = {}
            for obj in selection:
                obj_attrs = cmds.listAttr(obj, keyable=True) or []
                for attr in obj_attrs:
                    try:
                        times = cmds.keyframe(obj, attribute=attr, query=True, selected=True)
                        if times:
                            key_selection_map.setdefault((obj, attr), []).extend(times)
                    except:
                        pass

            for i, ((obj, attr), times) in enumerate(key_selection_map.items()):
                unique_times = sorted(set(times))
                obj_offset = offset * i if num_objs > 1 else offset
                values = cmds.keyframe(obj, attribute=attr, time=(min(unique_times), max(unique_times)), query=True, valueChange=True)
                pre_infinity, post_infinity = get_infinity(obj, attr)

                cmds.cutKey(obj, attribute=attr, time=(min(unique_times), max(unique_times)))
                new_times = [t + obj_offset for t in unique_times]
                for t, v in zip(new_times, values):
                    cmds.setKeyframe(obj, attribute=attr, time=t, value=v)
                for t in new_times:
                    cmds.selectKey(obj, attribute=attr, time=(t, t), add=True)

                set_infinity(obj, attr, pre_infinity, post_infinity)

        else:
            selected_attrs = cmds.channelBox("mainChannelBox", query=True, sma=True)
            if not selected_attrs:
                selected_attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']

            for i, obj in enumerate(selection):
                obj_offset = offset * i if num_objs > 1 else offset
                for attr in selected_attrs:
                    if not cmds.objExists("{}.{}".format(obj, attr)):
                        continue
                    if cmds.keyframe(obj, attribute=attr, query=True, keyframeCount=True):
                        times = cmds.keyframe(obj, attribute=attr, query=True)
                        values = cmds.keyframe(obj, attribute=attr, query=True, valueChange=True)
                        pre_infinity, post_infinity = get_infinity(obj, attr)

                        cmds.cutKey(obj, attribute=attr, time=(min(times), max(times)))
                        for t, v in zip(times, values):
                            cmds.setKeyframe(obj, attribute=attr, time=t + obj_offset, value=v)

                        set_infinity(obj, attr, pre_infinity, post_infinity)

    except Exception:
        pass
    finally:
        cmds.undoInfo(closeChunk=True)


offset_sequential_keys(2)
