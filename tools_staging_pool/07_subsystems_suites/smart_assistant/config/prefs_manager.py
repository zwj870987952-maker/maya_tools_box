import maya.cmds as cmds
import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

PREFS_KEYS = [
    'workingUnitLinear',
    'workingUnitTime',
    'gridSize',
    'gridSpacing',
    'gridDivisions',
    # 可根据需要添加更多首选项key
]

def export_prefs():
    """
    导出当前Maya首选项到config.json
    """
    prefs = {}
    for key in PREFS_KEYS:
        try:
            prefs[key] = cmds.optionVar(q=key)
        except Exception:
            pass
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)
    cmds.confirmDialog(title='提示', message='首选项已导出', button=['OK'])

def apply_prefs():
    """
    应用config.json中的首选项到当前Maya
    """
    if not os.path.exists(CONFIG_PATH):
        return
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        prefs = json.load(f)
    for key, value in prefs.items():
        try:
            cmds.optionVar(sv=(key, value))
        except Exception:
            pass 