import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/brs_loc_transfer'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/brs_loc_transfer'

OPTIONS = {'AnnoChk': 'annotation', 'BakeChk': 'bake_all', 'ConsChk': 'constrain', 'TimelineChk': 'in_timeline', 'translateChk': 'translate', 'rotateChk': 'rotate'}


class Business(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'cmds':
            if node.func.attr == 'checkBox':
                return ast.parse("_options[%r]" % OPTIONS[node.args[0].id], mode='eval').body if any(k.arg in ('q', 'query') for k in node.keywords) else ast.Constant(None)
            if node.func.attr in ('progressBar', 'inViewMessage'):
                return ast.Call(func=ast.Name(id='_feedback', ctx=ast.Load()), args=[], keywords=[])
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == 'mel' and node.func.attr == 'eval':
            return ast.Constant(None)
        return node


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    entry = UNIT / 'BRSLocTransfer.py'
    original = entry.read_text(encoding='utf-8-sig')
    tree = ast.parse(original)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    (PACKAGE / 'upstream').mkdir(exist_ok=True)
    shutil.copyfile(entry, PACKAGE / 'upstream/BRSLocTransfer.py')
    for path, text in [(UNIT / '.gitattributes', '/BRSLocTransfer.py -text\n'), (RC / '.gitattributes', '* -text\n'), (PACKAGE / 'upstream/.gitattributes', '* -text\n')]:
        path.write_text(text, encoding='utf-8', newline='\n')
    # Original helper algorithms and full two transfer loops remain traceable.
    unchanged = ['snap', 'snapPoint', 'getAllKeyframe', 'bakeKey', 'keepKeyframe', 'setKeyBreakdown']
    business = []
    for name in unchanged + ['objectToLocatorSnap', 'locatorToObjectSnap', 'applyRedirectGuide']:
        node = Business().visit(funcs[name])
        text = ast.unparse(node)
        text = text.replace('breakdownList = cmds.keyframe(objName, q=True, breakdown=True)', 'breakdownList = cmds.keyframe(objName, q=True, breakdown=True) or []')
        text = text.replace('breakdownList = cmds.keyframe(SnapLoc, q=True, breakdown=True)', 'breakdownList = cmds.keyframe(SnapLoc, q=True, breakdown=True) or []')
        text = text.replace('SnapLoc = objName + locSuffix', 'SnapLoc = _scene.locator_for(objName, required=True)')
        text = text.replace('cmds.delete(SnapLoc)', '_scene.delete_locator(SnapLoc)')
        text = text.replace('cmds.delete(BRSAnimLocGrp)', '_scene.delete_group_if_empty()')
        text = text.replace('cmds.delete(redirectGuide)', '_scene.delete_guide()')
        text = text.replace('cmds.parent(SnapLoc, BRSAnimLocGrp)', 'SnapLoc = cmds.parent(SnapLoc, BRSAnimLocGrp)[0]')
        if name == 'applyRedirectGuide':
            text = text.replace('selection = cmds.listRelatives(BRSAnimLocGrp, children=True)', 'selection = _scene.locators()')
        node = ast.parse(text).body[0]
        node.body.insert(0, ast.Expr(ast.Call(func=ast.Name(id='_guard', ctx=ast.Load()), args=[], keywords=[])))
        business.append(node)
    replacements = ast.parse('''
def resetViewport(*_):
    _guard()
    return None
def parentConstraint(object, target, translate=True, rotate=True):
    _guard()
    return _scene.constraints(object, target, translate, rotate)
def createBRSAnimLocGrp(snapObj):
    _guard()
    return _scene.ensure_group(snapObj)
def createRedirectGuide(*_):
    _guard()
    return _scene.create_guide()
def getMimicLocator(objectName, locName=None):
    _guard()
    return [_scene.make_locator(objectName, _options['annotation'])]
def deleteConstraint(objectName):
    _guard()
    return _scene.delete_constraints(objectName)
def statTextUI(text):
    return _feedback(text)
def BRSLocTransferUI(*_):
    return build_ui()
''').body
    header = ast.parse('''
import maya.cmds as cmds
from . import scene as _scene
from .runtime import require_active as _guard
from .ui import feedback as _feedback
_options = {}
locSuffix = '_mtbBRSSnapLoc'
BRSAnimLocGrp = 'mtbBRSAnimLoc_Grp'
redirectGuide = 'mtbBRSRedirectGuide'
''').body
    # All original UI layout calls become an explicit callable, no remote exec/cycleCheck reset.
    boundary = next(i for i, node in enumerate(tree.body) if isinstance(node, ast.If) and 'cmds.window' in ast.unparse(node.test))
    ui_nodes = tree.body[boundary:next(i for i, node in enumerate(tree.body) if isinstance(node, ast.FunctionDef) and node.name == 'BRSLocTransferUI')]
    constants = [node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ('version', 'winID', 'winWidth', 'colorSet') for t in node.targets)]
    for node in constants:
        if any(isinstance(t, ast.Name) and t.id == 'winID' for t in node.targets):
            node.value = ast.Constant('mtbBRSLOCTRANSFER')
    ui_text = '\n'.join(ast.unparse(n) for n in ui_nodes)
    ui_text = ui_text.replace('lambda arg: objectToLocatorSnap(toGroup=True, forceConstraint=False)', "lambda *_: _bridge.dispatch('create')")
    for old, action in [('locatorToObjectSnap', 'apply'), ('createRedirectGuide', 'create_guide'), ('applyRedirectGuide', 'redirect')]:
        ui_text = ui_text.replace('c=' + old, "c=lambda *_: _bridge.dispatch('" + action + "')")
    function = 'def build_ui():\n    global statText, ConsChk, AnnoChk, BakeChk, TimelineChk, translateChk, rotateChk\n    from . import ui as _bridge\n'
    function += '\n'.join('    ' + line for line in ui_text.splitlines()) + '\n    cmds.showWindow(winID)\n    cmds.window(winID, e=True, h=100, w=100)\n    return winID\n'
    output = ast.Module(body=header + constants + business + replacements + ast.parse(function).body, type_ignores=[])
    ast.fix_missing_locations(output)
    adapted = ast.unparse(output) + '\n'
    (PACKAGE / 'legacy.py').write_text(adapted, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'brs_loc_transfer_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True), fromfile='upstream/BRSLocTransfer.py', tofile='legacy.py')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'brs_loc_transfer', 'original_functions': list(funcs), 'raw_files': [{'path': 'upstream/BRSLocTransfer.py', 'sha256': hashlib.sha256(entry.read_bytes()).hexdigest()}], 'algorithm_helpers': unchanged, 'full_transfer_loops': ['objectToLocatorSnap', 'locatorToObjectSnap', 'applyRedirectGuide'], 'source_license': 'Author Burasate Uttha / DEX3D; no license file supplied, private preparation', 'changes': ['No import-time GUI', 'Remove downloaded exec and cycleCheck/global viewport resets', 'Explicit option values, no business widget/progress dependencies', 'Owned locator/group/guide/constraint UUID persistence', 'None breakdowns fixed, missing locator errors explicit', 'Native four buttons through standard API']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    descriptor = {'tool_id': 'brs_loc_transfer', 'registration': {'module': 'brs_loc_transfer', 'class_name': 'LocatorTransferTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': ['upstream/BRSLocTransfer.py', 'catalog.json'], 'dependencies': ['Maya Python3/cmds constraints/bakeResults/filterCurve', 'Actual GUI for native layout', 'Existing framework/core Undo'], 'source': '../BRSLocTransfer.py', 'change_summary': 'Complete original locator transfer/redirection bake algorithms and native layout, owned UUID helpers and strict channel preflight, no downloaded code or import-time scene writes.', 'verification_limitations': ['GUI and production rig/layers pending', 'Original guide flow moves group while isolated test preserves locator world trajectory; intended redirection result unverified', 'Original round/bake/snapKey affect key timing and key density', 'Generated blend nodes may remain carrying old curves', 'Only standard API permitted; raw original unsafe entry archived'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'original_functions': len(funcs), 'candidate_functions': len([n for n in output.body if isinstance(n, ast.FunctionDef)])}))


if __name__ == '__main__':
    main()
