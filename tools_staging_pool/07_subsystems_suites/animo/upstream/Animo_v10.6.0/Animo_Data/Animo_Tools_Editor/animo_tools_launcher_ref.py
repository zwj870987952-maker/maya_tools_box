from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os
import re
import types
import marshal
import importlib.abc
import importlib.machinery
import importlib.util
import maya.cmds as cmds


def get_maya_version():
    return int(cmds.about(version=True)[:4])


MAYA_VERSION = get_maya_version()


class VersionedModuleFinder(importlib.abc.MetaPathFinder):
    
    def __init__(self, search_paths, maya_version):
        self.search_paths = search_paths
        self.maya_version = maya_version
    
    def find_spec(self, fullname, path, target=None):
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
            
            py_path = os.path.join(search_path, fullname + ".py")
            if os.path.exists(py_path):
                return None
            
            versioned_pyc = os.path.join(search_path, "{0}_py{1}.pyc".format(fullname, self.maya_version))
            if os.path.exists(versioned_pyc):
                loader = importlib.machinery.SourcelessFileLoader(fullname, versioned_pyc)
                return importlib.util.spec_from_loader(fullname, loader, origin=versioned_pyc)
            
            generic_pyc = os.path.join(search_path, fullname + ".pyc")
            if os.path.exists(generic_pyc):
                loader = importlib.machinery.SourcelessFileLoader(fullname, generic_pyc)
                return importlib.util.spec_from_loader(fullname, loader, origin=generic_pyc)
        
        return None


_versioned_finder = None

def install_versioned_finder(search_paths):
    global _versioned_finder
    
    sys.meta_path[:] = [
        finder for finder in sys.meta_path
        if type(finder).__name__ != "VersionedModuleFinder"
    ]
    
    _versioned_finder = VersionedModuleFinder(search_paths, MAYA_VERSION)
    sys.meta_path.insert(0, _versioned_finder)


def get_animo_tools_path():
    maya_scripts_dir = cmds.internalVar(userScriptDir=True)
    global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
    
    return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")


def purge_stale_modules(animo_tools_path):
    if not os.path.isdir(animo_tools_path):
        return
    
    module_names = set()
    
    for filename in os.listdir(animo_tools_path):
        if filename.endswith('.py'):
            module_names.add(filename[:-3])
        elif filename.endswith('.pyc'):
            base_name = filename[:-4]
            prefix, marker, suffix = base_name.rpartition('_py')
            if marker and suffix.isdigit():
                base_name = prefix
            module_names.add(base_name)
    
    normalized_base_dir = os.path.normcase(os.path.normpath(animo_tools_path))
    
    for module_name in module_names:
        cached_module = sys.modules.get(module_name)
        if cached_module is None:
            continue
        
        cached_file = getattr(cached_module, '__file__', None)
        if not cached_file:
            continue
        
        cached_dir = os.path.normcase(os.path.normpath(os.path.dirname(cached_file)))
        if cached_dir != normalized_base_dir:
            continue
        
        del sys.modules[module_name]


def find_versioned_file(folder, base_name):
    py_path = os.path.join(folder, base_name + ".py")
    if os.path.exists(py_path):
        return py_path, "py"
    
    versioned_pyc = os.path.join(folder, "{0}_py{1}.pyc".format(base_name, MAYA_VERSION))
    if os.path.exists(versioned_pyc):
        return versioned_pyc, "pyc"
    
    pattern = re.compile(r'^' + re.escape(base_name) + r'_py(\d{4})\.pyc$', re.IGNORECASE)
    available_versions = []
    
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            match = pattern.match(filename)
            if match:
                file_version = int(match.group(1))
                available_versions.append((file_version, filename))
    
    if available_versions:
        available_versions.sort(key=lambda x: x[0], reverse=True)
        
        for file_version, filename in available_versions:
            if file_version <= MAYA_VERSION:
                return os.path.join(folder, filename), "pyc"
        
        return os.path.join(folder, available_versions[-1][1]), "pyc"
    
    generic_pyc = os.path.join(folder, base_name + ".pyc")
    if os.path.exists(generic_pyc):
        return generic_pyc, "pyc"
    
    return None, None


def show():
    animo_tools_path = get_animo_tools_path()
    
    purge_stale_modules(animo_tools_path)
    
    sys._animo_tools_path = animo_tools_path
    
    if animo_tools_path in sys.path:
        sys.path.remove(animo_tools_path)
    sys.path.insert(0, animo_tools_path)
    
    install_versioned_finder([animo_tools_path])
    
    filepath, filetype = find_versioned_file(animo_tools_path, "animo_tools_manager")
    
    if filepath is None:
        cmds.warning("Could not find animo_tools_manager in: {0}".format(animo_tools_path))
        return
    
    previous_module = sys.modules.get("animo_tools_manager")
    previous_dialog = getattr(previous_module, 'animo_dialog', None)
    
    try:
        module = types.ModuleType("animo_tools_manager")
        module.__file__ = filepath
        module.__builtins__ = __builtins__
        
        sys.modules["animo_tools_manager"] = module
        
        if filetype == "py":
            with open(filepath, 'r') as f:
                code = compile(f.read(), filepath, 'exec')
        else:
            with open(filepath, 'rb') as f:
                f.read(16)
                code = marshal.load(f)
        
        exec(code, module.__dict__)
        module.animo_dialog = previous_dialog
        sys.modules["animo_tools_manager"] = module
        
        if hasattr(module, 'show_animo_tools'):
            module.show_animo_tools()
        else:
            cmds.warning("show_animo_tools not found in module")
            
    except Exception as e:
        sys.modules.pop("animo_tools_manager", None)
        cmds.warning("Error launching Tools Editor: {0}".format(str(e)))
        import traceback
        traceback.print_exc()


def main():
    show()


if __name__ == "__main__":
    show()