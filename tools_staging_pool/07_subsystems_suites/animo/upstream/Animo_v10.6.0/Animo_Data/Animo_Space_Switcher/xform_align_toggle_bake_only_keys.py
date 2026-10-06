import maya.cmds as cmds

if cmds.optionVar(exists='XformAlignUI_bakeKeys'):
    _current = bool(cmds.optionVar(q='XformAlignUI_bakeKeys'))
else:
    _current = True

cmds.optionVar(iv=('XformAlignUI_bakeKeys', 0 if _current else 1))
