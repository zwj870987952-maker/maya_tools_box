"""Explicit suite installation/activation adapter, distinct from suite tools."""
import importlib
import os
from pathlib import Path
import sys
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import files

ACTIONS = ['inspect', 'install_files', 'register_module', 'launch_native']


def normalize(**kwargs):
    if set(kwargs) - {'action', 'destination', 'module_dir', 'acknowledge_external_effects'}:
        raise ValueError('Unknown arguments')
    p = dict(action='inspect', acknowledge_external_effects=False)
    p.update(kwargs)
    if p['action'] not in ACTIONS or type(p['acknowledge_external_effects']) is not bool:
        raise ValueError('Invalid action or acknowledgement')
    if p['action'] != 'inspect' and 'destination' not in p:
        raise ValueError('An absolute new/installed destination is required')
    if p['action'] == 'inspect' and ('destination' in p or 'module_dir' in p):
        raise ValueError('Inspect reads only bundled resources')
    if p['action'] not in ('register_module', 'launch_native') and 'module_dir' in p:
        raise ValueError('module_dir only applies to module registration/native launch')
    return p


def preflight(p):
    from maya import cmds
    action = p['action']
    if action == 'inspect':
        plan = files.snapshot()
    elif action == 'install_files':
        plan = files.install_plan(p['destination'])
    else:
        if os.name != 'nt':
            raise ValueError('Windows Maya is required')
        if not p['acknowledge_external_effects']:
            raise ValueError('Acknowledge module/preferences/runtime commands/plugin/menu/hotkey effects before activation')
        plan = files.installed(p['destination'])
        default = Path(cmds.internalVar(userAppDir=True)) / 'modules'
        directory = files.explicit_path(p.get('module_dir', str(default)))
        if not directory.is_dir():
            raise ValueError('Create/choose an existing module directory explicitly before activation')
        path = directory / 'tbAnimTools.mod'
        files.explicit_path(str(path))
        text = files.module_text(plan['destination'], str(cmds.about(version=True)))
        plan.update(module_file=str(path), module_text=text, auto_updates='disabled via persistent tbUpdateType=2')
        if action == 'register_module':
            if path.exists():
                raise ValueError('Existing tbAnimTools.mod will never be overwritten')
        else:
            if cmds.about(batch=True):
                raise ValueError('Native suite activation needs interactive Maya; no standalone Qt launch')
            if directory != default.resolve():
                raise ValueError('Native installer writes the default user module directory; register there first')
            if not path.is_file() or path.read_text(encoding='utf-8') != text:
                raise ValueError('Register this exact candidate module first; existing foreign module rejected')
            # Upstream uses top-level imports. A different loaded suite cannot
            # safely be unloaded; restart instead of replacing sys.modules.
            roots = {x['path'].split('/')[0][:-3] for x in plan['files'] if '/' not in x['path'] and x['path'].endswith('.py')}
            roots.add('apps')
            if any(k.split('.')[0] in roots for k in sys.modules):
                raise ValueError('TB namespace already loaded; restart Maya before the first native activation')
    plan.update(action=action, gui_acceptance='not_run', scene_undo='File writes, optionVars, deferred startup and hotkey registration are outside Maya Undo')
    return plan


class TBAnimToolsTool(BaseMayaTool):
    tool_id = 'tb_anim_tools'
    tool_name = 'TB Anim Tools 安装与启动'
    category = 'animation'
    version = '1.0.0-candidate.1'
    description = 'Inspect/install a complete pinned TB suite without network or overwrites; separately register a module and explicitly launch the original suite. Activation affects persistent Maya settings and commands.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'}, 'destination': {'type': 'string', 'minLength': 1}, 'module_dir': {'type': 'string', 'minLength': 1}, 'acknowledge_external_effects': {'type': 'boolean', 'default': False}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='Read-only pinned suite preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from maya import cmds
        p = normalize(**kwargs)
        plan = preflight(p)
        action = p['action']
        if action == 'install_files':
            plan = files.install(p['destination'])
        elif action == 'register_module':
            # No existing module or userSetup/hotkeys file is replaced.
            with open(plan['module_file'], 'x', encoding='utf-8', newline='\n') as stream:
                stream.write(plan['module_text'])
            cmds.optionVar(intValue=('tbUpdateType', 2))
        elif action == 'launch_native':
            cmds.optionVar(intValue=('tbUpdateType', 2))
            for suffix in ('', 'Icons', 'apps'):
                path = str(Path(plan['destination']) / suffix)
                if path not in sys.path:
                    sys.path.append(path)
            importlib.invalidate_caches()
            # Execute the complete, unchanged vendor initializer only after
            # explicit GUI acceptance. Its deferred jobs are not atomic/Undo.
            module = importlib.import_module('tbtoolsInstaller')
            if Path(module.__file__).resolve() != (Path(plan['destination']) / 'tbtoolsInstaller.py').resolve():
                raise RuntimeError('Python resolved a foreign TB installer; restart and remove conflicting paths')
            module.installer().install()
            plan['startup_state'] = 'original deferred startup requested; success requires real Maya acceptance'
        return ToolResult.ok(message='TB suite action completed: ' + action, data=plan, warnings=[] if action == 'inspect' else ['File/preferences/startup effects cannot be reverted by Maya Undo', 'Real Maya suite/GUI acceptance is still not_run'])

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui(parent)
