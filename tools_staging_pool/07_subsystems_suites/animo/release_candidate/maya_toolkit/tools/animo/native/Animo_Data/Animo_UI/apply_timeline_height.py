from maya import OpenMayaUI as omui
import maya.mel as mel

try:
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance

try:
    from . import get_timeline_height
except ImportError:
    import get_timeline_height

HEIGHT_OFFSET = 45


def applyTimelineHeight():
    # Get stored height from the get_timeline_height module
    stored_height = getattr(get_timeline_height, 'STORED_TIMELINE_HEIGHT', None)
    
    if stored_height is None:
        return False
    
    target_height = stored_height + HEIGHT_OFFSET
    
    try:
        time_slider_name = mel.eval('$tmpVar=$gPlayBackSlider')
        ptr = omui.MQtUtil.findControl(time_slider_name)
        if not ptr:
            return False
        
        time_slider = wrapInstance(int(ptr), QtWidgets.QWidget)
    except:
        return False
    
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
                current_size = sizes[idx]
                
                if current_size != target_height:
                    difference = current_size - target_height
                    
                    if idx > 0:
                        sizes[idx - 1] += difference
                    
                    sizes[idx] = target_height
                    splitter.setSizes(sizes)
                
                return True
        
        current = parent
    
    return False
