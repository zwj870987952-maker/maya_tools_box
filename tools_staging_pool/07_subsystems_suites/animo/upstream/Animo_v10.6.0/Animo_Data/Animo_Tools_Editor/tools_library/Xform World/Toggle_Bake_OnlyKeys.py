import maya.cmds as cmds

BAKE_KEYS_OPTION_VAR = "XformAlignUI_bakeKeys"


def toggle_bake_only_keys():
    if cmds.optionVar(exists=BAKE_KEYS_OPTION_VAR):
        current = bool(cmds.optionVar(q=BAKE_KEYS_OPTION_VAR))
    else:
        current = True

    new_value = not current
    cmds.optionVar(iv=(BAKE_KEYS_OPTION_VAR, 1 if new_value else 0))

    if new_value:
        message = '<span style="color:#4ca6e6;">Xform Align: Only Keys</span>'
    else:
        message = '<span style="color:#4ca6e6;">Xform Align: Bake</span>'

    cmds.inViewMessage(
        amg=message,
        pos='botCenter',
        fade=True
    )


toggle_bake_only_keys()