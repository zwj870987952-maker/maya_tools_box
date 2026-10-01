"""Retain all seven prototype functions and the original result window."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT/'tools_staging_pool/02_rigging_hierarchy/hierarchy_analyzer'
RC = UNIT/'release_candidate'
PKG = RC/'maya_toolkit/tools/hierarchy_analyzer'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(x.rstrip() for x in text.rstrip().splitlines())+'\n', encoding='utf-8', newline='\n')


def main():
    source = UNIT/'maya_hierarchy_analysis.py'
    target = PKG/'vendor/maya_hierarchy_analysis.py.original'
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    text = source.read_text(encoding='utf-8-sig')
    tree = ast.parse(text)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    lines = text.splitlines(keepends=True)
    complete = 'import maya.cmds as cmds\n\n'+'\n\n'.join(''.join(lines[n.lineno-1:n.end_lineno]) for n in functions)
    write(PKG/'original_logic.py', complete)
    ui = ''.join(lines[functions[-1].lineno-1:functions[-1].end_lineno])
    ui = ui.replace('influence_layers = analyze_influence_hierarchy(selected_nodes)', 'analysis = HierarchyAnalyzerTool().run(objects=selected_nodes)\n    if not analysis.success:\n        cmds.warning(analysis.message)\n        return\n    influence_layers = analysis.data["layers"]')
    ui = ui.replace('is_valid = verify_influence_hierarchy(influence_layers)', 'is_valid = analysis.data["valid"]')
    ui = ui.replace("short_name = node.split('|')[-1]", 'short_name = node')
    ui = ui.replace('    # 创建结果窗口', '    if analysis.data["unresolved"]:\n        result += "\\n未解决环或被环阻塞的节点：\\n" + "\\n".join(analysis.data["unresolved"])\n    for warning in analysis.data["warnings"]:\n        result += "\\n" + warning\n    # 创建结果窗口')
    ui = ui.replace('command=("cmds.deleteUI(\\\"influenceHierarchyWindow\\\")")', 'command=lambda *unused: cmds.deleteUI("influenceHierarchyWindow")')
    ui = ui.replace('验证通过: 所有层级关系正确。', '结构图分层校验通过；不代表 Maya 全部 DG 求值依赖。')
    write(PKG/'native_ui.py', 'import maya.cmds as cmds\nfrom .tool import HierarchyAnalyzerTool\n\n'+ui)
    catalog = {'files': [{'path': source.name, 'archive': target.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'bytes': source.stat().st_size}], 'functions': [n.name for n in functions], 'original_modified': False}
    write(PKG/'catalog.json', json.dumps(catalog, ensure_ascii=False, indent=2))
    write(UNIT/'.gitattributes', '*.py -text')
    write(RC/'.gitattributes', '* -text')
    launch = (ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'hierarchy_analyzer').replace('RootMotionBakeTool', 'HierarchyAnalyzerTool')
    write(RC/'launch_candidate.py', launch+'\n\ndef show_ui():\n    return load_tool().show_ui()\n')
    payload = [p for folder in (RC/'maya_toolkit', RC/'docs', RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'hierarchy_analyzer', 'registration': {'module': 'hierarchy_analyzer', 'class_name': 'HierarchyAnalyzerTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [source.name], 'dependencies': ['Maya cmds for read-only scene DAG and native constraint queries; Maya native UI only on explicit show_ui'], 'acceptance_required': True, 'change_summary': 'Complete seven-function prototype and result UI retained; full long DAG/UUID analysis, correct driver-to-child edges and geometry target support, preserved parent relationships, indirect paths through unselected nodes, stable true topological layers and explicit cycle/blocked diagnostics, read-only API/Schema/result and callable close callback.', 'verification_limitations': ['Real Maya result GUI and production rigs/multiple versions not_run', 'This is a structural DAG/native-constraint potential-influence graph, not the full DG/evaluation graph; offsets, zero weights, pairBlend, dynamics, expressions, custom matrix/deformer relationships do not prove runtime influence', 'Scene DAG instances and unknown native constraint target mappings require explicit review; ambiguous structures are rejected or warned instead of silently skipped', 'Large scene/edge budgets are bounded and exceedance fails read-only; no partial ordering claimed']}
    write(RC/'promotion.json', json.dumps(promotion, ensure_ascii=False, indent=2))
    print(json.dumps({'functions': catalog['functions']}))


if __name__ == '__main__':
    main()
