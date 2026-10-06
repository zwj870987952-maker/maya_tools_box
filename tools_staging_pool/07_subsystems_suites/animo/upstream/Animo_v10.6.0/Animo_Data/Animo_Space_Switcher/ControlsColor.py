from maya import cmds

def get_esn_ctrls():
    selection = []
    set_name = "esn_ctrls_set"
    
    if cmds.objExists(set_name):
        try:
            set_members = cmds.sets(set_name, query=True)
            if set_members:
                for member in set_members:
                    if cmds.objExists(member):
                        obj_type = cmds.objectType(member)
                        if obj_type == 'transform':
                            selection.append(member)
        except:
            pass
    
    if not selection:
        all_objects = cmds.ls(long=True)
        for obj in all_objects:
            try:
                if cmds.objectType(obj) == 'transform':
                    full_path = obj
                    if '_esn_ctrl' in full_path or '_PIPE_' in full_path:
                        selection.append(obj)
            except:
                continue
    
    return selection

def show_nurbs_curves_in_all_viewports():
    all_panels = cmds.getPanel(type='modelPanel')
    for panel in all_panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            editor = cmds.modelPanel(panel, query=True, modelEditor=True)
            cmds.modelEditor(editor, edit=True, nurbsCurves=True)
            cmds.modelEditor(panel, edit=True, controllers=True)

def turn_off_selection_highlighting():
    all_panels = cmds.getPanel(type='modelPanel')
    for panel in all_panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            cmds.modelEditor(panel, edit=True, selectionHiliteDisplay=False)

def turn_on_selection_highlighting():
    all_panels = cmds.getPanel(type='modelPanel')
    for panel in all_panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            cmds.modelEditor(panel, edit=True, selectionHiliteDisplay=True)

def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = v - c
    
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    
    return (r + m, g + m, b + m)

def apply_color_to_controls(rgb):
    """Apply RGB color to selected controls or esn_ctrls"""
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        selection = get_esn_ctrls()
    
    if not selection:
        return
    
    valid_objects = []
    for obj in selection:
        if not cmds.objExists(obj):
            continue
        try:
            obj_type = cmds.objectType(obj)
        except:
            continue
        if obj_type != 'transform':
            continue
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
        if not shapes:
            continue
        has_valid_shape = False
        for shape in shapes:
            try:
                node_type = cmds.nodeType(shape)
                if node_type in ["nurbsCurve", "locator"]:
                    has_valid_shape = True
                    break
            except:
                continue
        if has_valid_shape:
            valid_objects.append(obj)
    
    if valid_objects:
        show_nurbs_curves_in_all_viewports()
        turn_off_selection_highlighting()
        for obj in valid_objects:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            for shape in shapes:
                try:
                    cmds.setAttr(shape + ".overrideEnabled", 1)
                    cmds.setAttr(shape + ".overrideRGBColors", 1)
                    cmds.setAttr(shape + ".overrideColorRGB", rgb[0], rgb[1], rgb[2])
                except:
                    pass
        cmds.scriptJob(runOnce=True, killWithScene=True, event=["SelectionChanged", turn_on_selection_highlighting])

class ColorPickerTool:
    def __init__(self):
        self.winName = "colorPickerWin"
        self.width = 500
        self.height = 120
    
    def show(self):
        if cmds.window(self.winName, exists=True):
            cmds.deleteUI(self.winName)
        
        self.window = cmds.window(self.winName, title="Color Picker", 
                                 widthHeight=(self.width, self.height),
                                 sizeable=True)
        
        mainLayout = cmds.columnLayout(adjustableColumn=True, parent=self.window)
        
        cmds.text(label="Color Picker", font="boldLabelFont", height=30)
        
        cmds.separator(height=10, style='none')
        
        rowLayout = cmds.rowLayout(numberOfColumns=2, parent=mainLayout, columnWidth2=(350, 150))
        
        self.colorSlider = cmds.colorSliderGrp(label='Color', 
                                               rgb=(1, 0, 0),
                                               columnWidth=[(1, 50), (2, 250)],
                                               changeCommand=self.applyColorFromSlider,
                                               parent=rowLayout)
        
        self.hueSlider = cmds.floatSliderGrp(label='', 
                                             field=False,
                                             minValue=0.0,
                                             maxValue=360.0,
                                             value=0.0,
                                             columnWidth=[(1, 0), (2, 150)],
                                             changeCommand=self.applyColorFromHue,
                                             dragCommand=self.applyColorFromHue,
                                             parent=rowLayout)
        
        cmds.showWindow(self.window)
        
        try:
            colorSliderChildren = cmds.colorSliderGrp(self.colorSlider, query=True, fullPathName=True)
            sliders = cmds.layout(colorSliderChildren, query=True, childArray=True) or []
            for child in sliders:
                fullPath = colorSliderChildren + '|' + child
                if cmds.colorSliderGrp(fullPath, exists=True):
                    continue
                try:
                    if 'slider' in child.lower():
                        cmds.control(fullPath, edit=True, manage=False)
                except:
                    pass
        except:
            pass
    
    def getTargetObjects(self):
        selection = cmds.ls(selection=True, long=True)
        
        if not selection:
            selection = get_esn_ctrls()
        
        if not selection:
            return []
        
        valid_objects = []
        
        for obj in selection:
            if not cmds.objExists(obj):
                continue
            
            try:
                obj_type = cmds.objectType(obj)
            except:
                continue
            
            if obj_type != 'transform':
                continue
            
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
            if not shapes:
                continue
            
            has_valid_shape = False
            for shape in shapes:
                try:
                    node_type = cmds.nodeType(shape)
                    if node_type in ["nurbsCurve", "locator"]:
                        has_valid_shape = True
                        break
                except:
                    continue
            
            if has_valid_shape:
                valid_objects.append(obj)
        
        return valid_objects
    
    def applyColorFromSlider(self, *args):
        rgb = cmds.colorSliderGrp(self.colorSlider, query=True, rgbValue=True)
        self.applyColorToObjects(rgb)
    
    def applyColorFromHue(self, *args):
        hue = cmds.floatSliderGrp(self.hueSlider, query=True, value=True)
        rgb = hsv_to_rgb(hue, 1.0, 1.0)
        self.applyColorToObjects(rgb)
    
    def applyColorToObjects(self, rgb):
        apply_color_to_controls(rgb)

_colorPickerTool = None

def show():
    global _colorPickerTool
    _colorPickerTool = ColorPickerTool()
    _colorPickerTool.show()