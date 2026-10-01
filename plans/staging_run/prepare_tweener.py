"""Port the whole original 1.0.2 suite, not only linear interpolation."""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/tweener_v1_0_2'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/tweener_v1_0_2'
PREFIX = 'maya_toolkit.tools.tweener_v1_0_2'


def replace_function(text, name, body):
    tree = ast.parse(text)
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    lines = text.splitlines()
    indent = ' ' * node.col_offset
    decorators = '\n'.join(lines[(node.decorator_list[0].lineno - 1 if node.decorator_list else node.lineno - 1):node.lineno - 1])
    start = node.lineno - 1
    replacement = [indent + line if line else '' for line in body.splitlines()]
    lines[start:node.end_lineno] = replacement
    return '\n'.join(lines) + '\n'


def main():
    rows, methods = [], {}
    for source in sorted(UNIT.rglob('*')):
        if not source.is_file() or 'release_candidate' in source.parts or source.name.startswith('.') or '__pycache__' in source.parts:
            continue
        rel = source.relative_to(UNIT)
        archive = PKG / 'upstream' / (rel.as_posix() + ('.original' if source.suffix == '.py' else ''))
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, archive)
        rows.append({'path': rel.as_posix(), 'archive': archive.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
        if source.suffix != '.py':
            target = PKG / 'native' / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            continue
        if source.name == 'tweener-install.py':
            continue  # destructive/network installer remains complete archive only
        text = source.read_text(encoding='utf-8')
        tree = ast.parse(text)
        methods[rel.as_posix()] = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
        if source.name == 'tweener.py':
            text = re.sub(r'^import mods\.([a-z]+) as (\w+)', lambda m: 'from ' + PREFIX + '.native.mods import ' + m[1] + ' as ' + m[2], text, flags=re.M)
        else:
            text = re.sub(r'^import (?:mods\.)?([a-z]+) as (\w+)', lambda m: ('from . import ' + m[1] + ' as ' + m[2]) if m[1] in ('utils', 'animdata', 'animlayers', 'options', 'globals', 'tween') else m[0], text, flags=re.M)
        text = text.replace('.iteritems()', '.items()').replace('long(', 'int(')
        if source.name in ('ui.py', 'tweener.py', 'tool.py', 'utils.py', 'animdata.py', 'tween.py', 'keyhammer.py'):
            text = 'from ' + PREFIX + ' import runtime\n' + text
        if source.name == 'ui.py':
            text = text.replace('from PySide2.QtCore import *\nfrom PySide2.QtGui import *\nfrom PySide2.QtWidgets import *\nfrom shiboken2 import wrapInstance', "if int(cmds.about(qtVersion=True).split('.')[0]) >= 6:\n    from PySide6.QtCore import *\n    from PySide6.QtGui import *\n    from PySide6.QtWidgets import *\n    from shiboken6 import wrapInstance\nelse:\n    from PySide2.QtCore import *\n    from PySide2.QtGui import *\n    from PySide2.QtWidgets import *\n    from shiboken2 import wrapInstance")
            text = text.replace('qApp.processEvents()', 'QApplication.instance().processEvents()').replace('.exec_(', '.exec(')
            text = text.replace('self.mode_button_group.buttonClicked[int]', 'self.mode_button_group.idClicked')
            text = text.replace('slider_label_layout = QHBoxLayout(main_widget)', 'slider_label_layout = QHBoxLayout()')
            for i, fraction in enumerate(('0.0', '0.167', '0.25', '0.3333', '0.5', '0.6667', '0.75', '0.833', '1.0')):
                text = text.replace('lambda: self.fraction_clicked(' + fraction + ')', 'lambda: self.fraction_clicked(self.preset_' + str(i) + '_btn.fraction)')
            text = text.replace('value = value * 2.0 - 1.0', 'value = value * 2.0 - 1.0 if self.mode_button_group.checkedButton().mode() == options.BlendingMode.between else value')
            text = text.replace('def set_mode_button(self):\n', 'def set_mode_button(self):\n        runtime.cancel_preview()\n        self.dragging = False\n        _remove_idle(self)\n')
            shelf_tree = ast.parse(text)
            for call in ast.walk(shelf_tree):
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == 'shelfButton':
                    command = next(k.value for k in call.keywords if k.arg == 'command')
                    text = text.replace(ast.get_source_segment(text, command), repr('from maya_toolkit.tools.tweener_v1_0_2 import TweenerTool; TweenerTool().show_ui()'))
            text = text.replace('painter.begin(self)', '# QPainter(self) is already active')
            text = text.replace('painter.drawPie(self.rect, (self.angle - 90.0) * -16,\n                        (360 - self.angle) * -16)', 'painter.drawPie(self.rect, int((self.angle - 90.0) * -16),\n                        int((360 - self.angle) * -16))')
            text = text.replace('painter.drawPie(self.rect, 90.0 * 16, self.angle * -16)', 'painter.drawPie(self.rect, 90 * 16, int(self.angle * -16))')
            text = replace_function(text, 'TweenerUIScript', '''def TweenerUIScript(restore=False):
    global tweener_window
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    if tweener_window is None:
        if cmds.workspaceControl('stagingTweenerUIWindowWorkspaceControl', exists=True):
            cmds.deleteUI('stagingTweenerUIWindowWorkspaceControl')
        tweener_window = TweenerUI()
        tweener_window.setObjectName('stagingTweenerUIWindow')
    if restore:
        parent = omui.MQtUtil.getCurrentParent()
        pointer = omui.MQtUtil.findControl(tweener_window.objectName())
        if pointer and parent:
            omui.MQtUtil.addWidgetToMayaLayout(int(pointer), int(parent))
    else:
        tweener_window.show(dockable=True, retain=True, uiScript='from maya_toolkit.tools.tweener_v1_0_2.native.mods import ui; ui.TweenerUIScript(restore=True)')
    return tweener_window''')
            text = text.replace('om.MEventMessage.removeCallback(self.idle_callback)', '_remove_idle(self)')
        if source.name in ('ui.py', 'tool.py'):
            # Preview uses the full native prepare/interpolate and one cache;
            # no global Undo disabling, release publishes that cache once.
            text = re.sub(r'^\s*cmds\.undoInfo\(stateWithoutFlush=(?:False|True)\)\s*$', '', text, flags=re.M)
            text = re.sub(r'cmds\.tweener\(t=([^,]+), newCache=True, type=self.interpolation_mode.idx\)', r'runtime.begin_preview(\1, self.interpolation_mode.idx)', text)
            if source.name == 'ui.py':
                # Fraction and non-live release are committed commands.
                text = text.replace('runtime.begin_preview(value, self.interpolation_mode.idx)', 'cmds.stagingTweener(t=value, newCache=True, type=self.interpolation_mode.idx)')
                text = text.replace('else:\n            runtime.begin_preview(blend, self.interpolation_mode.idx)', 'else:\n            cmds.stagingTweener(t=blend, newCache=True, type=self.interpolation_mode.idx)')
            else:
                text = text.replace('else:\n            runtime.begin_preview(blend, self.interpolation_mode.idx)', 'else:\n            cmds.stagingTweener(t=blend, newCache=True, type=self.interpolation_mode.idx)')
                text = text.rstrip()
                if text.endswith('reset()'):
                    text = text[:-len('reset()')].rstrip() + '\n'
                text = text.replace('        pass\n    \n    def get_blend', '        runtime.cancel_preview()\n    \n    def get_blend')
                text = text.replace('        self.interpolation_mode = options.load_interpolation_mode()\n        self.overshoot = options.load_overshoot()\n        self.live_preview = options.load_live_preview()\n        \n        # disable undo', '        self.drag_position = list(self.press_position)\n        self.interpolation_mode = options.load_interpolation_mode()\n        self.overshoot = options.load_overshoot()\n        self.live_preview = options.load_live_preview()\n        \n        # disable undo')
            text = text.replace('cmds.tweener(', 'cmds.stagingTweener(').replace('cmds.keyHammer()', 'cmds.stagingKeyHammer()')
        if source.name == 'tween.py':
            text = text.replace('    if mode == options.BlendingMode.between:', '    runtime.guard_cached()\n    if mode == options.BlendingMode.between:')
            text = replace_function(text, 'tick_draw_special', '''def tick_draw_special(special=True):
    from maya_toolkit.tools.tweener_v1_0_2.tool import normalize
    runtime.tick(runtime.plan(normalize(action='tick'), gui=True), special)''')
        if source.name == 'animdata.py':
            text = text.replace("cmds.keyframe(str(curve_fn.absoluteName()), q=True, selected=True, indexValue=True)", 'runtime.selected_indices(str(curve_fn.absoluteName()))')
        if source.name == 'utils.py':
            # Wrap only selection/UI acquisition; preserve all math/algorithms.
            text = text.replace('def get_selected_objects():', 'def _original_get_selected_objects():').replace('def get_anim_curves_from_objects(nodes):', 'def _original_get_anim_curves_from_objects(nodes):').replace('def get_selected_anim_curves():', 'def _original_get_selected_anim_curves():').replace('def is_graph_editor():', 'def _original_is_graph_editor():').replace('def get_time_slider_range():', 'def _original_get_time_slider_range():')
            text = text.replace("    attr = set()\n", "    if cmds.about(batch=True):\n        return None\n    attr = set()\n")
            text = text.replace('            if dst_plug.isChild and target_plug.isChild:', '            if target_plug and dst_plug.isChild and target_plug.isChild:')
            text += '''
def get_selected_objects():
    return [] if runtime.ACTIVE is not None else _original_get_selected_objects()

def get_anim_curves_from_objects(nodes):
    return (runtime.scoped_curves(), runtime.scoped_plugs()) if runtime.ACTIVE is not None else _original_get_anim_curves_from_objects(nodes)

def get_selected_anim_curves():
    return runtime.scoped_curves() if runtime.ACTIVE is not None else _original_get_selected_anim_curves()

def is_graph_editor():
    return False if runtime.ACTIVE is not None or cmds.about(batch=True) else _original_is_graph_editor()

def get_time_slider_range():
    if runtime.ACTIVE is not None:
        return tuple(runtime.ACTIVE['time_range'])
    if cmds.about(batch=True):
        return (cmds.currentTime(query=True),) * 2
    return _original_get_time_slider_range()
'''
        if source.name == 'animlayers.py':
            text = text.replace('len(sel_layers) > 1', 'len(sel_layers or []) > 1')
        if source.name == 'keyhammer.py':
            text = text.replace('cmds.keyframe(q=True, selected=True, timeChange=True)', 'runtime.selected_times()')
            text = text.replace('min(curve_fn.numKeys, curve_fn.findClosest(max_time))', 'min(curve_fn.numKeys - 1, curve_fn.findClosest(max_time))')
            text = text.replace('range(start_index, end_index)', 'range(start_index, end_index + 1)')
            text = text.replace("mel.eval('$tmp = $gMainProgressBar')", "(None if cmds.about(batch=True) else mel.eval('$tmp = $gMainProgressBar'))").replace('cmds.progressBar(', 'runtime.progress(')
        if source.name == 'tweener.py':
            text = text.replace("cmd_name = 'tweener'", "cmd_name = 'stagingTweener'").replace("cmd_name = 'tweenerUI'", "cmd_name = 'stagingTweenerUI'").replace("cmd_name = 'keyHammer'", "cmd_name = 'stagingKeyHammer'").replace("cmd_name = 'tweenerTool'", "cmd_name = 'stagingTweenerTool'")
            text = text.replace('    def doIt(self, args):\n        # pass arguments', "    @runtime.native_command('tween')\n    def doIt(self, args):\n        # pass arguments", 1)
            text = text.replace('    def doIt(self, args):\n        self.anim_cache = oma.MAnimCurveChange()', "    @runtime.native_command('keyhammer')\n    def doIt(self, args):\n        self.anim_cache = oma.MAnimCurveChange()")
            text = text.replace('self.setResult(keyhammer.do())', 'self._operation_success = keyhammer.do()\n        self.setResult(self._operation_success)')
        if source.name == 'globals.py':
            text = text.replace("plugin_name = 'tweener.py'", "plugin_name = 'staging_tweener_plugin.py'")
        text = text.replace("'tweenerToolContext'", "'stagingTweenerToolContext'").replace("'tweenerUIWindowWorkspaceControl'", "'stagingTweenerUIWindowWorkspaceControl'")
        if source.name == 'ui.py':
            text += '''
def _remove_idle(instance):
    if instance.idle_callback is not None:
        try:
            om.MEventMessage.removeCallback(instance.idle_callback)
        except RuntimeError:
            pass
        instance.idle_callback = None

def _safe_event(function):
    def invoke(instance, *args):
        try:
            return function(instance, *args)
        except Exception as exc:
            runtime.cancel_preview()
            instance.dragging = False
            _remove_idle(instance)
            cmds.warning('Tween preview cancelled and rolled back: ' + str(exc))
        finally:
            instance.busy = False
            if function.__name__ == 'slider_released':
                _remove_idle(instance)
    return invoke

def _close_event(instance, event):
    runtime.cancel_preview()
    instance.dragging = False
    _remove_idle(instance)
    return QMainWindow.closeEvent(instance, event)

TweenerUI.slider_pressed = _safe_event(TweenerUI.slider_pressed)
TweenerUI.slider_changed = _safe_event(TweenerUI.slider_changed)
TweenerUI.slider_released = _safe_event(TweenerUI.slider_released)
TweenerUI.closeEvent = _close_event
'''
        if source.name == 'tool.py':
            text += '''
def _safe_tool_event(function):
    def invoke(instance, *args):
        try:
            return function(instance, *args)
        except Exception as exc:
            runtime.cancel_preview()
            cmds.warning('Mouse tween cancelled and rolled back: ' + str(exc))
    return invoke

Tool.press = _safe_tool_event(Tool.press)
Tool.drag = _safe_tool_event(Tool.drag)
Tool.release = _safe_tool_event(Tool.release)
'''
        text = '# Modified complete source port, 2026-10-01. Morten Andersen / original GPL LICENSE preserved.\n' + '\n'.join(line.rstrip() for line in text.splitlines()).rstrip() + '\n'
        text = text.rstrip() + '\n'
        ast.parse(text)
        target = PKG / 'native' / ('staging_tweener_plugin.py' if source.name == 'tweener.py' else rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8', newline='\n')
    (PKG / 'native/__init__.py').write_text('', encoding='utf-8')
    (PKG / 'catalog.json').write_text(json.dumps({'files': rows, 'original_declarations': methods, 'license': 'Complete original GNU GPL v3 LICENSE and Morten Andersen attribution preserved'}, indent=2) + '\n', encoding='utf-8', newline='\n')
    (UNIT / '.gitattributes').write_text('*.py -text\n', encoding='utf-8')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'tweener_v1_0_2').replace('RootMotionBakeTool', 'TweenerTool')
    (RC / 'launch_candidate.py').write_text(launch, encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'tweener_v1_0_2', 'registration': {'module': 'tweener_v1_0_2', 'class_name': 'TweenerTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [x['path'] for x in rows], 'dependencies': ['Maya API2/cmds, Qt5/6, complete private Python plugin; no download/installation/autoload required'], 'acceptance_required': True, 'change_summary': 'Complete original 1.0.2 suite ported with all five interpolation algorithms, animation-layer choice, original MPxCommand/MAnimCurveChange Undo, full dockable UI/mouse preview/keyhammer and resources/license. Explicit scoped API/read-only preflight, private namespaces/commands, Qt6/Py3 ports, non-destructive startup; original installer archive only.', 'verification_limitations': ['Full GUI/idle live preview/docking/mouse tool and production animation-layer rigs not_run', 'Initial private plugin registration and GUI preference writes are outside Undo', 'Endpoint-outside-keyed-range insertion rejected; keyhammer inclusive range endpoint repaired', 'Original network/delete/reinstall/autoload/shelf installer remains archive-only; direct framework use is self-contained', 'Original tick color changes may not be Undoable in all Maya versions']}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'files': len(rows), 'declarations': sum(len(v) for v in methods.values())}))


if __name__ == '__main__':
    main()
