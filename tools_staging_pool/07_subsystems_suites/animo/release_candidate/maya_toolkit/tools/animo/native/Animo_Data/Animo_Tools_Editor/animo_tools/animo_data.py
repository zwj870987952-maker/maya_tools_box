from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os
import shutil
import zipfile
import tempfile
import maya.cmds as cmds


def _get_animo_tools_editor_root():
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.normpath(os.path.join(this_dir, ".."))
    except NameError:
        pass
    
    maya_scripts_dir = cmds.internalVar(userScriptDir=True)
    global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
    return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor")


def get_animo_data_path():
    animo_data_dir = _get_animo_tools_editor_root()
    
    if not os.path.exists(animo_data_dir):
        os.makedirs(animo_data_dir)
    
    _migrate_legacy_animo_data(animo_data_dir)
    
    return animo_data_dir


def _migrate_legacy_animo_data(shared_animo_data_dir):
    try:
        maya_scripts = cmds.internalVar(userScriptDir=True)
        legacy_dir = os.path.join(maya_scripts, "Animo_Data", "Animo_Tools_Editor")
        
        same_folder = os.path.normcase(os.path.normpath(legacy_dir)) == os.path.normcase(os.path.normpath(shared_animo_data_dir))
        if same_folder or not os.path.exists(legacy_dir):
            return
        
        for filename in ("animo_tools.json", "animo_hotkeys.json"):
            legacy_file = os.path.join(legacy_dir, filename)
            shared_file = os.path.join(shared_animo_data_dir, filename)
            if os.path.exists(legacy_file) and not os.path.exists(shared_file):
                shutil.copyfile(legacy_file, shared_file)
    except Exception:
        pass


def get_tools_library_path():
    animo_data_root = _get_animo_tools_editor_root()
    tools_library_dir = os.path.join(animo_data_root, "tools_library")
    
    if not os.path.exists(tools_library_dir):
        legacy_dir = os.path.join(animo_data_root, "animo_others")
        if os.path.exists(legacy_dir):
            try:
                shutil.move(legacy_dir, tools_library_dir)
            except Exception:
                pass
    
    if not os.path.exists(tools_library_dir):
        os.makedirs(tools_library_dir)
    
    return tools_library_dir


def resolve_path_relative_to_tools_library(stored_path):
    if not stored_path:
        return ''
    
    normalized = stored_path.replace('\\', '/')
    marker = '/tools_library/'
    marker_index = normalized.lower().find(marker)
    if marker_index == -1:
        return ''
    
    relative_part = normalized[marker_index + len(marker):]
    relative_parts = [p for p in relative_part.split('/') if p]
    if not relative_parts:
        return ''
    
    local_tools_library = get_tools_library_path()
    candidate = os.path.join(local_tools_library, *relative_parts)
    
    if os.path.exists(candidate):
        return candidate
    
    return ''


def get_default_settings_file():
    return os.path.join(_get_animo_tools_editor_root(), "default_settings.json")


