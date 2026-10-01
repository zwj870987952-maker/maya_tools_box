"""Archive complete suite and extract complete headless business classes, no installer."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/retime_tools'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/retime_tools'
BUSINESS = {'RetimeStates', 'CoreFunctions', 'ShuffleKeys', 'RetimeLookup', 'Color'}


def main():
    PKG.mkdir(parents=True, exist_ok=True)
    raw_files = [p for p in UNIT.rglob('*') if p.is_file() and 'release_candidate' not in p.parts and '__pycache__' not in p.parts and p.name != '.gitattributes']
    upstream = PKG / 'upstream'
    catalog = {'raw_files': [], 'classes': {}, 'license': 'No independent distribution license supplied; retain author eblabs and Chinese UI credit. Local personal preparation only.', 'missing_optional_dependencies': ['UXFramework.scripts.LicenseManager', 'QTS/LicenseManager_311, _310, _39, _37, _27'], 'license_behavior': 'Original license modules and trial settings unchanged. Main RetimeTools.py does not import these optional modules. No fake licensing backend.', 'empty_modules': ['RetimeTools/Plugin.py', 'RetimeTools/__init__.py']}
    for p in raw_files:
        rel = p.relative_to(UNIT).as_posix()
        target = upstream / (rel + '.original' if p.suffix == '.py' else rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
        catalog['raw_files'].append({'source': rel, 'path': target.relative_to(upstream).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size})
    source = (UNIT / 'RetimeTools/RetimeTools.py').read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    for n in tree.body:
        if isinstance(n, ast.ClassDef):
            catalog['classes'][n.name] = [m.name for m in n.body if isinstance(m, ast.FunctionDef)]
    # Preserve every original definition in native.py; API uses the extracted full classes.
    native = source.replace('import maya.cmds as cmds', 'from .runtime import ui_cmds as cmds').replace('from QTS import Qt', 'from . import qt_compat as Qt').replace('long(mayaMainWindowPtr)', 'int(mayaMainWindowPtr)')
    native = native.replace('self.setObjectName(windowTitle)', "self.setObjectName('mtkRetimeCandidateWindow')")
    # Framework manages exception-safe chunks; old UI manually opened unbalanced chunks.
    native = re.sub(r'^\s*cmds\.undoInfo\([^\n]*\)\s*$', '', native, flags=re.M)
    native += '\nfrom .ui_bridge import install\ninstall(globals())\n'
    native = '\n'.join(line.rstrip() for line in native.splitlines()) + '\n'
    (PKG/'native.py').write_text(native, encoding='utf-8', newline='\n')
    body = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in BUSINESS or isinstance(n, ast.FunctionDef) and n.name == 'iteritems']
    prefix = 'from .runtime import engine_cmds as cmds\nimport decimal, colorsys, traceback, copy, math\nfrom collections import OrderedDict\nfrom operator import itemgetter\n'
    engine = prefix + ast.unparse(ast.Module(body=body, type_ignores=[])) + '\n'
    engine = re.sub(r'^\s*cmds\.undoInfo\([^\n]*\)\s*$', '', engine, flags=re.M)
    engine = engine.replace('pairs[min_index][1], pairs[min_index][1], ratio', 'pairs[min_index][1], pairs[max_index][1], ratio')
    engine = engine.replace('if not rt:', 'if rt is None:')
    engine = engine.replace('range(start_frame, end_frame)', 'range(start_frame, end_frame + 1)')
    engine = engine.replace('int(float(t) + 0.5)', 'int(math.floor(float(t) + 0.5))')
    engine = engine.replace('cmds.listConnections(anim_curves, plugs=True, source=False, destination=True)', "(cmds.listConnections(c + '.output', plugs=True, source=False, destination=True) or [])")
    engine = engine.replace('cmds.setInfinity(attribute=curve,', 'cmds.setInfinity(curve,')
    engine = engine.replace('preInfinite=pre_infinity)', 'preInfinite=pre_infinity[0])').replace('postInfinite=post_infinity)', 'postInfinite=post_infinity[0])')
    engine = engine.replace('pre_infinity = cmds.setInfinity(curve, query=True, preInfinite=True)', "pre_infinity = cmds.getAttr(curve + '.preInfinity')")
    engine = engine.replace('post_infinity = cmds.setInfinity(curve, query=True, postInfinite=True)', "post_infinity = cmds.getAttr(curve + '.postInfinity')")
    engine = engine.replace('cmds.setInfinity(curve, preInfinite=pre_infinity[0])', "cmds.setAttr(curve + '.preInfinity', pre_infinity)")
    engine = engine.replace('cmds.setInfinity(curve, postInfinite=post_infinity[0])', "cmds.setAttr(curve + '.postInfinity', post_infinity)")
    engine = engine.replace("print(1969, Exception, e)\n                print('Skipping:', curve)", 'raise RuntimeError("Shuffle failed for " + curve) from e')
    engine = engine.replace('option=\'insert\'', "option='merge'")
    # Return newly created controller for API rather than the original implicit None.
    engine = engine.replace('cls.set_retime_controller_state(retime_controller, RetimeStates.Reset)\n', 'cls.set_retime_controller_state(retime_controller, RetimeStates.Reset)\n        return retime_controller\n', 1)
    (PKG/'engine.py').write_text(engine, encoding='utf-8', newline='\n')
    catalog['native_sha256'] = hashlib.sha256(native.encode()).hexdigest()
    catalog['engine_sha256'] = hashlib.sha256(engine.encode()).hexdigest()
    catalog['mel_procedures'] = re.findall(r'global\s+proc\s+(?:\w+(?:\[\])?\s+)?(\w+)\s*\(', (UNIT/'RetimeTools/ebLabs_timeWarp.mel').read_text(encoding='utf-8-sig'))
    mel_source = (UNIT/'RetimeTools/ebLabs_timeWarp.mel').read_text(encoding='utf-8-sig').replace('ebLabs_', 'mtkRTlegacy_').replace('eb_labs_', 'mtkRTlegacy_')
    mel_source = mel_source.replace('import animscratch.mtkRTlegacy_retimeTools as mtkRTlegacy_retimeTools \\nmtkRTlegacy_retimeTools.CoreFunctions.addCurvesToTimewarp()', 'from maya_toolkit.tools.retime_tools.legacy_mel import connect_from_ui; connect_from_ui()')
    # Preserve complete legacy suite under private procedure/UI/global variable names.
    mel_source = '\n'.join(re.sub(r'^[ \t]+', lambda m:m.group(0).expandtabs(4), line.rstrip()) for line in mel_source.splitlines())+'\n'
    assets = PKG/'assets'
    assets.mkdir(exist_ok=True)
    (assets/'legacy_timewarp.mel').write_text(mel_source, encoding='utf-8', newline='\n')
    catalog['legacy_mel_sha256'] = hashlib.sha256(mel_source.encode()).hexdigest()
    (PKG/'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (UNIT/'.gitattributes').write_text('RetimeTools/** -text\n*.7z -text\n*.url -text\n', encoding='utf-8')
    (RC/'.gitattributes').write_text('* -text\n', encoding='utf-8')
    docs = RC/'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs/'retime_tools_changes.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True), native.splitlines(True), fromfile='upstream/RetimeTools/RetimeTools.py.original', tofile='native.py')), encoding='utf-8')
    launcher = (ROOT/'tools_staging_pool/01_animation/pose_transfer_remote/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('pose_transfer_remote', 'retime_tools').replace('PoseTransferRemoteTool', 'RetimeToolsTool')
    (RC/'launch_candidate.py').write_text(launcher, encoding='utf-8')
    payload = [p for folder in (RC/'maya_toolkit', RC/'docs', RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    data = {'tool_id':'retime_tools', 'registration':{'module':'retime_tools','class_name':'RetimeToolsTool'}, 'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources':[r['path'] for r in catalog['raw_files']], 'dependencies':['Maya cmds/mel', 'PySide6 or PySide2 with matching shiboken for original Qt UI', 'Original optional QTS license/version modules unavailable; never faked'], 'acceptance_required':True, 'change_summary':'Full original Python suite/Qt widgets and headless CoreFunctions/ShuffleKeys/RetimeLookup, complete MEL and vendor/resources archives; checked API/UI, explicit file IO, and full original method catalog.', 'verification_limitations':['GUI and legacy MEL suite require human Maya acceptance', 'Original disabled import/export menu stubs are identified; explicit API supplies curve IO', 'No independent license supplied; local only']}
    (RC/'promotion.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'raw_files':len(raw_files),'classes':len(catalog['classes']),'methods':sum(map(len,catalog['classes'].values())),'mel_procs':len(catalog['mel_procedures'])}))


if __name__ == '__main__':
    main()
