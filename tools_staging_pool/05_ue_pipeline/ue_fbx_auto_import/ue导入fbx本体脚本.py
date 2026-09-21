import unreal
import os
import json
import glob

def set_property_safe(obj, property_name, value):
    """
    Safely set a property on an object, skipping if the property does not exist.
    """
    try:
        obj.set_editor_property(property_name, value)
    except Exception as e:
        unreal.log_warning(f"Property '{property_name}' not found on {obj}: {e}")

def get_import_options(skeleton_path):
    """
    Create and configure FbxImportUI for importing animations.
    """
    options = unreal.FbxImportUI()
    options.reset_to_default()

    options.automated_import_should_detect_type = False
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION

    skeleton = unreal.load_asset(skeleton_path)
    if not skeleton:
        unreal.log_error(f"Failed to load skeleton at path: {skeleton_path}")
        return None

    options.set_editor_property('skeleton', skeleton)
    options.set_editor_property('import_animations', True)

    anim_sequence_import_data = options.anim_sequence_import_data
    set_property_safe(anim_sequence_import_data, 'animation_length', unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)

    options.set_editor_property('import_mesh', False)

    set_property_safe(options.static_mesh_import_data, 'import_as_skeletal', True)
    set_property_safe(options.static_mesh_import_data, 'update_skeleton_reference_pose', True)
    set_property_safe(options.static_mesh_import_data, 'use_t0_as_reference_pose', True)
    set_property_safe(options.static_mesh_import_data, 'import_morph_targets', True)
    set_property_safe(options.static_mesh_import_data, 'normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)

    set_property_safe(options.static_mesh_import_data, 'import_materials', True)
    set_property_safe(options.static_mesh_import_data, 'import_textures', True)

    return options

def import_fbx_files(fbx_files, destination_content_path, skeleton_path):
    unreal.log(f"Importing FBX files to {destination_content_path}")

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    import_options = get_import_options(skeleton_path)
    if not import_options:
        unreal.log_error("Import options could not be created due to skeleton loading failure.")
        return

    for fbx_file in fbx_files:
        unreal.log(f"Importing file: {fbx_file}")

        task = unreal.AssetImportTask()
        task.set_editor_property('filename', fbx_file)
        task.set_editor_property('destination_path', destination_content_path)
        task.set_editor_property('replace_existing', False)
        task.set_editor_property('save', True)
        task.set_editor_property('automated', True)
        task.set_editor_property('options', import_options)

        asset_tools.import_asset_tasks([task])

        if task.imported_object_paths:
            unreal.log(f"Successfully imported: {fbx_file}")
        else:
            unreal.log_error(f"Failed to import: {fbx_file}")

def load_config(config_file_path):
    """
    Load configuration from a JSON file using UTF-8 encoding.
    """
    try:
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)
    except Exception as e:
        unreal.log_error(f"Failed to load config file {config_file_path}: {e}")
        return None

def process_all_configs(config_directory):
    """
    Process all JSON configuration files in the specified directory.
    """
    config_files = glob.glob(os.path.join(config_directory, "*.json"))

    for config_file_path in config_files:
        unreal.log(f"Processing config file: {config_file_path}")

        config = load_config(config_file_path)

        if config:
            fbx_files = config.get("fbx_files", [])
            destination_content_path = config.get("destination_content_path", "")
            skeleton_path = config.get("skeleton_path", "")

            if fbx_files:
                import_fbx_files(fbx_files, destination_content_path, skeleton_path)
            else:
                unreal.log_error(f"No FBX files specified for import in config file: {config_file_path}")
        else:
            unreal.log_error(f"Configuration could not be loaded from {config_file_path}. Please check the config file.")

# Determine the directory of the current script
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# Process all configuration files in the current script's directory
process_all_configs(current_script_dir)