"""Create a complete private Python 3 port, retaining every upstream byte."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/01_animation/spring_magic_v3_5a'
RAW=UNIT/'springmagic'
RC=UNIT/'release_candidate'
PKG=RC/'maya_toolkit/tools/spring_magic_v3_5a'


def put(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8',newline='\n')


def replace_body(text,name,body):
    tree=ast.parse(text)
    node=next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    lines=text.splitlines(True)
    indent=' '*(node.col_offset+4)
    lines[node.body[0].lineno-1:node.end_lineno]=[indent+s+'\n' for s in body.splitlines()]
    return ''.join(lines)


def main():
    native=PKG/'native'
    native.mkdir(parents=True,exist_ok=True)
    rows=[]
    for src in sorted(RAW.rglob('*')):
        if not src.is_file():
            continue
        rel=src.relative_to(RAW)
        archive=PKG/'upstream'/rel
        if src.suffix=='.py':
            archive=archive.with_suffix('.py.original')
        archive.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,archive)
        rows.append({'path':rel.as_posix(),'archive':archive.relative_to(PKG).as_posix(),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
        if src.suffix!='.py':
            dst=native/rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dst)
    definitions={}
    for filename in ('core.py','springMath.py','utility.py','ui.py','decorators.py'):
        source=(RAW/filename).read_text(encoding='utf-8-sig')
        definitions[filename]=[n.name for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef)]
        text=source.replace('import decorators','from . import decorators').replace('import springMath','from . import springMath').replace('from utility import *','from .utility import *').replace('import springmagic.core as core','from . import core').replace('import urllib2','import urllib.request as urllib2').replace('progression_generator.next()','next(progression_generator)')
        if filename=='core.py':
            text=replace_body(text,'__del__','pass  # Deterministic cleanup belongs to the candidate operation scope.')
            text=text.replace('self._instances[id(self)] = self','self._instances[id(self)] = self\n        _active_data.append(self)')
            text=text.replace("pm.delete(pm.ls('*' + kNullSuffix + '*', recursive=True))","pass  # Never delete scene-wide wildcard matches.")
            text=text.replace("springMagic.collision_planes_list = [get_node('*' + kCollisionPlaneSuffix + '*')]","from .. import runtime\n        springMagic.collision_planes_list = [runtime.collision_plane()]")
            text=text.replace("    collision_plane = get_node('*' + kCollisionPlaneSuffix + '*')\n\n    if collision_plane:\n        pm.delete(collision_plane)\n\n    collision_plane = pm.polyPlane", "    # Owned previous plane is removed by the adapter using its UUID.\n    collision_plane = pm.polyPlane")
            text=text.replace("if pm.ls(kWindObjectName):\n        springMagic.wind = pm.ls(kWindObjectName)[0]","from .. import runtime\n    springMagic.wind = runtime.wind_source()")
            text=replace_body(text,'getCapsule',"from .. import runtime\nreturn runtime.capsules(getAll)")
            text=replace_body(text,'clearBind',"from .. import runtime\nreturn runtime.clear_bind(startFrame, endFrame)")
            text+='\n_active_data = []\n'
        elif filename=='decorators.py':
            text=text.replace("self.mMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')","self.mMainProgressBar = None\n        self.previous_cursor = False")
            text=text.replace('cmds.progressBar(self.mMainProgressBar, edit=True, step=inValue)','if self.mMainProgressBar:\n            cmds.progressBar(self.mMainProgressBar, edit=True, step=inValue)')
            text=text.replace('cmds.progressBar(self.mMainProgressBar, edit=True, progress=inValue)','if self.mMainProgressBar:\n            cmds.progressBar(self.mMainProgressBar, edit=True, progress=int(inValue))')
            text=text.replace('return cmds.progressBar(self.mMainProgressBar, query=True, isCancelled=True)','return self.cancelled or bool(self.mMainProgressBar and cmds.progressBar(self.mMainProgressBar, query=True, isCancelled=True))')
            text=text.replace('self.mInterruptable = interruptable','self.mInterruptable = interruptable\n        self.cancelled = False')
            text=replace_body(text,'start',"self.previous_cursor = cmds.waitCursor(query=True, state=True) if not cmds.about(batch=True) else False\nif cmds.about(batch=True):\n    return\nself.mMainProgressBar = mel.eval('$tmp = $gMainProgressBar')\ncmds.waitCursor(state=True)\ncmds.progressBar(self.mMainProgressBar, edit=True, beginProgress=True, isInterruptable=self.mInterruptable, status=self.mStatus, minValue=self.mStartValue, maxValue=self.mEndValue)\ncmds.refresh()")
            text=text.replace('self.previous_cursor = cmds.waitCursor(query=True, state=True) if not cmds.about(batch=True) else False','self.cancelled = False\n        self.previous_cursor = cmds.waitCursor(query=True, state=True) if not cmds.about(batch=True) else False')
            text=replace_body(text,'end',"try:\n    self.cancelled = self.isInterrupted()\n    if self.mMainProgressBar:\n        cmds.progressBar(self.mMainProgressBar, edit=True, endProgress=True)\nfinally:\n    if not cmds.about(batch=True):\n        cmds.waitCursor(state=self.previous_cursor)\n    self.mMainProgressBar = None")
            text=replace_body(text,'wrapped_f',"try:\n    self.start()\n    return inFunction(*args, **kwargs)\nfinally:\n    self.end()")
        elif filename=='ui.py':
            text=text.replace('self.ui = pm.loadUI(f=ui_file)','from ..ui_support import load_ui\n        self.ui = load_ui(getattr(self, "language", ""))')
            text=text.replace('self.checkUpdate()','pm.text(self.main_processLabel, edit=True, label="Ready — Spring Magic 3.5a candidate")')
            text=text.replace('unicode(sWord, "utf8", errors="ignore")','str(sWord)')
            text=text.replace("self.floor_lineEdit = pm.textField(self.uiObjects['springFloor_lineEdit'], edit=True, changeCommand=self.twistChangeCmd)","self.floor_lineEdit = pm.textField(self.uiObjects['springFloor_lineEdit'], edit=True, enable=False)\n        self.floor_checkBox.setEnable(False)\n        self.subs_lineEdit.setEnable(False)")
            text=replace_body(text,'applyLanguage',"mapping={1:'chn',2:'eng',3:'jpn'}\nif lanId in mapping:\n    self.language=mapping[lanId]\n    self.init()\n    self.show()")
            text=text.replace('self.applyLanguage(lanDict[mayaLan])','self.applyLanguage(lanDict.get(mayaLan, 2))')
            text=replace_body(text,'checkUpdate',"# The legacy endpoint is obsolete; opening the documented page is explicit.\nreturn self.updatePageCmd()")
            text=replace_body(text,'goShelfCmd',"from ..ui_support import add_shelf_button\nreturn add_shelf_button()")
            text=replace_body(text,'applyCmd',"from ..ui_support import compute\nreturn compute(self)")
            action_map={'pasteCmd':'paste_pose','copyCmd':'copy_pose','setCmd':'bind_pose','straightCmd':'straight','addWindCmd':'add_wind','addBodyCmd':'add_capsule','createColPlaneCmd':'add_plane','removeBodyCmd':'remove_capsule','clearBodyCmd':'clear_collision','bindControlsCmd':'bind_controls','clearBindCmd':'bake_controls'}
            for method,action in action_map.items():
                text=replace_body(text,method,"from ..ui_support import dispatch\nreturn dispatch(self, %r)" % action)
        put(native/filename,text)
    put(native/'__init__.py',"\"\"\"Complete Spring Magic 3.5a private engine; import only after PyMel preflight.\"\"\"\n__version__='3.5a'\n")
    put(native/'main.py',"def main():\n    from ..tool import SpringMagicTool\n    return SpringMagicTool().show_ui()\n")
    put(native/'springMagic.py',"from .main import main\n# Explicit invocation only; no sys.path mutation or import-time UI.\n")
    # The developer module is retained verbatim in the archive; it reloads global
    # modules and is not part of the production runtime.
    runtime_hashes={p.relative_to(PKG).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in native.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    put(PKG/'catalog.json',json.dumps({'files':rows,'definitions':definitions,'runtime_sha256':runtime_hashes,'source_version':'3.5a','license':'No independent license supplied; author Yanbin Bai, 3.5a fixes Benoit Degand. Local preparation only; distribution authorization unresolved.'},ensure_ascii=False,indent=2)+'\n')
    put(UNIT/'.gitattributes','springmagic/** -text\n')
    put(RC/'.gitattributes','* -text\n')
    launch=(ROOT/'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake','spring_magic_v3_5a').replace('RootMotionBakeTool','SpringMagicTool')
    put(RC/'launch_candidate.py',launch)
    payload=[p for folder in (RC/'maya_toolkit',RC/'docs',RC/'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
    put(RC/'promotion.json',json.dumps({'tool_id':'spring_magic_v3_5a','registration':{'module':'spring_magic_v3_5a','class_name':'SpringMagicTool'},'files':[{'source':p.relative_to(RC).as_posix(),'target':p.relative_to(RC).as_posix()} for p in sorted(payload)],'resources':[r['path'] for r in rows],'dependencies':['Maya cmds/MEL','PyMel compatible with the target Maya/Python (not bundled; absent from this machine Maya 2025)','Full private Spring Magic 3.5a engine/UI/icons, all included'],'acceptance_required':True,'change_summary':'Complete original spring/twist/tension/inertia/extension, looping/pose-match, capsule/plane/wind and controller-binding engine retained. Python 3 private imports, safe API/UI bridge, UUID ownership, deterministic helper cleanup, read-only preflight, Undo, complete resources/docs/tests/promotion prepared.','verification_limitations':['PyMel absent on installed Maya 2025: full engine, collision geometry, bind/bake and GUI not executed','Source supplied no redistribution license; local preparation only','Original Floor/Subs fields have no implemented algorithm; disabled with explanation','Straight originally called missing straightBonePose; explicit selected joint rotate-zero repair requires Maya acceptance','Bind-pose runtime can touch the connected skin/bind-pose hierarchy; explicit API allowance required','Normal spring mode originally cuts all keyable channels of processed parents/children in the range; explicit acknowledgement required','Non-uniformly scaled capsule/plane, cancellation, animation layers, constrained rigs and Maya/PyMel version support require manual acceptance']},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'files':len(rows),'definitions':{k:len(v) for k,v in definitions.items()}}))


if __name__=='__main__':
    main()
