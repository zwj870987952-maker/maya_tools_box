"""Validate all native cache exports/imports, including reloaded original UI callbacks."""
import ast
import functools
import inspect
from pathlib import Path
import re

PACKAGE = Path(__file__).resolve().parent


def external_directory(value):
    if not isinstance(value,str) or not value or not Path(value).is_absolute():
        raise ValueError('Use an absolute directory')
    directory = Path(value).resolve()
    if directory==PACKAGE or PACKAGE in directory.parents:
        raise ValueError('User data/cache must be outside bundled code')
    return directory


def cache_path(value,leaf,writing=False):
    directory = external_directory(value)
    if re.search(r'[\s;"`$]',directory.as_posix()):
        raise ValueError('Original MEL cache path requires no spaces, quotes, control characters or command punctuation')
    target = directory/leaf
    if writing:
        if target.exists():
            raise ValueError('Cache overwrite refused: '+str(target)+'; choose a new version/directory')
        if not directory.is_dir() and not directory.parent.is_dir():
            raise ValueError('Create the cache parent directory first')
    elif not target.is_file():
        raise ValueError('Missing input cache: '+str(target))
    return directory,target


def node_list(value):
    if isinstance(value,str):
        value = ast.literal_eval(value)
    if not isinstance(value,list) or not value or any(not isinstance(n,str) or not n or re.search(r'[\s;"`{}$()]',n) for n in value):
        raise ValueError('Use a nonempty list of simple Maya node paths')
    return value


def cache_io(leaf,writing):
    def decorate(function):
        signature = inspect.signature(function)
        @functools.wraps(function)
        def guarded(*args,**kwargs):
            import maya.cmds as cmds
            bound = signature.bind(*args,**kwargs)
            directory,target = cache_path(bound.arguments['path'],leaf,writing)
            bound.arguments['path'] = directory.as_posix()
            plugin = ('AbcExport' if writing else 'AbcImport') if leaf=='geometry.abc' else None
            if plugin and function.__name__!='swap' and not cmds.pluginInfo(plugin,query=True,loaded=True):
                raise ValueError('Load '+plugin+' explicitly before cache I/O')
            for key in ('geos','cams'):
                if key in bound.arguments:
                    nodes = node_list(bound.arguments[key])
                    if any(not cmds.objExists(n) for n in nodes):
                        raise ValueError('Cache roots include missing nodes')
                    bound.arguments[key] = nodes
            return function(*bound.args,**bound.kwargs)
        return guarded
    return decorate