def export_tool_library_zip(destination_zip_path):
    root_dir = _get_animo_tools_editor_root()
    
    tools_json = os.path.join(root_dir, "animo_tools.json")
    hotkeys_json = os.path.join(root_dir, "animo_hotkeys.json")
    tools_library_dir = get_tools_library_path()
    custom_icons_dir = os.path.join(root_dir, "icons", "custom")
    
    with zipfile.ZipFile(destination_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists(tools_json):
            zf.write(tools_json, "animo_tools.json")
        
        if os.path.exists(hotkeys_json):
            zf.write(hotkeys_json, "animo_hotkeys.json")
        
        for base_dir, arc_prefix in ((tools_library_dir, "tools_library"), (custom_icons_dir, os.path.join("icons", "custom"))):
            if not os.path.isdir(base_dir):
                continue
            for dirpath, dirnames, filenames in os.walk(base_dir):
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    rel_path = os.path.relpath(full_path, base_dir)
                    arcname = os.path.join(arc_prefix, rel_path)
                    zf.write(full_path, arcname)
    
    return destination_zip_path


def extract_tool_library_zip(source_zip_path):
    temp_dir = tempfile.mkdtemp(prefix="animo_tools_import_")
    with zipfile.ZipFile(source_zip_path, 'r') as zf:
        zf.extractall(temp_dir)
    return temp_dir


def copy_imported_tool_asset(imported_tools_library_root, stored_path, target_folder, desired_filename):
    if not stored_path:
        return ''
    
    normalized = stored_path.replace('\\', '/')
    marker = '/tools_library/'
    marker_index = normalized.lower().find(marker)
    
    if marker_index != -1:
        relative_part = normalized[marker_index + len(marker):]
    elif not _looks_like_absolute_path(stored_path):
        relative_part = normalized
    else:
        return ''
    
    relative_parts = [p for p in relative_part.split('/') if p]
    if not relative_parts:
        return ''
    
    source_path = os.path.join(imported_tools_library_root, *relative_parts)
    if not os.path.exists(source_path):
        return ''
    
    try:
        if not os.path.isdir(target_folder):
            os.makedirs(target_folder)
    except Exception:
        pass
    
    base_name, ext = os.path.splitext(desired_filename)
    target_path = os.path.join(target_folder, desired_filename)
    counter = 2
    while os.path.exists(target_path):
        target_path = os.path.join(target_folder, "{0}_{1}{2}".format(base_name, counter, ext))
        counter += 1
    
    try:
        shutil.copyfile(source_path, target_path)
        return target_path
    except Exception:
        return ''


def save_default_settings(data):
    try:
        file_path = get_default_settings_file()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False


def load_default_settings():
    try:
        file_path = get_default_settings_file()
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def sanitize_name(name):
    if not name:
        return "Unnamed"
    
    invalid_chars = '<>:"/\\|?*'
    cleaned = ''.join(ch for ch in name if ch not in invalid_chars and ord(ch) >= 32)
    cleaned = cleaned.strip().strip('.').strip()
    
    if not cleaned:
        cleaned = "Unnamed"
    
    return cleaned


def get_category_folder_path(category_name, create=True):
    library_path = get_tools_library_path()
    folder_name = sanitize_name(category_name)
    folder_path = os.path.join(library_path, folder_name)
    
    if create and not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
        except Exception:
            pass
    
    return folder_path


def delete_category_folder(category_name):
    try:
        folder_path = get_category_folder_path(category_name, create=False)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        return True
    except Exception:
        return False


def rename_category_folder(old_category_name, new_category_name):
    try:
        old_path = get_category_folder_path(old_category_name, create=False)
        new_path = get_category_folder_path(new_category_name, create=False)
        
        if old_path == new_path:
            return True
        
        if not os.path.exists(old_path):
            get_category_folder_path(new_category_name, create=True)
            return True
        
        if os.path.exists(new_path):
            for item in os.listdir(old_path):
                src = os.path.join(old_path, item)
                dst = os.path.join(new_path, item)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            if not os.listdir(old_path):
                os.rmdir(old_path)
        else:
            shutil.move(old_path, new_path)
        
        return True
    except Exception:
        return False


def _get_unique_file_path(folder_path, base_name, extension):
    candidate = os.path.join(folder_path, base_name + extension)
    if not os.path.exists(candidate):
        return candidate
    
    counter = 2
    while True:
        candidate = os.path.join(folder_path, "{0}_{1}{2}".format(base_name, counter, extension))
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def save_category_tool_file(category_name, tool_name, script_content, script_type):
    try:
        folder_path = get_category_folder_path(category_name, create=True)
        extension = ".mel" if script_type == "MEL" else ".py"
        base_name = sanitize_name(tool_name)
        file_path = _get_unique_file_path(folder_path, base_name, extension)
        
        with open(file_path, 'w') as f:
            f.write(script_content or "")
        
        return file_path
    except Exception:
        return None


def save_tooltip_sidecar(tool_entry):
    file_path = tool_entry.get('file_path')
    if not file_path:
        return
    
    try:
        sidecar_path = os.path.splitext(file_path)[0] + '.tooltip.json'
        gif_path = tool_entry.get('tooltip_gif_path', '')
        sidecar_data = {
            'title': tool_entry.get('tooltip_title', ''),
            'description': tool_entry.get('tooltip_description', ''),
            'gif_filename': os.path.basename(gif_path) if gif_path else '',
            'gif_width': tool_entry.get('tooltip_gif_width', '')
        }
        with open(sidecar_path, 'w') as f:
            json.dump(sidecar_data, f, indent=4)
    except Exception:
        pass


def resolve_gif_path_from_sidecar(file_path):
    if not file_path:
        return ''
    
    folder_path = os.path.dirname(file_path)
    sidecar_path = os.path.splitext(file_path)[0] + '.tooltip.json'
    
    gif_filename = ''
    if os.path.exists(sidecar_path):
        try:
            with open(sidecar_path, 'r') as f:
                sidecar_data = json.load(f)
            gif_filename = sidecar_data.get('gif_filename', '')
        except Exception:
            gif_filename = ''
    
    if gif_filename:
        candidate_path = os.path.join(folder_path, gif_filename)
        if os.path.exists(candidate_path):
            return candidate_path
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    fallback_path = os.path.join(folder_path, base_name + '.tooltip.gif')
    if os.path.exists(fallback_path):
        return fallback_path
    
    found_elsewhere = find_gif_anywhere_in_library(base_name)
    if found_elsewhere:
        try:
            shutil.copyfile(found_elsewhere, fallback_path)
            return fallback_path
        except Exception:
            return found_elsewhere
    
    return ''


def save_category_tool_gif(category_name, tool_name, source_gif_path):
    try:
        folder_path = get_category_folder_path(category_name, create=True)
        base_name = sanitize_name(tool_name)
        target_path = os.path.join(folder_path, base_name + ".tooltip.gif")
        shutil.copyfile(source_gif_path, target_path)
        return target_path
    except Exception:
        return None


def save_tool_gif_next_to_script(tool_file_path, tool_name, source_gif_path):
    if not tool_file_path:
        return None
    
    try:
        folder_path = os.path.dirname(tool_file_path)
        base_name = sanitize_name(tool_name)
        target_path = os.path.join(folder_path, base_name + ".tooltip.gif")
        shutil.copyfile(source_gif_path, target_path)
        return target_path
    except Exception:
        return None


def find_gif_anywhere_in_library(tool_name):
    library_path = get_tools_library_path()
    if not os.path.isdir(library_path):
        return ''
    
    base_name = sanitize_name(tool_name)
    target_filename = (base_name + ".tooltip.gif").lower()
    
    for dirpath, dirnames, filenames in os.walk(library_path):
        for filename in filenames:
            if filename.lower() == target_filename:
                return os.path.join(dirpath, filename)
    
    return ''


def extract_raw_script(script, script_type):
    if script_type == "MEL":
        prefix = "import maya.mel as mel; mel.eval('''"
        suffix = "''')"
        if script.startswith(prefix) and script.endswith(suffix):
            return script[len(prefix):-len(suffix)]
    
    return script


def wrap_script_for_command(script_type, raw_script):
    if script_type == "MEL":
        return "import maya.mel as mel; mel.eval('''{0}''')".format(raw_script or "")
    
    return raw_script or ""


def ensure_category_tool_file(category_name, tool_entry):
    file_path = tool_entry.get('file_path')
    if file_path and os.path.exists(file_path):
        return file_path
    
    script_type = tool_entry.get('script_type', 'Python')
    raw_script = extract_raw_script(tool_entry.get('script', ''), script_type)
    
    return save_category_tool_file(
        category_name,
        tool_entry.get('name', 'Unnamed'),
        raw_script,
        script_type
    )


def move_category_tool_file(old_file_path, new_category_name, tool_name, script_content, script_type, allow_move=True):
    folder_path = get_category_folder_path(new_category_name, create=True)
    raw_script_content = extract_raw_script(script_content, script_type)
    
    if old_file_path and os.path.exists(old_file_path):
        if not allow_move:
            try:
                with open(old_file_path, 'w') as f:
                    f.write(raw_script_content)
            except Exception:
                pass
            return old_file_path
        
        extension = ".mel" if script_type == "MEL" else ".py"
        base_name = sanitize_name(tool_name)
        target_path = os.path.join(folder_path, base_name + extension)
        
        already_in_place = os.path.normcase(os.path.normpath(old_file_path)) == os.path.normcase(os.path.normpath(target_path))
        
        if already_in_place:
            new_file_path = old_file_path
        else:
            new_file_path = _get_unique_file_path(folder_path, base_name, extension)
            try:
                shutil.move(old_file_path, new_file_path)
            except Exception:
                new_file_path = old_file_path
        
        try:
            with open(new_file_path, 'w') as f:
                f.write(raw_script_content)
            return new_file_path
        except Exception:
            pass
    
    return save_category_tool_file(new_category_name, tool_name, raw_script_content, script_type)


def move_category_tool_assets(tool_entry, new_category_name, allow_move=True):
    old_file_path = tool_entry.get('file_path')
    old_gif_path = tool_entry.get('tooltip_gif_path')
    old_sidecar_path = os.path.splitext(old_file_path)[0] + '.tooltip.json' if old_file_path else None
    
    new_file_path = move_category_tool_file(
        old_file_path,
        new_category_name,
        tool_entry.get('name', 'Unnamed'),
        tool_entry.get('script', ''),
        tool_entry.get('script_type', 'Python'),
        allow_move=allow_move
    )
    tool_entry['file_path'] = new_file_path
    
    if not allow_move:
        return tool_entry
    
    if old_gif_path and os.path.exists(old_gif_path):
        try:
            folder_path = get_category_folder_path(new_category_name, create=True)
            base_name = sanitize_name(tool_entry.get('name', 'Unnamed'))
            new_gif_path = os.path.join(folder_path, base_name + ".tooltip.gif")
            
            if os.path.normcase(os.path.normpath(old_gif_path)) != os.path.normcase(os.path.normpath(new_gif_path)):
                shutil.move(old_gif_path, new_gif_path)
            
            tool_entry['tooltip_gif_path'] = new_gif_path
        except Exception:
            pass
    
    if old_sidecar_path and os.path.exists(old_sidecar_path):
        try:
            os.remove(old_sidecar_path)
        except Exception:
            pass
    
    if tool_entry.get('tooltip_title') or tool_entry.get('tooltip_description') or tool_entry.get('tooltip_gif_path'):
        save_tooltip_sidecar(tool_entry)
    
    return tool_entry


def scan_tools_library():
    library_path = get_tools_library_path()
    result = {}
    
    if not os.path.exists(library_path):
        return result
    
    reserved_names = ('icons', 'animo tools')
    
    for entry in sorted(os.listdir(library_path)):
        if entry.lower() in reserved_names:
            continue
        
        folder_path = os.path.join(library_path, entry)
        if not os.path.isdir(folder_path):
            continue
        
        script_files = []
        for filename in sorted(os.listdir(folder_path)):
            file_path = os.path.join(folder_path, filename)
            if not os.path.isfile(file_path):
                continue
            
            extension = os.path.splitext(filename)[1].lower()
            if extension in ('.py', '.mel'):
                script_files.append(file_path)
        
        result[entry] = script_files
    
    return result


def get_tools_data_file():
    return os.path.join(get_animo_data_path(), "animo_tools.json")


def get_hotkeys_data_file():
    return os.path.join(get_animo_data_path(), "animo_hotkeys.json")


def save_tools_data(data):
    try:
        file_path = get_tools_data_file()
        relative_data = _convert_stored_paths(data, to_relative=True)
        with open(file_path, 'w') as f:
            json.dump(relative_data, f, indent=4)
        return True
    except Exception:
        return False


def load_tools_data():
    try:
        file_path = get_tools_data_file()
        if not os.path.exists(file_path):
            return {'custom_tools': [], 'custom_categories': []}
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        return _convert_stored_paths(data, to_relative=False)
    except Exception:
        return {'custom_tools': [], 'custom_categories': []}


def _looks_like_absolute_path(path_value):
    if not path_value:
        return False
    normalized = path_value.replace('\\', '/')
    if normalized.startswith('/'):
        return True
    if len(normalized) >= 2 and normalized[1] == ':':
        return True
    return False


def _convert_stored_paths(data, to_relative):
    tools_library_root = get_tools_library_path()
    result = json.loads(json.dumps(data))
    
    def relativize(path_value):
        if not path_value:
            return path_value
        if _looks_like_absolute_path(path_value):
            try:
                if os.path.exists(path_value):
                    rel = os.path.relpath(path_value, tools_library_root)
                    if not rel.startswith('..'):
                        return rel.replace(os.sep, '/')
            except Exception:
                pass
            return path_value
        return path_value
    
    def absolutize(path_value):
        if not path_value:
            return path_value
        if _looks_like_absolute_path(path_value):
            return path_value
        return os.path.normpath(os.path.join(tools_library_root, path_value.replace('/', os.sep)))
    
    convert = relativize if to_relative else absolutize
    
    for category in result.get('custom_categories', []):
        for entry in category.get('tools_data', []):
            if entry.get('file_path'):
                entry['file_path'] = convert(entry['file_path'])
            
            if entry.get('tooltip_gif_path'):
                if to_relative:
                    converted_gif = relativize(entry['tooltip_gif_path'])
                    if _looks_like_absolute_path(converted_gif):
                        entry['tooltip_gif_path'] = ''
                    else:
                        entry['tooltip_gif_path'] = converted_gif
                else:
                    entry['tooltip_gif_path'] = absolutize(entry['tooltip_gif_path'])
    
    return result


def get_library_order_file():
    return os.path.join(get_tools_library_path(), "library_order.json")


def save_library_order(category_order, tools_order, category_appearance=None, tools_appearance=None):
    try:
        file_path = get_library_order_file()
        order_data = {
            'category_order': category_order,
            'tools_order': tools_order,
            'category_appearance': category_appearance or {},
            'tools_appearance': tools_appearance or {}
        }
        with open(file_path, 'w') as f:
            json.dump(order_data, f, indent=4)
        return True
    except Exception:
        return False


def load_library_order():
    default_data = {
        'category_order': [],
        'tools_order': {},
        'category_appearance': {},
        'tools_appearance': {}
    }
    
    try:
        file_path = get_library_order_file()
        if not os.path.exists(file_path):
            return default_data
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for key, default_value in default_data.items():
            data.setdefault(key, default_value)
        
        return data
    except Exception:
        return default_data


def save_hotkeys_data(hotkeys_dict):
    try:
        file_path = get_hotkeys_data_file()
        with open(file_path, 'w') as f:
            json.dump(hotkeys_dict, f, indent=4)
        return True
    except Exception:
        return False


def load_hotkeys_data():
    try:
        file_path = get_hotkeys_data_file()
        if not os.path.exists(file_path):
            return {}
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def export_hotkeys(export_path, hotkeys_dict):
    try:
        with open(export_path, 'w') as f:
            json.dump(hotkeys_dict, f, indent=4)
        return True
    except Exception:
        return False


def import_hotkeys(import_path):
    try:
        if not os.path.exists(import_path):
            return None
        
        with open(import_path, 'r') as f:
            return json.load(f)
    except Exception:
        return None
