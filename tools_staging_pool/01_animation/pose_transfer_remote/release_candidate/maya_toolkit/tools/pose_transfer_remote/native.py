from .runtime import require_scope, checked_delete, helper_name
import maya.cmds as cmds
import maya.OpenMaya as om

class PoseTransfer:

    def __init__(self):
        self.root_controller = None
        self.controllers = []
        self.locators = []
        self.original_root_pos = None

    def get_selected_root(self):
        """获取选中的ROOT控制器"""
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning('请先选择ROOT控制器')
            return False
        self.root_controller = selection[0]
        print(f'ROOT控制器已设置: {self.root_controller}')
        return True

    def get_all_controllers(self):
        """获取所有控制器 - 使用多种方法"""
        if not self.root_controller:
            cmds.warning('请先设置ROOT控制器')
            return False
        self.controllers = []
        control_set = 'ControlSet'
        if cmds.objExists(control_set):
            set_members = cmds.sets(control_set, query=True) or []
            self.controllers.extend(set_members)
            print(f'从ControlSet获取到 {len(set_members)} 个控制器')
        descendants = cmds.listRelatives(self.root_controller, allDescendents=True, type='transform') or []
        for obj in descendants:
            if self.is_controller(obj):
                if obj not in self.controllers:
                    self.controllers.append(obj)
        if self.root_controller not in self.controllers:
            self.controllers.append(self.root_controller)
        print(f'自动检测到 {len(self.controllers)} 个控制器:')
        for ctrl in self.controllers:
            print(f'  - {ctrl}')
        return True

    def is_controller(self, obj):
        """判断对象是否是控制器"""
        controller_patterns = ['_M', '_L', '_R', 'FK', 'IK', 'Ctrl', 'ctrl', 'Control', 'control']
        obj_name = obj.rsplit('|', 1)[-1].lower()
        for pattern in controller_patterns:
            if pattern.lower() in obj_name:
                return True
        if cmds.attributeQuery('overrideEnabled', node=obj, exists=True):
            if cmds.getAttr(f'{obj}.overrideEnabled'):
                return True
        shapes = cmds.listRelatives(obj, shapes=True) or []
        for shape in shapes:
            shape_type = cmds.nodeType(shape)
            if shape_type in ['nurbsCurve', 'nurbsSurface']:
                return True
        return False

    def manual_select_and_create_locators(self):
        """手动选择控制器并创建定位器"""
        if not self.root_controller:
            cmds.warning('请先设置ROOT控制器')
            return False
        result = cmds.confirmDialog(title='手动选择控制器', message='请在场景中选择所有需要的控制器，然后点击确定', button=['确定', '取消'], defaultButton='确定', cancelButton='取消', dismissString='取消')
        if result == '确定':
            selection = cmds.ls(selection=True)
            if selection:
                self.controllers = selection
                print(f'手动选择了 {len(self.controllers)} 个控制器:')
                for ctrl in self.controllers:
                    print(f'  - {ctrl}')
                return self.create_locators_and_record_pose()
            else:
                cmds.warning('没有选择任何对象')
                return False
        return False

    def create_locators_and_record_pose(self):
        """创建定位器并记录当前姿态"""
        require_scope()
        if not self.controllers:
            cmds.warning('没有找到控制器')
            return False
        if not self.root_controller:
            cmds.warning('请先设置ROOT控制器')
            return False
        self.original_root_pos = cmds.xform(self.root_controller, query=True, worldSpace=True, translation=True)
        if self.locators:
            for loc in self.locators:
                if cmds.objExists(loc):
                    checked_delete(loc)
        self.locators = []
        for i, ctrl in enumerate(self.controllers):
            if not cmds.objExists(ctrl):
                print(f'控制器 {ctrl} 不存在，跳过')
                continue
            loc_name = helper_name(ctrl, i)
            locator = cmds.spaceLocator(name=loc_name)[0]
            self.locators.append(locator)
            ctrl_matrix = cmds.xform(ctrl, query=True, worldSpace=True, matrix=True)
            cmds.xform(locator, worldSpace=True, matrix=ctrl_matrix)
            cmds.addAttr(locator, longName='original_controller', dataType='string')
            cmds.setAttr(f'{locator}.original_controller', ctrl, type='string')
        print(f'创建了 {len(self.locators)} 个定位器')
        return True

    def move_locators_to_new_root_position(self):
        """将定位器移动到新的ROOT位置"""
        require_scope()
        if not self.locators or not self.root_controller:
            cmds.warning('请先创建定位器和设置ROOT')
            return False
        current_root_pos = cmds.xform(self.root_controller, query=True, worldSpace=True, translation=True)
        offset = [current_root_pos[i] - self.original_root_pos[i] for i in range(3)]
        for locator in self.locators:
            current_pos = cmds.xform(locator, query=True, worldSpace=True, translation=True)
            new_pos = [current_pos[i] + offset[i] for i in range(3)]
            cmds.xform(locator, worldSpace=True, translation=new_pos)
        print(f'定位器已移动，偏移量: {offset}')
        self.original_root_pos = current_root_pos
        return True

    def apply_pose_from_locators(self):
        """从定位器应用姿态到控制器"""
        require_scope()
        if not self.locators:
            cmds.warning('没有找到定位器')
            return False
        for locator in self.locators:
            if not cmds.attributeQuery('original_controller', node=locator, exists=True):
                continue
            ctrl_name = cmds.getAttr(f'{locator}.original_controller')
            if not cmds.objExists(ctrl_name):
                print(f'控制器 {ctrl_name} 不存在，跳过')
                continue
            loc_matrix = cmds.xform(locator, query=True, worldSpace=True, matrix=True)
            cmds.xform(ctrl_name, worldSpace=True, matrix=loc_matrix)
        print('姿态已应用到控制器')
        return True

    def cleanup_locators(self):
        """清理定位器"""
        require_scope()
        if self.locators:
            for loc in self.locators:
                if cmds.objExists(loc):
                    checked_delete(loc)
            self.locators = []
            print('定位器已清理')

