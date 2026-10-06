from maya import OpenMayaUI as omui
import maya.mel as mel

try:
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance

# Module-level variable to store timeline height
STORED_TIMELINE_HEIGHT = None


def queryTimelineHeight():
    global STORED_TIMELINE_HEIGHT
    
    try:
        time_slider_name = mel.eval('$tmpVar=$gPlayBackSlider')
        ptr = omui.MQtUtil.findControl(time_slider_name)
        if not ptr:
            return None
        
        time_slider = wrapInstance(int(ptr), QtWidgets.QWidget)
    except:
        return None
    
    current = time_slider
    for _ in range(20):
        if not current:
            break
        
        parent = current.parent()
        if parent and parent.__class__.__name__ == 'QSplitter':
            splitter = parent
            idx = splitter.indexOf(current)
            
            if idx >= 0:
                sizes = splitter.sizes()
                STORED_TIMELINE_HEIGHT = sizes[idx]
                return STORED_TIMELINE_HEIGHT
        
        current = parent
    
    return None
