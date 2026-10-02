"""Guarded explicit theme uninstall; external files cannot be Maya-undone."""
def uninstall_theme(resource_path):
    from maya_toolkit.tools.studiolibrary_patch.theme_io import uninstall
    return uninstall(resource_path)
