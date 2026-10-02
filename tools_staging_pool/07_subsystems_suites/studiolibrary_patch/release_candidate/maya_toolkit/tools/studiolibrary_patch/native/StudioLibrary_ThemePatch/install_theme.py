"""Guarded explicit theme install; external files cannot be Maya-undone."""
def install_theme(resource_path):
    from maya_toolkit.tools.studiolibrary_patch.theme_io import install
    return install(resource_path)
