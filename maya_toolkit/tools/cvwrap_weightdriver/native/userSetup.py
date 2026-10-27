from maya import cmds
from pymel import mayautils

def mGear_menu_loader():
    """Create mGear menu"""
    import mgear
    mgear.install()
    import mgear.core.dagmenu
    mgear.core.dagmenu.install()
    import mgear.shifter.menu
    mgear.shifter.menu.install()
    import mgear.simpleRig.menu
    mgear.simpleRig.menu.install()
    import mgear.core.menu
    mgear.core.menu.install_skinning_menu()
    import mgear.rigbits.menu
    mgear.rigbits.menu.install()
    import mgear.animbits.menu
    mgear.animbits.menu.install()
    import mgear.cfxbits.menu
    mgear.cfxbits.menu.install()
    import mgear.crank.menu
    mgear.crank.menu.install()
    import mgear.anim_picker.menu
    mgear.anim_picker.menu.install()
    import mgear.synoptic.menu
    mgear.synoptic.menu.install()
    import mgear.flex.menu
    mgear.flex.menu.install()
    import mgear.menu
    m = mgear.menu.install_utils_menu()
    mgear.core.menu.install_utils_menu(m)
    mgear.rigbits.menu.install_utils_menu(m)
    import mgear.core.dragdrop
    mgear.core.dragdrop.install_utils_menu(m)
    mgear.menu.install_help_menu()
