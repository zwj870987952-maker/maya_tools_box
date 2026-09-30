"""Catalog validation without importing Maya or vendor modules."""
import copy
import hashlib
import json
import math
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
CATALOG = json.loads((PACKAGE/'catalog.json').read_text(encoding='utf-8'))
DEFAULTS = dict(action='inventory',function='',arguments={},dock=0)
API_FUNCTIONS = sorted(name for name,fn in CATALOG['functions'].items() if fn['callable_by_api'])
HEADLESS = {'sculptPose.sculpt','sculptPose.sculpt_sel','sculptPose.abortSculpt','sculptPose.getAttrs','sculptPose.atoi','sculptPose.sortKey',
            'wrap.wrapToWorld','wrap.wrapToWorld_sel','wrap.duplicate','wrap.extractFaces','growShrink.run','iron.run',
            'assignColors.createMat','assignColors.createMats','assignColors.assign','assignColors.assign_sel','assignColors.random','assignColors.random_sel','assignColors.printColor','assignColors.printColor_sel',
            'smoothPreview.run','quickBake.run','quickBake.run_sel','quickBake.rivet','quickBake.rivet_sel','quickBake.plane','quickBake.plane_sel',
            'rivetStuff.rivet','rivetStuff.rivet_sel','rivetStuff.stickyMod','copyPasteAttrs.copy','copyPasteAttrs.paste','caching.exp_cams','caching.exp_geos','caching.imp_cams','caching.swap'}
NODE_PARAMS = {'geo','scu','drvn','drvr','obj','object','surf','sm','bs','drv','mat','vtx','cp','outGeo'}
ARRAY_PARAMS = {'verts','dfrmverts','floodverts','comps','objs','chars','geos','cams','sm'}
INT_PARAMS = {'lv','ihi','vis','shade','editMode','smooth','its','hideData','allP2P','loc','sphVis','lra','div','rate','skipOrtho','grpPar','k','color','create','cnt','dock','mode'}


def resources():
    for relative,digest in CATALOG['resources'].items():
        path = PACKAGE/relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Missing/changed original resource: '+relative)


def json_value(value):
    if value is None or type(value) in (str,bool,int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError('Numbers must be finite')
        return
    if isinstance(value,list):
        for item in value:
            json_value(item)
        return
    if isinstance(value,dict) and all(isinstance(k,str) for k in value):
        for item in value.values():
            json_value(item)
        return
    raise ValueError('Arguments must contain ordinary JSON values')


def normalize(kwargs):
    if set(kwargs)-set(DEFAULTS):
        raise ValueError('Unknown top-level parameter')
    args = dict(DEFAULTS,**kwargs)
    if args['action'] not in ('inventory','open_ui','invoke') or type(args['dock']) is not int or args['dock'] not in (0,1):
        raise ValueError('Unknown action or dock (0/1)')
    if not isinstance(args['function'],str) or not isinstance(args['arguments'],dict):
        raise ValueError('function requires text; arguments requires object')
    json_value(args['arguments'])
    if args['action']!='invoke':
        if args['function'] or args['arguments']:
            raise ValueError('function/arguments are only used by invoke')
        return args,None,{}
    if args['function'] not in API_FUNCTIONS:
        raise ValueError('Choose an exported JSON callable from inventory')
    fn = CATALOG['functions'][args['function']]
    names = {p['name'] for p in fn['parameters']}
    if set(args['arguments'])-names:
        raise ValueError('Unknown function argument')
    bound = {}
    for p in fn['parameters']:
        if p['name'] not in args['arguments'] and p['required']:
            raise ValueError('Missing argument: '+p['name'])
        bound[p['name']] = copy.deepcopy(args['arguments'].get(p['name'],p.get('default')))
    for name,value in bound.items():
        string_mode = name=='mode' and (args['function'].startswith('assignColors.') or args['function'] in ('sculptPose.run','sculptPose.apply','sculptPose.apply_sel'))
        color_value = name=='color' and (args['function'].startswith('assignColors.') or args['function']=='ui.assignColor')
        if name in INT_PARAMS and not string_mode and not color_value:
            if type(value) is not int:
                raise ValueError(name+' requires an integer')
            if name in ('lv','rate','its') and value<1 or name in ('smooth','div','cnt') and value<0:
                raise ValueError(name+' outside allowed range')
            if name in ('ihi','vis','shade','editMode','hideData','allP2P','loc','sphVis','lra','skipOrtho','grpPar','k','create','dock') and value not in (0,1):
                raise ValueError(name+' must be 0/1')
            if name=='color' and not 0<=value<=31:
                raise ValueError('Maya indexed color must be 0..31')
        if name in ('falloff','scale') and (isinstance(value,bool) or not isinstance(value,(int,float)) or value<=0):
            raise ValueError(name+' must be positive')
        if name in ('path','geo','scu','drvn','drvr','obj','surf','bs','drv','mat','vtx','cp','outGeo','n','cb','text','name') and not isinstance(value,str):
            raise ValueError(name+' requires text')
        if name in ARRAY_PARAMS and name!='sm' and not isinstance(value,(str,list)):
            raise ValueError(name+' requires a JSON array or legacy literal array text')
    if args['function'] in ('sculptPose.run','sculptPose.apply','sculptPose.apply_sel') and bound.get('mode') not in ('standard','p2p'):
        raise ValueError('mode must be standard/p2p')
    if args['function'].startswith('assignColors.') and 'mode' in bound and bound['mode'] not in ('blinn','lambert'):
        raise ValueError('mode must be blinn/lambert')
    if args['function']=='assignColors.createMat':
        if not isinstance(bound['color'],list) or len(bound['color'])!=3 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not 0<=v<=1 for v in bound['color']):
            raise ValueError('color requires three finite components in 0..1')
    return args,fn,bound
