import maya.cmds as cmds

def orient_constraint_selected_channels():
    selected_objects = cmds.ls(selection=True)

    if len(selected_objects) < 2:
        cmds.warning("Please select at least 2 objects. First is parent, rest are children.")
        return

    selected_channels = None
    try:
        selected_channels = cmds.channelBox('mainChannelBox', q=True, selectedMainAttributes=True)
    except:
        pass

    if not selected_channels:
        try:
            selected_channels = cmds.channelBox('mainChannelBox', q=True, selectedAttributes=True)
        except:
            pass

    if not selected_channels:
        channel_boxes = cmds.lsUI(type='channelBox')
        for cb in channel_boxes:
            try:
                selected_channels = cmds.channelBox(cb, q=True, selectedMainAttributes=True)
                if selected_channels:
                    break
            except:
                continue

    if not selected_channels:
        selected_channels = ['rx', 'ry', 'rz']

    parent_obj = selected_objects[0]
    child_objects = selected_objects[1:]

    for child in child_objects:
        actual_channels = []

        for ch in selected_channels:
            if ch not in ('rx', 'ry', 'rz'):
                continue
            full_attr = f"{child}.{ch}"
            if cmds.objExists(full_attr):
                try:
                    is_locked = cmds.getAttr(full_attr, lock=True)
                    is_keyable = cmds.getAttr(full_attr, keyable=True)
                    is_channelbox = cmds.getAttr(full_attr, channelBox=True)

                    if not is_locked and (is_keyable or is_channelbox):
                        actual_channels.append(ch)
                except:
                    continue

        if not actual_channels:
            cmds.warning(f"{child}: No valid, unlocked rotate channels to constrain.")
            continue

        rotate_mapping = {'rx': 'x', 'ry': 'y', 'rz': 'z'}

        skip_rotate = [v for k, v in rotate_mapping.items() if k not in actual_channels]

        try:
            constraint = cmds.orientConstraint(
                parent_obj,
                child,
                skip=skip_rotate,
                maintainOffset=True
            )
            print(f"? Orient-constrained {child} using: {actual_channels}")
        except Exception as e:
            cmds.warning(f"Failed to constrain {child}: {e}")


orient_constraint_selected_channels()