def create_pose_transfer_ui():
    window_name = 'mtkPoseTransferCandidateWindow'
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    window = cmds.window(window_name, title='姿态传输工具', widthHeight=(350, 550))
    main_layout = cmds.columnLayout(adjustableColumn=True)
    cmds.separator(height=10, style='none')
    cmds.text(label='姿态传输工具', font='boldLabelFont')
    cmds.separator(height=10)
    from .ui_bridge import SessionButtons
    pose_transfer = SessionButtons()
    cmds.checkBox('mtkPoseTransferCandidateAllowReferences', label='Allow reference edits when applying pose', value=False)
    cmds.button(label='1. 选择ROOT控制器', height=30, command=lambda x: pose_transfer.get_selected_root())
    cmds.separator(height=10)
    cmds.text(label='选择以下任一方式获取控制器:', font='boldLabelFont')
    cmds.separator(height=5, style='none')
    cmds.button(label='2a. 自动获取所有控制器', height=30, command=lambda x: pose_transfer.get_all_controllers())
    cmds.separator(height=5, style='none')
    cmds.button(label='2b. 手动选择控制器并创建定位器', height=30, command=lambda x: pose_transfer.manual_select_and_create_locators(), backgroundColor=(0.7, 0.7, 0.9))
    cmds.separator(height=5, style='none')
    cmds.button(label='3. 创建定位器并记录姿态', height=30, command=lambda x: pose_transfer.create_locators_and_record_pose())
    cmds.separator(height=10)
    cmds.text(label='移动ROOT到目标位置后:', font='boldLabelFont')
    cmds.separator(height=5, style='none')
    cmds.button(label='4. 移动定位器到新ROOT位置', height=30, command=lambda x: pose_transfer.move_locators_to_new_root_position())
    cmds.separator(height=5, style='none')
    cmds.button(label='5. 应用姿态到控制器', height=30, command=lambda x: pose_transfer.apply_pose_from_locators())
    cmds.separator(height=15)
    cmds.button(label='清理定位器', height=30, command=lambda x: pose_transfer.cleanup_locators(), backgroundColor=(0.8, 0.4, 0.4))
    cmds.separator(height=10, style='none')
    cmds.showWindow(window)
