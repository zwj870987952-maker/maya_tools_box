"""Preserve upstream and extract the original UI/algorithms without running Maya."""
import ast
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/anim_layer_bookmark_trimmer'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/anim_layer_bookmark_trimmer'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    upstream = PACKAGE / 'upstream'
    upstream.mkdir(exist_ok=True)
    for name in ('anim_layer_bookmark_trimmer.py', 'README.md'):
        shutil.copyfile(UNIT / name, upstream / name)
    source = (UNIT / 'anim_layer_bookmark_trimmer.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    ui = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    lines = source.splitlines(keepends=True)
    operations = ''.join(lines[:ui.lineno - 1])
    # Plugin loading is an explicit UI preparation action; queries remain read-only.
    first = operations.index('def ensure_bookmark_plugin():')
    last = operations.index('def get_scene_anim_layers():')
    operations = operations[:first] + '''def ensure_bookmark_plugin():
    """Queries must never load plugins or change the scene."""
    if not cmds.pluginInfo("timeSliderBookmark", query=True, loaded=True):
        raise RuntimeError("Load timeSliderBookmark explicitly before using this tool")
    return True


''' + operations[last:]
    # Missing boundary keys in dry-run must be evaluated, not indexed as existing keys.
    operations = operations.replace('inner_count = count - 2', 'inner_count = sum(st + 0.001 < t < sp - 0.001 for t in k_times)')
    operations = operations.replace('cmds.keyframe(c, time=(st, st), query=True, valueChange=True)[0]', 'cmds.keyframe(c, time=(st, st), query=True, eval=True)[0]')
    operations = operations.replace('cmds.keyframe(c, time=(sp, sp), query=True, valueChange=True)[0]', 'cmds.keyframe(c, time=(sp, sp), query=True, eval=True)[0]')
    operations = operations.replace("        cb = mel.eval('$tmpVar=$gChannelBoxName')", "        if cmds.about(batch=True):\n            return []\n        cb = mel.eval('$tmpVar=$gChannelBoxName')")
    operations = operations.replace("slider = mel.eval('$tmpVar=$gPlayBackSlider')", "slider = None if cmds.about(batch=True) else mel.eval('$tmpVar=$gPlayBackSlider')")
    # Curve lookup is replaced below by a normalized exact-plug resolver.
    start = operations.index('def get_layer_curves_for_objects(')
    end = operations.index('def get_bookmark_details():')
    replacement = (Path(__file__).parent / 'bookmark_curve_resolver.txt').read_text(encoding='utf-8')
    operations = operations[:start] + replacement + '\n\n' + operations[end:]
    # Preserve catches that are intentionally best effort, but boundary insertion must fail loudly.
    start = operations.index('def _ensure_boundary_keys_on_curve(')
    end = operations.index('def optimize_layer_curves_by_bookmarks(')
    operations = operations[:start] + '''def _ensure_boundary_keys_on_curve(curve, start_time, stop_time):
    for time in (start_time, stop_time):
        if not cmds.keyframe(curve, time=(time, time), query=True, timeChange=True):
            cmds.setKeyframe(curve, time=(time, time), insert=True)


''' + operations[end:]
    operations = operations.replace('''                try:
                    cmds.setKeyframe(curves, time=(kf, kf), insert=True)
                except Exception:
                    pass''', '''                cmds.setKeyframe(curves, time=(kf, kf), insert=True)''')
    (PACKAGE / 'operations.py').write_text(operations, encoding='utf-8')
    native_ui = 'import sys\nimport maya.cmds as cmds\nfrom .operations import *\n\n' + ''.join(lines[ui.lineno-1:ui.end_lineno])
    native_ui = native_ui.replace('• 🎛️ 曲线优化：端点绝对锁定，提供平滑去噪、冗余简化、多帧S曲线缓动与端点缓入缓出。', '• 🎛️ 曲线优化：保留端点值；切线可能影响范围外插值。支持平滑、简化与缓动。')
    native_ui = native_ui.replace('🎛️ 书签区间动画曲线优化 (端点姿态绝对锁定)', '🎛️ 书签区间动画曲线优化 (保留本层曲线端点值)')
    (PACKAGE / 'native_ui.py').write_text(native_ui, encoding='utf-8')
    payload = sorted([p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests')
                      for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts])
    description = {
        'tool_id': 'anim_layer_bookmark_trimmer',
        'registration': {'module': 'anim_layer_bookmark_trimmer', 'class_name': 'AnimLayerBookmarkTrimmerTool'},
        'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in payload],
        'resources': ['upstream/anim_layer_bookmark_trimmer.py', 'upstream/README.md'],
        'dependencies': ['maya.cmds/maya.mel', 'timeSliderBookmark plugin explicitly loaded', 'existing maya_toolkit framework/core', 'Python 3'],
        'source': '../anim_layer_bookmark_trimmer.py',
        'change_summary': 'Original six algorithms/native UI retained; read-only plugin preflight, exact layer/continuous-channel lookup, missing-boundary preview fix, parameter/scene guards, complete archive and promotion package.',
        'verification_limitations': ['Actual Maya GUI and timeline/channel-box interaction pending', 'Other Maya versions/Python 2 unverified', 'Optimization may change interpolation outside bookmarks; overlapping optimization bookmarks rejected'],
        'acceptance_required': True,
    }
    (RC / 'promotion.json').write_text(json.dumps(description, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Original source/README preserved; runtime and native UI extracted')


if __name__ == '__main__':
    main()
