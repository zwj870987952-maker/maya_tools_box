"""Noodle Installation Module.

Run script within Maya using the script editor.
"""

import sys

try:
    import pymel.core as pm
except ImportError:
    raise ImportError(
        "PyMel could not be imported. PyMel is required to run Noodle. To"
        " continue, install PyMel or ensure it can be located. Refer to:\n"
        " https://knowledge.autodesk.com/support/maya/learn-explore/caas/"
        "CloudHelp/cloudhelp/2022/ENU/Maya-Scripting/files/GUID-2AA5EFCE-53B1"
        "-46A0-8E43-4CD0B2C72FB4-htm.html"
    )


SCRIPT = """

from noodle import noodle

noodle.NoodleUI().show()

"""


if 'maya' in sys.executable:
    MAYA_INTERPRETER = True
else:
    MAYA_INTERPRETER = False


def get_shelf_tablayout():
    """Return main shelf's tab layout.

    Returns
    -------
    pm.ui.ShelfTabLayout
    """
    return pm.ui.ShelfTabLayout(pm.mel.eval('$tmpVar = $gShelfTopLevel'))


def get_shelves():
    """Return list of shelves on main shelf.

    Returns
    -------
    List[str]
    """
    shelf_top_level = get_shelf_tablayout()
    shelves = shelf_top_level.getChildArray()
    shelf_layouts = [
        pm.ui.ShelfLayout('|'.join([shelf_top_level, i])) for i in shelves
    ]
    return shelf_layouts


def create_shelf(tablayout):
    """Create shelf on shelf tab layout.

    Parameters
    ----------
    tablayout : pm.ui.ShelfTabLayout

    Returns
    -------
    pm.ui.ShelfLayout
    """
    shelflayout = pm.shelfLayout(COLLECTION, parent=tablayout)
    return shelflayout


def create_shelf_button(shelf, **kwargs):
    """Create shelf button on shelf.

    Parameters
    ----------
    shelf : pm.ui.ShelfLayout
    kwargs : Any

    Returns
    -------
    pm.ui.ShelfButton
    """
    shelf_button = pm.shelfButton(
        parent=shelf,
        **kwargs
    )
    return shelf_button


def install(button_kwargs):
    """Install shelf and shelf button.

    Parameters
    ----------
    button_kwargs : dict

    Returns
    -------
    Tuple[pm.ui.ShelfLayout, pm.ui.ShelfButton]
    """
    shelves = get_shelves()
    for shelf in shelves:
        if COLLECTION in str(shelf):
            target_shelf = shelf
            break
    else:
        tablayout = get_shelf_tablayout()
        target_shelf = create_shelf(tablayout)

    button = create_shelf_button(target_shelf, **button_kwargs)

    return target_shelf, button


if __name__ == '__main__' and MAYA_INTERPRETER:
    COLLECTION = 'Decogged'
    TOOL = 'Noodle'
    button_params = {
        'image1': 'noodleIcon.png',
        'style': 'iconOnly',
        'annotation': 'Launch Noodle, an auto overlap tool.',
        'label': 'Noodle',
        'command': SCRIPT,
        'sourceType': 'python',
    }
    install(button_kwargs=button_params)
