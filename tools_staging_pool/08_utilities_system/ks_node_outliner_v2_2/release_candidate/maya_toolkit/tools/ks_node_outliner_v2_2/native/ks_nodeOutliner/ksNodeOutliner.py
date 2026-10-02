from __future__ import absolute_import
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtCore

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya import OpenMayaUI as omui
from maya_toolkit.tools.ks_node_outliner_v2_2.session import cmdshim as cmds

from ks_nodeOutliner.lib import GUI_NodeOutliner

__WINDOW_NAME__ = 'KS Node Outliner'
__WORKSPACE_NAME__ = 'MTB_KS_NodeOutliner'
__NODEOUTLINER__ = None

if not __WINDOW_NAME__ in globals():
    customMixinWindow = None

# ---------------------------------------------------------#
#           MAYA 2016+ GUI SETUP
# ---------------------------------------------------------#


class maya_dockableGUI(MayaQWidgetDockableMixin, GUI_NodeOutliner.GUI_NodeOutliner):
    def __init__(self, parent=None):
        super(maya_dockableGUI, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(__WINDOW_NAME__)
        self.setObjectName(__WORKSPACE_NAME__)


def maya_openDockableGUI(restore=False):
    customMixinWindow = maya_dockableGUI()

    global __NODEOUTLINER__
    __NODEOUTLINER__ = customMixinWindow

    if restore is True:
        restoredControl = omui.MQtUtil.getCurrentParent()
        mixinPtr = omui.MQtUtil.findControl(customMixinWindow.objectName())
        omui.MQtUtil.addWidgetToMayaLayout(int(mixinPtr), int(restoredControl))
    else:
        uiScript = 'from ks_nodeOutliner import ksNodeOutliner\nksNodeOutliner.maya_openDockableGUI(restore=True)'
        customMixinWindow.show(dockable=True, checksPlugins=True,
                               loadImmediately=False, collapse=True, uiScript=uiScript)


def OpenNodeOutliner():
    from maya_toolkit.tools.ks_node_outliner_v2_2 import session
    if session.config_path is None:raise RuntimeError("Select independent config via candidate show_ui first")
    return session.show(str(session.config_path))

def setCustomOutput(nodeList, ignoreHierarchy=False):
    outliner = __NODEOUTLINER__.allOutliners[0]
    outliner.setFilter_customOutput(nodeList, ignoreHierarchy)
