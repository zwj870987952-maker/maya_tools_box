from .proxy import cmds
from . import runtime as _r
'\nMaya脚本: 动画万向锁修复工具\n功能: 修复现有动画曲线中因欧拉角万向锁问题而产生的异常\n作者: Claude\n'
import maya.OpenMaya as om
import math

class GimbalLockFixer(object):
    """
    万向锁修复工具类
    用于修复动画曲线中因万向锁问题导致的旋转异常
    """

    def __init__(self):
        """初始化修复工具"""
        self.time_range = None
        self.frame_rate = 24
        self.smooth_factor = 1.0
        self.preserve_keys = True
        self.create_new_curves = False

    def euler_to_quaternion(self, x, y, z, rotation_order='xyz'):
        """将欧拉角转换为四元数"""
        x_rad = math.radians(x)
        y_rad = math.radians(y)
        z_rad = math.radians(z)
        euler = om.MEulerRotation(x_rad, y_rad, z_rad)
        order_dict = {'xyz': om.MEulerRotation.kXYZ, 'xzy': om.MEulerRotation.kXZY, 'yxz': om.MEulerRotation.kYXZ, 'yzx': om.MEulerRotation.kYZX, 'zxy': om.MEulerRotation.kZXY, 'zyx': om.MEulerRotation.kZYX}
        euler.order = order_dict.get(rotation_order.lower(), om.MEulerRotation.kXYZ)
        quat = euler.asQuaternion()
        return quat

    def quaternion_to_euler(self, quat, rotation_order='xyz'):
        """将四元数转换为欧拉角"""
        euler = om.MEulerRotation()
        order_dict = {'xyz': om.MEulerRotation.kXYZ, 'xzy': om.MEulerRotation.kXZY, 'yxz': om.MEulerRotation.kYXZ, 'yzx': om.MEulerRotation.kYZX, 'zxy': om.MEulerRotation.kZXY, 'zyx': om.MEulerRotation.kZYX}
        euler = quat.asEulerRotation()
        euler.reorderIt(order_dict.get(rotation_order.lower(), om.MEulerRotation.kXYZ))
        return [math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z)]

    def quaternion_slerp(self, quat1, quat2, t):
        """
        四元数球面线性插值
        quat1, quat2: 起始和结束四元数
        t: 插值参数 (0-1)
        """
        quat2 = om.MQuaternion(quat2)
        dot = quat1.x * quat2.x + quat1.y * quat2.y + quat1.z * quat2.z + quat1.w * quat2.w
        if dot < 0:
            quat2.x = -quat2.x
            quat2.y = -quat2.y
            quat2.z = -quat2.z
            quat2.w = -quat2.w
            dot = -dot
        if dot > 0.9995:
            result = om.MQuaternion(quat1.x * (1 - t) + quat2.x * t, quat1.y * (1 - t) + quat2.y * t, quat1.z * (1 - t) + quat2.z * t, quat1.w * (1 - t) + quat2.w * t)
            result.normalizeIt()
            return result
        theta_0 = math.acos(dot)
        theta = theta_0 * t
        sin_theta = math.sin(theta)
        sin_theta_0 = math.sin(theta_0)
        s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
        s1 = sin_theta / sin_theta_0
        result = om.MQuaternion(quat1.x * s0 + quat2.x * s1, quat1.y * s0 + quat2.y * s1, quat1.z * s0 + quat2.z * s1, quat1.w * s0 + quat2.w * s1)
        return result

    def get_animation_data(self, obj):
        """
        获取对象的动画数据
        返回关键帧时间和对应的旋转值
        """
        rotate_x_curve = cmds.listConnections(obj + '.rotateX', type='animCurve', source=True)
        rotate_y_curve = cmds.listConnections(obj + '.rotateY', type='animCurve', source=True)
        rotate_z_curve = cmds.listConnections(obj + '.rotateZ', type='animCurve', source=True)
        if not (rotate_x_curve and rotate_y_curve and rotate_z_curve):
            return (None, None, None)
        x_times = cmds.keyframe(rotate_x_curve, query=True, timeChange=True)
        y_times = cmds.keyframe(rotate_y_curve, query=True, timeChange=True)
        z_times = cmds.keyframe(rotate_z_curve, query=True, timeChange=True)
        all_times = sorted(list(set(x_times + y_times + z_times)))
        rotation_order = cmds.getAttr(obj + '.rotateOrder')
        rotation_order_names = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
        rotation_order_name = rotation_order_names[rotation_order]
        rotations = []
        for t in all_times:
            rot = cmds.getAttr(obj + '.rotate', time=t)[0]
            rotations.append(rot)
        return (all_times, rotations, rotation_order_name)

    def detect_gimbal_issues(self, obj, threshold=45.0):
        """
        检测动画曲线中可能存在的万向锁问题
        threshold: 角度变化阈值（度/帧）
        返回可能存在问题的帧范围列表
        """
        times, rotations, rotation_order = self.get_animation_data(obj)
        if not times or len(times) < 2:
            return []
        problem_ranges = []
        start_problem = None
        for i in range(1, len(times)):
            prev_rot = rotations[i - 1]
            curr_rot = rotations[i]
            prev_quat = self.euler_to_quaternion(prev_rot[0], prev_rot[1], prev_rot[2], rotation_order)
            curr_quat = self.euler_to_quaternion(curr_rot[0], curr_rot[1], curr_rot[2], rotation_order)
            angle_diff = _r.shortest_angle(prev_quat, curr_quat) * 180.0 / math.pi
            frame_diff = times[i] - times[i - 1]
            if angle_diff / frame_diff > threshold:
                if start_problem is None:
                    start_problem = times[i - 1]
            elif start_problem is not None:
                problem_ranges.append((start_problem, times[i - 1]))
                start_problem = None
        if start_problem is not None:
            problem_ranges.append((start_problem, times[-1]))
        return problem_ranges

    def fix_animation_curves(self, obj, start_frame=None, end_frame=None, samples_per_frame=1):
        """
        修复对象的动画曲线
        obj: 要修复的对象
        start_frame, end_frame: 要修复的帧范围，如果为None则使用整个动画范围
        samples_per_frame: 每帧的采样数，增加可提高精度
        """
        times, rotations, rotation_order = self.get_animation_data(obj)
        if not times:
            cmds.warning(f'对象 {obj} 没有动画曲线')
            return False
        if start_frame is None:
            start_frame = times[0]
        if end_frame is None:
            end_frame = times[-1]
        frame_quats = {}
        for i, t in enumerate(times):
            if start_frame <= t <= end_frame:
                rot = rotations[i]
                quat = self.euler_to_quaternion(rot[0], rot[1], rot[2], rotation_order)
                frame_quats[t] = quat
        if not frame_quats:
            cmds.warning(f'指定范围 {start_frame}-{end_frame} 内没有关键帧')
            return False
        new_times = []
        for t in times:
            if start_frame <= t <= end_frame:
                new_times.append(t)
        if samples_per_frame > 1 and len(new_times) > 1:
            extra_times = []
            for i in range(len(new_times) - 1):
                t1 = new_times[i]
                t2 = new_times[i + 1]
                frame_diff = t2 - t1
                if frame_diff > 1.0:
                    samples = int(frame_diff * samples_per_frame)
                    for j in range(1, samples):
                        extra_times.append(t1 + j * frame_diff / samples)
            new_times.extend(extra_times)
            new_times.sort()
        interp_quats = {}
        key_times = sorted(frame_quats.keys())
        for t in new_times:
            if t in frame_quats:
                interp_quats[t] = frame_quats[t]
                continue
            prev_time = None
            next_time = None
            for kt in key_times:
                if kt < t:
                    prev_time = kt
                elif kt > t:
                    next_time = kt
                    break
            if prev_time is None or next_time is None:
                continue
            time_range = next_time - prev_time
            if time_range <= 0:
                continue
            blend = (t - prev_time) / time_range
            prev_quat = frame_quats[prev_time]
            next_quat = frame_quats[next_time]
            interp_quat = self.quaternion_slerp(prev_quat, next_quat, blend)
            interp_quats[t] = interp_quat
        fixed_rotations = {}
        for t, quat in interp_quats.items():
            euler = self.quaternion_to_euler(quat, rotation_order)
            fixed_rotations[t] = euler
        self._apply_fixed_rotations(obj, fixed_rotations, rotation_order)
        return True

    def _apply_fixed_rotations(self, obj, fixed_rotations, rotation_order):
        """
        将修复后的旋转值应用到对象的动画曲线
        """
        _r.require_active()
        rotate_x_curve = cmds.listConnections(obj + '.rotateX', type='animCurve', source=True, destination=False)
        rotate_y_curve = cmds.listConnections(obj + '.rotateY', type='animCurve', source=True, destination=False)
        rotate_z_curve = cmds.listConnections(obj + '.rotateZ', type='animCurve', source=True, destination=False)
        if not rotate_x_curve:
            rotate_x_curve = [cmds.createNode('animCurveTA', name=obj + '_rotateX')]
            cmds.connectAttr(rotate_x_curve[0] + '.output', obj + '.rotateX')
        if not rotate_y_curve:
            rotate_y_curve = [cmds.createNode('animCurveTA', name=obj + '_rotateY')]
            cmds.connectAttr(rotate_y_curve[0] + '.output', obj + '.rotateY')
        if not rotate_z_curve:
            rotate_z_curve = [cmds.createNode('animCurveTA', name=obj + '_rotateZ')]
            cmds.connectAttr(rotate_z_curve[0] + '.output', obj + '.rotateZ')
        for time, rotation in fixed_rotations.items():
            cmds.setKeyframe(rotate_x_curve[0], time=time, value=rotation[0])
            cmds.setKeyframe(rotate_y_curve[0], time=time, value=rotation[1])
            cmds.setKeyframe(rotate_z_curve[0], time=time, value=rotation[2])
        cmds.keyTangent(rotate_x_curve[0], edit=True, inTangentType='spline', outTangentType='spline')
        cmds.keyTangent(rotate_y_curve[0], edit=True, inTangentType='spline', outTangentType='spline')
        cmds.keyTangent(rotate_z_curve[0], edit=True, inTangentType='spline', outTangentType='spline')

