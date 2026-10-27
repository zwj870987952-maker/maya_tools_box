"""Unified batch weights and every full original GUI business command."""
import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .fileio import finite

CATALOG=json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf8'))
COMMANDS=sorted({row['function'] for rows in CATALOG['ui_controls'].values() for row in rows} | {'goreGetBaseMeshCmd','goreAddCmd','goreRemoveCmd','goreClearCmd','goreMakeCmd'})
ACTIONS=['status','inspect_skin','set_weights','export_weights','import_weights','ui_command','show_ui','show_gore','close_ui']
PROPERTIES={
    'action':{'type':'string','enum':ACTIONS,'default':'status'},
    'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},
    'weights':{'type':'object','additionalProperties':{'type':'number','minimum':0,'maximum':1}},
    'path':{'type':'string'},
    'command':{'type':'string','enum':COMMANDS},
    'language':{'type':'string','enum':['','chn','eng','jpn'],'default':''},
    'allow_scene_scope':{'type':'boolean','default':False,'description':'Allow explicitly previewed entire-scene rename (GUI All mode)'}
}


def normalize(kwargs):
    if set(kwargs)-set(PROPERTIES):
        raise ValueError('Unknown arguments')
    p=dict(kwargs)
    p.setdefault('action','status')
    if p['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    applicable={'status':set(),'inspect_skin':{'objects'},'set_weights':{'objects','weights'},'export_weights':{'objects','path'},'import_weights':{'objects','path'},'ui_command':{'command','allow_scene_scope'},'show_ui':{'language'},'show_gore':set(),'close_ui':set()}
    if set(p)-{'action'}-applicable[p['action']]:
        raise ValueError('Arguments do not apply to action')
    if 'objects' in p and (not isinstance(p['objects'],list) or not p['objects'] or len(p['objects'])!=len(set(p['objects'])) or any(not isinstance(v,str) or not v for v in p['objects'])):
        raise ValueError('Objects must be a nonempty list of distinct names/components')
    if 'path' in p and (not isinstance(p['path'],str) or not p['path']):
        raise ValueError('Path must be a nonempty string')
    if 'language' in p and p['language'] not in ('','chn','eng','jpn'):
        raise ValueError('Invalid language')
    if 'allow_scene_scope' in p and type(p['allow_scene_scope']) is not bool:
        raise ValueError('allow_scene_scope must be boolean')
    if p['action']=='ui_command' and p.get('command') not in COMMANDS:
        raise ValueError('A known UI command is required')
    if p['action']=='set_weights':
        weights=p.get('weights')
        if not isinstance(weights,dict) or not weights or any(not isinstance(k,str) or not k or not finite(v) or not 0<=v<=1 for k,v in weights.items()) or abs(sum(weights.values())-1)>1e-6:
            raise ValueError('Weights must be distinct influence names, finite values [0,1], sum=1')
    if p['action'] in ('export_weights','import_weights') and 'path' not in p:
        raise ValueError('Path is required')
    return p


class SkinMagicTool(BaseMayaTool):
    tool_id='skin_magic'
    tool_name='SkinMagic 4.0'
    category='rigging'
    version='4.0-candidate.1'
    description='Complete original skin weights, LoD, rename, bind, deformer/blendshape/weight-map and supplemental Gore GUI; batch inspect/set/JSON weights. Full GUI requires PyMel. Real Maya acceptance pending.'
    parameters_schema={'type':'object','properties':PROPERTIES,'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only SkinMagic plan',data=preflight(normalize(kwargs)),dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from .runtime import execute
        return ToolResult.ok(message='SkinMagic action complete; GUI acceptance pending',data=execute(normalize(kwargs)))

    def show_ui(self,parent=None):
        from .ui_support import show_ui
        return show_ui()
