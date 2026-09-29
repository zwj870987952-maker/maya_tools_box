import maya.cmds as cmds
import maya.OpenMaya as om

class HighlightTool(object):
    def __init__(self):
        self.window_name = "highlightToolWindow"
        self.callback_ids = []
        self.previous_obj = None
        self.is_active = False
        self.active_panel = None
        
    def get_active_panel(self):
        # 获取所有模型面板
        model_panels = cmds.getPanel(type='modelPanel')
        
        # 首先检查当前焦点面板
        focused_panel = cmds.getPanel(withFocus=True)
        if focused_panel in model_panels:
            return focused_panel
            
        # 如果当前焦点不是模型面板，则获取第一个可见的模型面板
        for panel in model_panels:
            if cmds.modelEditor(panel, query=True, activeView=True):
                return panel
                
        # 如果没有找到活动的面板，返回第一个模型面板
        return model_panels[0] if model_panels else None

    def create_ui(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        window = cmds.window(self.window_name, title="Highlight Tool", widthHeight=(200, 100))
        cmds.columnLayout(adjustableColumn=True)
        
        self.toggle_button = cmds.button(
            label="Start Tool", 
            command=self.toggle_tool,
            backgroundColor=[0.2, 0.6, 0.2]
        )
        cmds.showWindow(window)
        
    def toggle_tool(self, *args):
        if not self.is_active:
            self.start_tool()
        else:
            self.stop_tool()
            
    def start_tool(self):
        # 获取并存储当前活动面板
        self.active_panel = self.get_active_panel()
        if not self.active_panel:
            cmds.warning("No active model panel found!")
            return
            
        self.is_active = True
        cmds.button(
            self.toggle_button, 
            edit=True, 
            label="Stop Tool",
            backgroundColor=[0.6, 0.2, 0.2]
        )
        
        # 存储面板原始的选择高亮状态
        self.original_sel_state = cmds.modelEditor(self.active_panel, query=True, sel=True)
        
        self.setup_tool()
        
    def stop_tool(self):
        self.is_active = False
        cmds.button(
            self.toggle_button, 
            edit=True, 
            label="Start Tool",
            backgroundColor=[0.2, 0.6, 0.2]
        )
        self.close_tool()
        
    def setup_tool(self):
        if not self.active_panel:
            return
            
        # 关闭选择高亮
        cmds.modelEditor(self.active_panel, edit=True, sel=False)
        
        # 切换到面选择模式
        cmds.selectMode(component=True)
        cmds.selectType(facet=True)
        
        # 添加选择改变回调
        self.callback_ids.append(om.MEventMessage.addEventCallback("SelectionChanged", self.selection_changed))
        
    def selection_changed(self, *args):
        if not self.is_active:
            return
            
        selection = cmds.ls(selection=True, flatten=True)
        
        if self.previous_obj:
            try:
                # 移除之前物体的覆盖
                shapes = cmds.listRelatives(self.previous_obj, shapes=True) or []
                for shape in shapes:
                    cmds.setAttr(f"{shape}.overrideEnabled", 0)
                    cmds.setAttr(f"{shape}.overrideShading", 1)
            except:
                pass
        
        if selection:
            current_obj = selection[0].split('.')[0]
            
            if current_obj != self.previous_obj:
                try:
                    # 为当前物体设置覆盖
                    shapes = cmds.listRelatives(current_obj, shapes=True) or []
                    for shape in shapes:
                        cmds.setAttr(f"{shape}.overrideEnabled", 1)
                        cmds.setAttr(f"{shape}.overrideShading", 0)
                    self.previous_obj = current_obj
                except:
                    pass
        else:
            self.previous_obj = None
            
    def close_tool(self, *args):
        if self.active_panel:
            # 恢复面板原始的选择高亮状态
            try:
                cmds.modelEditor(self.active_panel, edit=True, sel=self.original_sel_state)
            except:
                pass
        
        cmds.selectMode(object=True)
        
        for callback_id in self.callback_ids:
            om.MMessage.removeCallback(callback_id)
        self.callback_ids = []
        
        if self.previous_obj:
            try:
                shapes = cmds.listRelatives(self.previous_obj, shapes=True) or []
                for shape in shapes:
                    cmds.setAttr(f"{shape}.overrideEnabled", 0)
                    cmds.setAttr(f"{shape}.overrideShading", 1)
            except:
                pass
            self.previous_obj = None
        
        self.active_panel = None

# 创建工具实例并显示UI
if __name__ == "__main__":
    tool = HighlightTool()
    tool.create_ui()