def create_gimbal_fix_ui():
    """创建万向锁修复工具的用户界面"""
    if cmds.window('mtbGimbalFixerUI', exists=True):
        cmds.deleteUI('mtbGimbalFixerUI')
    fixer = GimbalLockFixer()
    window = cmds.window('mtbGimbalFixerUI', title='动画万向锁修复工具', width=400)
    main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=['both', 10])
    cmds.text(label='动画万向锁修复工具', font='boldLabelFont')
    cmds.separator()
    cmds.frameLayout(label='对象选择', collapsable=True, collapse=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.text(label='选择要修复动画的对象，然后点击检测按钮')
    selected_objects_text = cmds.textFieldButtonGrp(label='选中的对象:', buttonLabel='<<', buttonCommand=lambda: update_selected_objects())
    cmds.button(label='检测万向锁问题', command=lambda x: detect_gimbal_issues())
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.frameLayout(label='时间范围', collapsable=True, collapse=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    time_range_radio = cmds.radioButtonGrp(label='时间范围:', labelArray3=['播放范围（原行为）', '动画范围（原行为）', '自定义'], numberOfRadioButtons=3, select=1, onCommand1=lambda: disable_custom_range(True), onCommand2=lambda: disable_custom_range(True), onCommand3=lambda: disable_custom_range(False))
    custom_range_layout = cmds.rowLayout(numberOfColumns=4, adjustableColumn=4)
    cmds.text(label='开始帧:')
    start_frame = cmds.floatField(value=0.0, precision=1, enable=False)
    cmds.text(label='结束帧:')
    end_frame = cmds.floatField(value=10.0, precision=1, enable=False)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.frameLayout(label='修复选项', collapsable=True, collapse=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    samples_per_frame = cmds.intSliderGrp(label='采样密度:', field=True, minValue=1, maxValue=10, fieldMinValue=1, fieldMaxValue=100, value=1)
    preserve_keys = cmds.checkBoxGrp(label='保留键时间（原选项未实现）:', value1=True, enable=False)
    cmds.button(label='修复动画', command=lambda x: fix_animation())
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.frameLayout(label='帮助信息', collapsable=True, collapse=True)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    cmds.text(label='这个工具用于修复动画曲线中因欧拉角万向锁问题导致的旋转异常。', align='left', wordWrap=True)
    cmds.text(label='1. 选择要修复的对象', align='left', wordWrap=True)
    cmds.text(label="2. 点击'检测万向锁问题'按钮识别可能存在问题的帧范围", align='left', wordWrap=True)
    cmds.text(label='3. 设置要修复的时间范围', align='left', wordWrap=True)
    cmds.text(label='4. 调整修复选项', align='left', wordWrap=True)
    cmds.text(label="5. 点击'修复动画'按钮应用修复", align='left', wordWrap=True)
    cmds.text(label='注意：修复过程会使用四元数插值替换原有的欧拉角插值，可能会略微改变动画曲线的形状，需要视窗逐帧复验，不能保证消除所有万向锁。', align='left', wordWrap=True)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.showWindow(window)

    def update_selected_objects():
        """更新选中的对象"""
        selected = cmds.ls(selection=True)
        if selected:
            cmds.textFieldButtonGrp(selected_objects_text, edit=True, text=', '.join(selected))
        else:
            cmds.textFieldButtonGrp(selected_objects_text, edit=True, text='')

    def disable_custom_range(disabled):
        """启用或禁用自定义范围输入"""
        cmds.floatField(start_frame, edit=True, enable=not disabled)
        cmds.floatField(end_frame, edit=True, enable=not disabled)

    def get_time_range():
        """获取时间范围"""
        range_option = cmds.radioButtonGrp(time_range_radio, query=True, select=True)
        if range_option == 1:
            start = cmds.playbackOptions(query=True, minTime=True)
            end = cmds.playbackOptions(query=True, maxTime=True)
        elif range_option == 2:
            start = cmds.playbackOptions(query=True, animationStartTime=True)
            end = cmds.playbackOptions(query=True, animationEndTime=True)
        else:
            start = cmds.floatField(start_frame, query=True, value=True)
            end = cmds.floatField(end_frame, query=True, value=True)
        return (start, end)

    def detect_gimbal_issues():
        """检测万向锁问题"""
        obj_text = cmds.textFieldButtonGrp(selected_objects_text, query=True, text=True)
        if not obj_text:
            cmds.warning('请先选择至少一个对象')
            return
        objects = [obj.strip() for obj in obj_text.split(',')]
        for obj in objects:
            if not cmds.objExists(obj):
                cmds.warning(f'对象 {obj} 不存在')
                continue
            problem_ranges = fixer.detect_gimbal_issues(obj)
            if not problem_ranges:
                cmds.confirmDialog(title='检测结果', message=f'对象 {obj} 未检测到明显的万向锁问题', button=['确定'])
            else:
                ranges_text = '\n'.join([f'帧 {start} - {end}' for start, end in problem_ranges])
                result = cmds.confirmDialog(title='检测结果', message=f'对象 {obj} 在以下帧范围可能存在万向锁问题:\n\n{ranges_text}\n\n是否要修复这些范围?', button=['修复全部', '取消'], defaultButton='修复全部', cancelButton='取消')
                if result == '修复全部':
                    start = problem_ranges[0][0]
                    end = problem_ranges[-1][1]
                    cmds.radioButtonGrp(time_range_radio, edit=True, select=3)
                    disable_custom_range(False)
                    cmds.floatField(start_frame, edit=True, value=start)
                    cmds.floatField(end_frame, edit=True, value=end)

    def fix_animation():
        """修复动画"""
        obj_text = cmds.textFieldButtonGrp(selected_objects_text, query=True, text=True)
        if not obj_text:
            cmds.warning('请先选择至少一个对象')
            return
        objects = [obj.strip() for obj in obj_text.split(',')]
        start, end = get_time_range()
        samples = cmds.intSliderGrp(samples_per_frame, query=True, value=True)
        success_count = 0
        for obj in objects:
            if not cmds.objExists(obj):
                cmds.warning(f'对象 {obj} 不存在')
                continue
            if fixer.fix_animation_curves(obj, start, end, samples):
                success_count += 1
        if success_count > 0:
            cmds.confirmDialog(title='修复完成', message=f'成功修复了 {success_count} 个对象的动画曲线', button=['确定'])
_Algorithm = GimbalLockFixer

class GimbalLockFixer(_Algorithm):

    def detect_gimbal_issues(self, obj, threshold=45.0):
        from .tool import GimbalFixTool
        result = GimbalFixTool().run(action='detect', objects=[obj], threshold=threshold)
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['results'][0]['problem_ranges']

    def fix_animation_curves(self, obj, start_frame=None, end_frame=None, samples_per_frame=1):
        from .tool import GimbalFixTool
        result = GimbalFixTool().run(action='fix', objects=[obj], start=start_frame, end=end_frame, samples_per_frame=samples_per_frame)
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['results'][0]['fixed']
