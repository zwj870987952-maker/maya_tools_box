"""Pure in-memory configuration; no Qt import, file writes or Maya edits."""
import copy
import json
from pathlib import Path

LIBRARY = json.loads(Path(__file__).with_name('library.json').read_text(encoding='utf-8'))
KNOWN = {tool['id'] for cat in LIBRARY['MAIN_TOOL_LIBRARY'].values() for mod in cat['modules'].values() for tool in mod['tools']}
KNOWN.update(LIBRARY['CLASSIC_DEFAULT_TOOLS']); KNOWN.update(LIBRARY['CLASSIC_GRAPH_EDITOR_TOOLS'])
PRESETS = copy.deepcopy(LIBRARY['PRESETS'])
CONFIGS = {
    'main':{'active_tools':set(LIBRARY['CLASSIC_DEFAULT_TOOLS']), 'location':'时间轴顶部', 'alignment':'center', 'single_row':False},
    'graph_editor':{'active_tools':set(LIBRARY['CLASSIC_GRAPH_EDITOR_TOOLS']), 'location':'在图形编辑器菜单下', 'alignment':'center', 'single_row':False}}
CURRENT_PRESET = 'Classic *'

def snapshot():
    return {'current_preset':CURRENT_PRESET, 'configs':{key:dict(value, active_tools=sorted(value['active_tools'])) for key,value in CONFIGS.items()},
            'preset_names':sorted(PRESETS), 'tool_library_count':len(KNOWN), 'animation_algorithms_implemented':False,
            'capability':'Supplied toolbar/workspace UI prototype only; animation menu labels do not implement animation operations.'}

def configuration(toolbar, config):
    if toolbar not in CONFIGS: raise ValueError('toolbar must be main or graph_editor')
    if not isinstance(config,dict) or not config or set(config)-{'active_tools','location','alignment','single_row'}:
        raise ValueError('Nonempty supported config required')
    result = copy.deepcopy(CONFIGS[toolbar])
    for key,value in config.items():
        if key == 'active_tools':
            if not isinstance(value,list) or not all(isinstance(t,str) for t in value) or len(value)!=len(set(value)) or set(value)-KNOWN:
                raise ValueError('Unknown or duplicate tool ids')
            value=set(value)
        elif key == 'single_row':
            if not isinstance(value,bool): raise ValueError('single_row must be boolean')
        elif key == 'alignment':
            if value not in ('left','center','right'): raise ValueError('Invalid alignment')
        elif key == 'location':
            choices = LIBRARY['MAIN_LOCATIONS' if toolbar=='main' else 'GRAPH_EDITOR_LOCATIONS']
            if value not in choices: raise ValueError('Invalid location for toolbar')
        result[key]=value
    return result

def preset_plan(name):
    if not isinstance(name,str) or name not in PRESETS: raise ValueError('Unknown preset')
    result={}
    for toolbar in CONFIGS:
        cfg=copy.deepcopy(PRESETS[name][toolbar]); active=cfg['active_tools']
        cfg['active_tools']=sorted(KNOWN) if active is None else active
        cfg['alignment']={'左对齐':'left','居中对齐':'center','右对齐':'right','单行':'center'}.get(cfg['alignment'],cfg['alignment'])
        result[toolbar]=configuration(toolbar,cfg)
    return result

def apply_preset(name):
    global CURRENT_PRESET
    plan=preset_plan(name)
    for toolbar,cfg in plan.items(): CONFIGS[toolbar].clear(); CONFIGS[toolbar].update(cfg)
    CURRENT_PRESET=name
