# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import maya.cmds as cmds
import maya.api.OpenMaya as om
import math
import sys

# Python 2/3 兼容
if sys.version_info[0] >= 3:
    unicode = str
    xrange = range

# ----------------------- 辅助向量运算函数 -----------------------

def vector_length(v):
    """计算向量长度"""
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def is_close_to_zero(value, tolerance=1e-9):
    """检查数值是否接近零"""
    return abs(value) < tolerance

def normalize_vector(v):
    """归一化向量"""
    length = vector_length(v)
    if length > 0:
        return [v[0]/length, v[1]/length, v[2]/length]
    return v

def cross_product(v1, v2):
    """向量叉积"""
    return [
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    ]

def dot_product(v1, v2):
    """向量点积"""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def vector_subtract(v1, v2):
    """向量减法"""
    return [v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2]]

def vector_multiply(v, scalar):
    """向量标量乘法"""
    return [v[0]*scalar, v[1]*scalar, v[2]*scalar]

def clamp(value, min_val, max_val):
    """限制数值范围"""
    return max(min(value, max_val), min_val)

# ----------------------- 全局配置与工具函数 -----------------------

WINDOW_NAME = 'alignmentToolWindow'
AXIS_OPTIONS = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']

alignment_settings = {
    'full_alignment': False,
    'rotate_axes': {'x': True, 'y': True, 'z': True},
    'source_axis': '+Y',
    'target_axis': '+Y',
    # 时间与执行设置
    'time_next_frame': False,            # 单帧模式下执行后跳到下一帧
    'time_mode': 'timeline',             # single/custom/timeline，默认timeline
    'custom_start': 1,
    'custom_end': 1,
    'bake_all_frames': True,             # 烘焙模式，默认True
    'per_frame_iters': 5,                # 每帧迭代次数
    # 对象列表设置（多组源-目标对）
    'object_pairs': [],                  # [(source1, target1), (source2, target2), ...]
}

ui_controls = {}


def parse_axis_option(axis_option):
    """解析轴选项，返回轴字母与符号"""
    axis_option = axis_option.upper()
    sign = -1 if axis_option.startswith('-') else 1
    axis = axis_option[-1].lower()
    if axis not in ['x', 'y', 'z']:
        axis = 'y'
    return axis, sign


def get_axis_vector_with_sign(obj, axis_option, fallback_child=None):
    """根据轴选项获取对象在世界空间中的轴向量"""
    axis_name, sign = parse_axis_option(axis_option)
    axis_vectors = get_object_axes(obj)
    axis_map = {'x': axis_vectors[0], 'y': axis_vectors[1], 'z': axis_vectors[2]}
    vector = axis_map.get(axis_name, [0.0, 1.0, 0.0])
    if is_close_to_zero(vector_length(vector)) and fallback_child:
        vector = get_object_direction(obj, fallback_child)
    if is_close_to_zero(vector_length(vector)):
        # 最终兜底为世界Y轴
        vector = [0.0, 1.0, 0.0]
    return vector_multiply(vector, sign)


def apply_limited_rotation(obj, ordered_euler, rotate_axes):
    """根据轴限制应用旋转"""
    if rotate_axes is None:
        rotate_axes = {'x': True, 'y': True, 'z': True}
    axes = ['x', 'y', 'z']
    for idx, axis in enumerate(axes):
        attr = '{0}.rotate{1}'.format(obj, axis.upper())
        # 未允许 或 已锁定：完全不写入
        if not rotate_axes.get(axis, True):
            continue
        is_locked = False
        try:
            is_locked = cmds.getAttr(attr, lock=True)
        except Exception:
            is_locked = False
        if is_locked:
            # 严格遵循“不动锁定轴”
            continue
        try:
            target_val = math.degrees(ordered_euler[idx])
            cmds.setAttr(attr, target_val)
        except Exception as e:
            cmds.warning(u'设置 {0} 失败: {1}'.format(attr, e))

def get_writable_axes(obj, rotate_axes):
    """返回允许且未锁定的可写轴列表，例如 ['x','z']"""
    if rotate_axes is None:
        rotate_axes = {'x': True, 'y': True, 'z': True}
    writable = []
    for axis in ['x', 'y', 'z']:
        if not rotate_axes.get(axis, True):
            continue
        attr = '{0}.rotate{1}'.format(obj, axis.upper())
        try:
            if not cmds.getAttr(attr, lock=True):
                writable.append(axis)
        except Exception:
            # 读取失败则视为不可写
            pass
    return writable


# ----------------------- 核心空间变换函数 -----------------------

def get_object_position(obj):
    """获取对象的全局位置"""
    pos = cmds.xform(obj, query=True, worldSpace=True, translation=True)
    return list(pos)

def getGlobalRot(obj):
    """获取对象的全局旋转矩阵"""
    matrix = cmds.xform(obj, q=True, m=True, ws=True)
    m_matrix = om.MMatrix(matrix)
    t_matrix = om.MTransformationMatrix(m_matrix)
    return t_matrix.rotation(asQuaternion=True).asMatrix()

def getJointOrient(obj):
    """获取关节方向矩阵，对非骨骼对象返回单位矩阵"""
    obj_type = cmds.objectType(obj)
    if obj_type == "joint":
        orient = cmds.getAttr(obj + ".jointOrient")[0]
        jo_euler = om.MEulerRotation(
            math.radians(orient[0]),
            math.radians(orient[1]),
            math.radians(orient[2])
        )
        return jo_euler.asMatrix()
    else:
        # 非骨骼对象返回单位矩阵
        return om.MMatrix()

def getRotateAxisRot(obj):
    """获取rotateAxis矩阵，对非骨骼对象检查是否有该属性"""
    if cmds.attributeQuery("rotateAxis", node=obj, exists=True):
        joint_axis = cmds.getAttr(obj + ".rotateAxis")[0]
        ra_euler = om.MEulerRotation(
            math.radians(joint_axis[0]),
            math.radians(joint_axis[1]),
            math.radians(joint_axis[2]),
            0
        )
        return ra_euler.asMatrix()
    else:
        # 没有rotateAxis属性的对象返回单位矩阵
        return om.MMatrix()

def getRotOrder(obj):
    """获取旋转顺序"""
    if cmds.attributeQuery("rotateOrder", node=obj, exists=True):
        return cmds.getAttr(obj + ".rotateOrder")
    return 0  # 默认XYZ顺序

def getAnimRotate(obj):
    """获取动画旋转矩阵"""
    animLocalRot = cmds.getAttr(obj + ".rotate")[0]
    animEuler = om.MEulerRotation(
        math.radians(animLocalRot[0]),
        math.radians(animLocalRot[1]),
        math.radians(animLocalRot[2]),
        getRotOrder(obj)
    )
    return animEuler.asMatrix()

def getInherentRotWithoutParent(obj):
    """获取不考虑父级的固有旋转"""
    jo_matrix = getJointOrient(obj)
    ra_matrix = getRotateAxisRot(obj)
    anim_matrix = getAnimRotate(obj)

    tmp_matrix = om.MMatrix()
    result_matrix = om.MMatrix()
    tmp_matrix.setToProduct(ra_matrix, anim_matrix)
    result_matrix.setToProduct(tmp_matrix, jo_matrix)
    return result_matrix

def get_parent_delta_global_rot(obj):
    """计算父级额外贡献的全局旋转"""
    inherent_global_rot = getInherentRotWithoutParent(obj)
    global_rot = getGlobalRot(obj)
    delta_rot = om.MMatrix()
    delta_rot.setToProduct(inherent_global_rot.inverse(), global_rot)
    return delta_rot

# ----------------------- 核心对齐函数 -----------------------

def get_object_direction(obj, child_obj=None):
    """获取对象的方向向量
    
    参数:
    obj - 要获取方向的对象
    child_obj - 可选的子对象，用于确定方向。如果提供，将使用它来计算方向
    
    对于骨骼，默认使用子骨骼确定方向
    对于其他对象，如果指定了子对象，使用子对象确定方向；否则使用对象自身的局部轴
    """
    # 如果提供了明确的子对象，直接使用它计算方向
    if child_obj:
        child_pos = get_object_position(child_obj)
        obj_pos = get_object_position(obj)
        direction = vector_subtract(child_pos, obj_pos)
        # 检查方向向量是否有效
        if not is_close_to_zero(vector_length(direction)):
            return direction
    
    # 对于骨骼，尝试使用子骨骼确定方向
    obj_type = cmds.objectType(obj)
    if obj_type == "joint":
        children = cmds.listRelatives(obj, children=True, type="joint")
        if children:
            child_pos = get_object_position(children[0])
            obj_pos = get_object_position(obj)
            direction = vector_subtract(child_pos, obj_pos)
            if not is_close_to_zero(vector_length(direction)):
                return direction
    
    # 尝试使用所有子对象（不限于骨骼）
    children = cmds.listRelatives(obj, children=True)
    if children:
        # 找到第一个有位置信息的子对象
        for child in children:
            try:
                child_pos = get_object_position(child)
                obj_pos = get_object_position(obj)
                direction = vector_subtract(child_pos, obj_pos)
                if not is_close_to_zero(vector_length(direction)):
                    return direction
            except:
                continue
    
    # 如果以上方法都失败，使用对象的局部轴
    # 获取对象的全局矩阵
    matrix = cmds.xform(obj, q=True, m=True, ws=True)
    
    # 尝试使用Y轴（通常是Maya中的主轴）
    y_axis = [matrix[4], matrix[5], matrix[6]]
    if not is_close_to_zero(vector_length(y_axis)):
        return y_axis
    
    # 如果Y轴接近零向量，尝试使用X轴或Z轴
    x_axis = [matrix[0], matrix[1], matrix[2]]
    if not is_close_to_zero(vector_length(x_axis)):
        return x_axis
    
    z_axis = [matrix[8], matrix[9], matrix[10]]
    return z_axis

def get_object_axes(obj):
    """获取对象的所有三个轴向
    
    返回:
    tuple: (x_axis, y_axis, z_axis) 三个轴的单位向量
    """
    matrix = cmds.xform(obj, q=True, m=True, ws=True)
    
    # 从变换矩阵中提取三个轴
    x_axis = [matrix[0], matrix[1], matrix[2]]
    y_axis = [matrix[4], matrix[5], matrix[6]]
    z_axis = [matrix[8], matrix[9], matrix[10]]
    
    # 归一化
    x_norm = vector_length(x_axis)
    if x_norm > 0:
        x_axis = [x_axis[0]/x_norm, x_axis[1]/x_norm, x_axis[2]/x_norm]
        
    y_norm = vector_length(y_axis)
    if y_norm > 0:
        y_axis = [y_axis[0]/y_norm, y_axis[1]/y_norm, y_axis[2]/y_norm]
        
    z_norm = vector_length(z_axis)
    if z_norm > 0:
        z_axis = [z_axis[0]/z_norm, z_axis[1]/z_norm, z_axis[2]/z_norm]
    
    return x_axis, y_axis, z_axis

def create_orientation_matrix(primary_axis, secondary_axis, primary_axis_name='y', secondary_axis_name='x'):
    """创建方向矩阵
    
    参数:
    primary_axis - 主轴方向向量
    secondary_axis - 辅助轴方向向量
    primary_axis_name - 主轴名称 ('x', 'y', 或 'z')
    secondary_axis_name - 辅助轴名称 ('x', 'y', 或 'z')
    
    返回:
    om.MMatrix: 表示所需方向的矩阵
    """
    # 确保输入是单位向量
    primary = list(primary_axis)
    primary_norm = vector_length(primary)
    if primary_norm > 0:
        primary = [primary[0]/primary_norm, primary[1]/primary_norm, primary[2]/primary_norm]
    
    secondary = list(secondary_axis)
    secondary_norm = vector_length(secondary)
    if secondary_norm > 0:
        secondary = [secondary[0]/secondary_norm, secondary[1]/secondary_norm, secondary[2]/secondary_norm]
    
    # 计算第三个轴（叉积）
    tertiary = cross_product(primary, secondary)
    tertiary_norm = vector_length(tertiary)
    if tertiary_norm > 0:
        tertiary = [tertiary[0]/tertiary_norm, tertiary[1]/tertiary_norm, tertiary[2]/tertiary_norm]
    
    # 重新计算secondary以确保正交性
    secondary = cross_product(tertiary, primary)
    secondary_norm = vector_length(secondary)
    if secondary_norm > 0:
        secondary = [secondary[0]/secondary_norm, secondary[1]/secondary_norm, secondary[2]/secondary_norm]
    
    # 根据指定的轴名称创建矩阵
    matrix_array = [0.0] * 16  # 4x4矩阵
    
    # 设置单位矩阵
    matrix_array[0] = 1.0
    matrix_array[5] = 1.0
    matrix_array[10] = 1.0
    matrix_array[15] = 1.0
    
    # 根据主轴和辅助轴的名称填充矩阵
    axes = {'x': 0, 'y': 1, 'z': 2}
    vectors = [secondary, primary, tertiary]  # 顺序: x, y, z
    
    # 填充矩阵
    for i, axis_name in enumerate(['x', 'y', 'z']):
        vector_index = 0
        if axis_name == primary_axis_name:
            vector_index = 1
        elif axis_name == secondary_axis_name:
            vector_index = 0
        else:
            vector_index = 2
            
        vector = vectors[vector_index]
        matrix_array[i] = float(vector[0])
        matrix_array[i+4] = float(vector[1])
        matrix_array[i+8] = float(vector[2])
    
    return om.MMatrix(matrix_array)

def align_object_to_target_full(source_obj, target_obj, source_child=None, target_child=None,
                               source_up_obj=None, target_up_obj=None,
                               settings=None):
    """将源对象完全对齐到目标对象的方向（两步法）
    - 第一步：先执行单轴对齐，让主轴完全对齐
    - 第二步：绕主轴旋转源对象，使剩余两个轴也对齐（选择旋转角度最小的方案）
    """
    if settings is None:
        settings = alignment_settings
    rotate_axes = settings.get('rotate_axes', {'x': True, 'y': True, 'z': True})
    source_axis_option = settings.get('source_axis', '+Y')
    target_axis_option = settings.get('target_axis', '+Y')

    source_primary_axis, source_sign = parse_axis_option(source_axis_option)
    target_primary_axis, target_sign = parse_axis_option(target_axis_option)

    # 检查可写轴
    allowed_axes = get_writable_axes(source_obj, rotate_axes)
    if len(allowed_axes) <= 1:
        # 只有一个或没有轴可写，退化为单轴对齐
        cmds.warning(u"{0} 可写轴不足（需至少2个），退化为单轴对齐".format(source_obj))
        return align_object_to_target(source_obj, target_obj, source_child, target_child, settings=settings)

    print(u"完全对齐第一步: 单轴对齐主轴 {0}".format(source_primary_axis))
    
    # ===== 第一步：执行单轴对齐，让主轴完全对齐 =====
    success = align_object_to_target(source_obj, target_obj, source_child, target_child, settings=settings)
    if not success:
        cmds.warning(u"单轴对齐失败，无法继续完全对齐")
        return False
    
    print(u"完全对齐第二步: 绕主轴旋转以对齐剩余轴")
    
    # ===== 第二步：在同一帧绕主轴旋转，对齐剩余轴 =====
    # 获取源对象主轴的世界空间向量（对齐后）
    source_primary_vector = get_axis_vector_with_sign(source_obj, source_axis_option, source_child)
    if is_close_to_zero(vector_length(source_primary_vector)):
        cmds.warning(u"源对象 {0} 主轴向量异常".format(source_obj))
        return False
    
    # 获取剩余的两个轴
    all_axes = ['x', 'y', 'z']
    remaining_axes = [ax for ax in all_axes if ax != source_primary_axis]
    
    # 获取源对象和目标对象的所有轴向量
    source_axes_dict = dict(zip(['x', 'y', 'z'], get_object_axes(source_obj)))
    target_axes_dict = dict(zip(['x', 'y', 'z'], get_object_axes(target_obj)))
    
    # 选择剩余轴中与目标夹角较小的作为参考轴（旋转角度最少原则）
    reference_axis = remaining_axes[0]
    min_angle = float('inf')
    for axis_name in remaining_axes:
        source_vec = source_axes_dict[axis_name]
        target_vec = target_axes_dict[axis_name]
        dot_val = dot_product(source_vec, target_vec)
        dot_val = clamp(dot_val, -1.0, 1.0)
        angle = math.acos(abs(dot_val))
        if angle < min_angle:
            min_angle = angle
            reference_axis = axis_name
    
    print(u"  选择参考轴: {0} (初始偏差: {1:.1f}°)".format(reference_axis, math.degrees(min_angle)))
    
    # 获取参考轴的源向量和目标向量
    source_ref_vec = source_axes_dict[reference_axis]
    target_ref_vec = target_axes_dict[reference_axis]
    
    # 将两个向量投影到垂直于主轴的平面上
    primary_mvec = om.MVector(
        float(source_primary_vector[0]),
        float(source_primary_vector[1]),
        float(source_primary_vector[2])
    )
    
    def project_to_plane(vec, normal):
        """将向量投影到垂直于法向量的平面上"""
        v = [vec[0], vec[1], vec[2]]
        n = [normal.x, normal.y, normal.z]
        n_normalized = normalize_vector(n)
        proj_length = dot_product(v, n_normalized)
        proj = vector_multiply(n_normalized, proj_length)
        v_plane = vector_subtract(v, proj)
        return normalize_vector(v_plane)
    
    # 将参考轴向量投影到垂直于主轴的平面
    source_ref_projected = project_to_plane(source_ref_vec, primary_mvec)
    target_ref_projected = project_to_plane(target_ref_vec, primary_mvec)
    
    # 检查投影后的向量是否有效
    if is_close_to_zero(vector_length(source_ref_projected)) or is_close_to_zero(vector_length(target_ref_projected)):
        print(u"  参考轴与主轴平行，剩余轴已对齐或无需旋转")
        print(u"完全对齐完成: {0}".format(source_obj))
        return True
    
    # 计算需要绕主轴旋转的角度
    dot_val = dot_product(source_ref_projected, target_ref_projected)
    dot_val = clamp(dot_val, -1.0, 1.0)
    rotation_angle = math.acos(dot_val)
    
    # 确定旋转方向（通过叉积判断）
    cross = cross_product(source_ref_projected, target_ref_projected)
    # 如果叉积与主轴同向，角度为正；反向则为负
    direction = dot_product(cross, [primary_mvec.x, primary_mvec.y, primary_mvec.z])
    if direction < 0:
        rotation_angle = -rotation_angle
    
    print(u"  绕主轴旋转角度: {0:.1f}°".format(math.degrees(rotation_angle)))
    
    # 应用旋转
    if abs(rotation_angle) > 1e-6:  # 只有当旋转角度不为零时才应用
        # 准备旋转计算所需的矩阵
        parent_delta_global_rot = get_parent_delta_global_rot(source_obj)
        jo_mat = getJointOrient(source_obj)
        ra_mat = getRotateAxisRot(source_obj)
        current_global = getGlobalRot(source_obj)
        rot_order = getRotOrder(source_obj)
        
        axis_quat = om.MQuaternion(rotation_angle, primary_mvec)
        final_rotation_matrix = axis_quat.asMatrix()
        
        # 计算最终的rotate值
        tmp1 = om.MMatrix()
        tmp2 = om.MMatrix()
        tmp3 = om.MMatrix()
        new_rot_mat = om.MMatrix()
        
        tmp1.setToProduct(jo_mat, parent_delta_global_rot)
        tmp2.setToProduct(current_global, final_rotation_matrix)
        tmp3.setToProduct(ra_mat.inverse(), tmp2)
        new_rot_mat.setToProduct(tmp3, tmp1.inverse())
        
        new_rot_transMat = om.MTransformationMatrix(new_rot_mat)
        new_rot = new_rot_transMat.rotation(asQuaternion=True)
        new_rot_euler = new_rot.asEulerRotation()
        ordered_euler = new_rot_euler.reorderIt(rot_order)
        
        apply_limited_rotation(source_obj, ordered_euler, rotate_axes)
    else:
        print(u"  无需旋转，剩余轴已对齐")
    
    print(u"完全对齐完成: {0}".format(source_obj))
    return True

def align_object_to_target(source_obj, target_obj, source_child=None, target_child=None, settings=None):
    """将源对象对齐到目标对象的方向（仅主轴）"""
    if settings is None:
        settings = alignment_settings
    source_axis_option = settings.get('source_axis', '+Y')
    target_axis_option = settings.get('target_axis', '+Y')
    rotate_axes = settings.get('rotate_axes', {'x': True, 'y': True, 'z': True})

    target_primary_axis, target_sign = parse_axis_option(target_axis_option)
    target_vector = get_axis_vector_with_sign(
        target_obj,
        '+{0}'.format(target_primary_axis.upper()),
        target_child
    )
    target_vector = vector_multiply(target_vector, target_sign)

    if is_close_to_zero(vector_length(target_vector)):
        cmds.warning(u"目标对象 {0} 无法确定方向".format(target_obj))
        return False

    align_to_vector(source_obj, target_vector, source_child, settings=settings, rotate_axes=rotate_axes, source_axis_option=source_axis_option)
    return True

def align_to_vector(obj, target_vector, child_obj=None, settings=None, rotate_axes=None, source_axis_option='+Y'):
    """将对象对齐到指定方向向量
    - 若仅允许单轴旋转：绕该局部轴做最优单轴旋转，使主轴方向尽量对齐目标方向
    - 若多轴旋转：在对齐主轴的基础上，选择与当前旋转变化最小的解（最小化跳动）
    """
    if settings is None:
        settings = alignment_settings
    if rotate_axes is None:
        rotate_axes = settings.get('rotate_axes', {'x': True, 'y': True, 'z': True})

    current_direction = get_axis_vector_with_sign(obj, source_axis_option, child_obj)

    if is_close_to_zero(vector_length(current_direction)):
        matrix = cmds.xform(obj, q=True, m=True, ws=True)
        current_direction = [matrix[4], matrix[5], matrix[6]]
        if is_close_to_zero(vector_length(current_direction)):
            current_direction = [matrix[0], matrix[1], matrix[2]]
        if is_close_to_zero(vector_length(current_direction)):
            current_direction = [matrix[8], matrix[9], matrix[10]]

    parent_delta_global_rot = get_parent_delta_global_rot(obj)

    boneVec = om.MVector(float(current_direction[0]), float(current_direction[1]), float(current_direction[2]))
    targetVec = om.MVector(float(target_vector[0]), float(target_vector[1]), float(target_vector[2]))

    # 仅允许单轴旋转时，计算绕该局部轴的最佳旋转
    allowed_axes = get_writable_axes(obj, rotate_axes)
    if len(allowed_axes) == 1:
        axis_name = allowed_axes[0]  # 'x'/'y'/'z'
        ax_x, ax_y, ax_z = get_object_axes(obj)
        axis_map = {'x': ax_x, 'y': ax_y, 'z': ax_z}
        axis_vec_np = axis_map.get(axis_name, ax_y)
        # 旋转轴（世界空间中的源对象局部轴）
        axis_vec = om.MVector(float(axis_vec_np[0]), float(axis_vec_np[1]), float(axis_vec_np[2]))
        # 投影到垂直于轴的平面
        def proj_perp_axis(v):
            v_np = [v.x, v.y, v.z]
            a_np = [axis_vec.x, axis_vec.y, axis_vec.z]
            a_len = vector_length(a_np)
            a_np = [a_np[0]/a_len, a_np[1]/a_len, a_np[2]/a_len] if a_len > 0 else a_np
            par_scale = dot_product(v_np, a_np)
            v_par = vector_multiply(a_np, par_scale)
            v_perp = vector_subtract(v_np, v_par)
            n = vector_length(v_perp)
            return [v_perp[0]/n, v_perp[1]/n, v_perp[2]/n] if n > 1e-8 else v_perp
        v1 = proj_perp_axis(boneVec)
        v2 = proj_perp_axis(targetVec)
        n1 = vector_length(v1)
        n2 = vector_length(v2)
        if n1 < 1e-8 or n2 < 1e-8:
            # 投影退化，无法通过该轴产生有效对齐，放弃旋转
            needRot = om.MQuaternion()
        else:
            # 计算有符号角度
            dot = float(clamp(dot_product(v1, v2), -1.0, 1.0))
            angle = math.acos(dot)
            # 方向通过三重积确定
            cross_np = cross_product(v1, v2)
            sign = 1.0 if dot_product(cross_np, [axis_vec.x, axis_vec.y, axis_vec.z]) > 0 else -1.0
            needRot = om.MQuaternion(angle * sign, axis_vec)
    elif len(allowed_axes) >= 2:
        # 多轴旋转：基础对齐 + 最小变化优化
        # 1. 获取当前旋转状态（作为参考）
        current_rotate = [
            cmds.getAttr('{0}.rotateX'.format(obj)),
            cmds.getAttr('{0}.rotateY'.format(obj)),
            cmds.getAttr('{0}.rotateZ'.format(obj))
        ]
        
        # 2. 计算基础对齐旋转（最短路径）
        baseRot = boneVec.rotateTo(targetVec)
        
        # 3. 在绕目标向量的360度范围内，寻找让旋转变化最小的角度
        # 测试多个角度（每30度一个采样点）
        best_angle = 0.0
        min_change = float('inf')
        
        for test_angle_deg in range(0, 360, 30):
            test_angle = math.radians(test_angle_deg)
            # 绕目标向量额外旋转
            axisRot = om.MQuaternion(test_angle, targetVec)
            combinedRot = axisRot * baseRot
            testRotMat = combinedRot.asMatrix()
            
            # 计算这个旋转会产生的最终欧拉角
            jo_mat = getJointOrient(obj)
            ra_mat = getRotateAxisRot(obj)
            current_global = getGlobalRot(obj)
            tmp1 = om.MMatrix()
            tmp2 = om.MMatrix()
            tmp3 = om.MMatrix()
            test_new_rot_mat = om.MMatrix()
            tmp1.setToProduct(jo_mat, parent_delta_global_rot)
            tmp2.setToProduct(current_global, testRotMat)
            tmp3.setToProduct(ra_mat.inverse(), tmp2)
            test_new_rot_mat.setToProduct(tmp3, tmp1.inverse())
            
            test_transMat = om.MTransformationMatrix(test_new_rot_mat)
            test_quat = test_transMat.rotation(asQuaternion=True)
            test_euler = test_quat.asEulerRotation()
            order = getRotOrder(obj)
            test_ordered = test_euler.reorderIt(order)
            
            # 计算与当前旋转的差异（欧拉角距离）
            change = 0.0
            for i in range(3):
                angle_diff = abs(math.degrees(test_ordered[i]) - current_rotate[i])
                # 处理角度环绕（例如 359度 和 1度 实际很接近）
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                change += angle_diff * angle_diff  # 平方和
            
            if change < min_change:
                min_change = change
                best_angle = test_angle
        
        # 4. 使用最佳角度构建最终旋转
        axisRot = om.MQuaternion(best_angle, targetVec)
        needRot = axisRot * baseRot
        needRotMat = needRot.asMatrix()
    else:
        # 无可写轴：不做任何旋转
        cmds.warning(u"{0} 没有可写的旋转轴（全部未勾选或被锁定），已跳过。".format(obj))
        needRot = om.MQuaternion()
        needRotMat = needRot.asMatrix()
    
    # 单轴旋转情况：需要转换为矩阵
    if len(allowed_axes) == 1:
        needRotMat = needRot.asMatrix()

    jo_mat = getJointOrient(obj)
    ra_mat = getRotateAxisRot(obj)
    current_global = getGlobalRot(obj)

    tmp1 = om.MMatrix()
    tmp2 = om.MMatrix()
    tmp3 = om.MMatrix()
    new_rot_mat = om.MMatrix()

    tmp1.setToProduct(jo_mat, parent_delta_global_rot)
    tmp2.setToProduct(current_global, needRotMat)
    tmp3.setToProduct(ra_mat.inverse(), tmp2)
    new_rot_mat.setToProduct(tmp3, tmp1.inverse())

    new_rot_transMat = om.MTransformationMatrix(new_rot_mat)
    new_rot = new_rot_transMat.rotation(asQuaternion=True)
    new_rot_euler = new_rot.asEulerRotation()

    order = getRotOrder(obj)
    ordered_euler = new_rot_euler.reorderIt(order)

    print(u"正在对齐对象: {0}".format(obj))
    apply_limited_rotation(obj, ordered_euler, rotate_axes)

# ----------------------- 主执行函数 -----------------------

def align_selected_objects(settings=None):
    """对齐选中的对象"""
    if settings is None:
        settings = alignment_settings
    full_alignment = settings.get('full_alignment', False)
    selected = cmds.ls(selection=True)
    
    if not selected:
        cmds.warning("请先选择需要对齐的对象")
        return
    
    if len(selected) == 2:
        source_obj = selected[0]
        target_obj = selected[1]
        
        cmds.undoInfo(openChunk=True)
        try:
            if full_alignment:
                if align_object_to_target_full(source_obj, target_obj, settings=settings):
                    cmds.inViewMessage(amg=u'已将 {0} 完全对齐到 {1}'.format(source_obj, target_obj), pos='topCenter', fade=True)
            else:
                if align_object_to_target(source_obj, target_obj, settings=settings):
                    cmds.inViewMessage(amg=u'已将 {0} 对齐到 {1}'.format(source_obj, target_obj), pos='topCenter', fade=True)
        except Exception as e:
            cmds.warning(u"对齐失败: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            
    elif len(selected) == 4:
        source_obj = selected[0]
        source_child = selected[1]
        target_obj = selected[2]
        target_child = selected[3]
        
        cmds.undoInfo(openChunk=True)
        try:
            if full_alignment:
                if align_object_to_target_full(source_obj, target_obj, source_child, target_child, settings=settings):
                    cmds.inViewMessage(amg=u'已将 {0} 完全对齐到 {1}'.format(source_obj, target_obj), pos='topCenter', fade=True)
            else:
                if align_object_to_target(source_obj, target_obj, source_child, target_child, settings=settings):
                    cmds.inViewMessage(amg=u'已将 {0} 对齐到 {1}'.format(source_obj, target_obj), pos='topCenter', fade=True)
        except Exception as e:
            cmds.warning(u"对齐失败: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            
    elif len(selected) == 6:
        source_obj = selected[0]
        source_child = selected[1]
        source_up = selected[2]
        target_obj = selected[3]
        target_child = selected[4]
        target_up = selected[5]
        
        if not full_alignment:
            cmds.warning("选择了6个对象但未选择完全对齐模式，将仅使用前4个对象进行单轴对齐")
            align_object_to_target(source_obj, target_obj, source_child, target_child, settings=settings)
            return
        
        cmds.undoInfo(openChunk=True)
        try:
            if align_object_to_target_full(source_obj, target_obj, source_child, target_child, source_up, target_up, settings=settings):
                cmds.inViewMessage(amg=u'已将 {0} 完全对齐到 {1}'.format(source_obj, target_obj), pos='topCenter', fade=True)
        except Exception as e:
            cmds.warning(u"对齐失败: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
    else:
        cmds.confirmDialog(
            title='错误', 
            message='请选择2个对象(源和目标)、4个对象(源、源子、目标、目标子)或6个对象(源、源子、源辅助、目标、目标子、目标辅助)', 
            button=['确定'], 
            defaultButton='确定'
        )
        return

def execute_alignment(*args):
    """从UI读取设置并执行对齐"""
    global alignment_settings
    if not ui_controls:
        cmds.warning(u"UI尚未初始化")
        return
    
    # 检查是否有录入的对象对
    if not alignment_settings.get('object_pairs'):
        cmds.warning(u'请先录入至少一组对象对')
        return
    
    # 读取UI设置
    full_alignment = cmds.radioButtonGrp(ui_controls['mode'], q=True, select=True) == 2
    rotate_axes = {
        'x': cmds.checkBox(ui_controls['rotate_x'], q=True, value=True),
        'y': cmds.checkBox(ui_controls['rotate_y'], q=True, value=True),
        'z': cmds.checkBox(ui_controls['rotate_z'], q=True, value=True),
    }
    source_axis = cmds.optionMenu(ui_controls['source_axis'], q=True, value=True)
    target_axis = cmds.optionMenu(ui_controls['target_axis'], q=True, value=True)
    
    # 时间与范围
    time_next_frame = cmds.menuItem(ui_controls['opt_next_frame'], q=True, checkBox=True)
    is_single = cmds.radioButton(ui_controls['time_mode_single'], q=True, select=True)
    is_custom = cmds.radioButton(ui_controls['time_mode_custom'], q=True, select=True)
    time_mode = 'single' if is_single else ('custom' if is_custom else 'timeline')
    custom_start = cmds.intField(ui_controls['custom_start'], q=True, value=True)
    custom_end = cmds.intField(ui_controls['custom_end'], q=True, value=True)
    bake_all_frames = cmds.checkBox(ui_controls['bake'], q=True, value=True)
    
    # 更新全局设置
    alignment_settings.update({
        'full_alignment': full_alignment,
        'rotate_axes': rotate_axes,
        'source_axis': source_axis,
        'target_axis': target_axis,
        'time_next_frame': time_next_frame,
        'time_mode': time_mode,
        'custom_start': custom_start,
        'custom_end': custom_end,
        'bake_all_frames': bake_all_frames,
    })
    
    execute_alignment_core(alignment_settings)

def create_alignment_window():
    """创建对齐工具UI"""
    global ui_controls
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)
    
    ui_controls = {}
    rotate_axes_defaults = alignment_settings.get('rotate_axes', {'x': True, 'y': True, 'z': True})
    
    window = cmds.window(WINDOW_NAME, title=u'旋转对齐工具', sizeable=True, widthHeight=(380, 460))
    main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=4, columnAttach=('both', 6))
    
    # 对齐模式
    cmds.frameLayout(label=u'对齐模式', marginHeight=3, collapsable=False)
    cmds.rowLayout(numberOfColumns=2, columnAttach=[(1,'left',4),(2,'left',20)])
    ui_controls['mode'] = cmds.radioButtonGrp(
        label='',
        labelArray2=[u'单轴对齐', u'完全对齐'],
        numberOfRadioButtons=2,
        select=2 if alignment_settings.get('full_alignment') else 1,
        columnWidth2=[80, 80]
    )
    cmds.setParent('..'); cmds.setParent('..')
    
    # 旋转轴限制
    cmds.frameLayout(label=u'旋转轴限制', marginHeight=3, collapsable=False)
    cmds.rowLayout(numberOfColumns=3, columnAttach=[(1, 'left', 6)])
    ui_controls['rotate_x'] = cmds.checkBox(label='X', value=rotate_axes_defaults.get('x', True), width=50)
    ui_controls['rotate_y'] = cmds.checkBox(label='Y', value=rotate_axes_defaults.get('y', True), width=50)
    ui_controls['rotate_z'] = cmds.checkBox(label='Z', value=rotate_axes_defaults.get('z', True), width=50)
    cmds.setParent('..'); cmds.setParent('..')
    
    # 对齐轴设置
    cmds.frameLayout(label=u'对齐轴设置', marginHeight=3, collapsable=False)
    cmds.rowLayout(numberOfColumns=4, columnAttach=[(1,'left',6),(2,'left',4),(3,'left',10),(4,'left',4)])
    cmds.text(label=u'源:', width=30)
    ui_controls['source_axis'] = cmds.optionMenu(width=70)
    for opt in AXIS_OPTIONS:
        cmds.menuItem(label=opt)
    cmds.text(label=u'目标:', width=40)
    ui_controls['target_axis'] = cmds.optionMenu(width=70)
    for opt in AXIS_OPTIONS:
        cmds.menuItem(label=opt)
    cmds.optionMenu(ui_controls['source_axis'], e=True, value=alignment_settings.get('source_axis', '+Y'))
    cmds.optionMenu(ui_controls['target_axis'], e=True, value=alignment_settings.get('target_axis', '+Y'))
    cmds.setParent('..'); cmds.setParent('..')

    # 对象列表
    cmds.frameLayout(label=u'对象列表', marginHeight=3, collapsable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=2, columnAttach=('both', 4))
    
    # 对象列表显示
    ui_controls['object_list'] = cmds.textScrollList(height=80, allowMultiSelection=False)
    
    # 录入和管理按钮
    cmds.rowLayout(numberOfColumns=3, columnAttach=[(1,'both',0),(2,'both',2),(3,'both',0)])
    cmds.button(label=u'录入选中', command=lambda *args: _add_object_pair(), backgroundColor=(0.4, 0.6, 0.45))
    cmds.button(label=u'移除选中', command=lambda *args: _remove_selected_pair())
    cmds.button(label=u'清空列表', command=lambda *args: _clear_object_list())
    cmds.setParent('..')
    cmds.text(label=u'说明：先选源，再选目标，点录入', align='left', font='smallPlainLabelFont')
    cmds.setParent('..'); cmds.setParent('..')

    # 执行范围
    cmds.frameLayout(label=u'执行范围', marginHeight=3, collapsable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=2, columnAttach=('left', 6))
    
    # 创建单选按钮集合
    ui_controls['time_mode_collection'] = cmds.radioCollection()
    
    # 单帧选项（带右键菜单）
    single_btn = cmds.radioButton(label=u'单帧', select=alignment_settings.get('time_mode')=='single')
    ui_controls['time_mode_single'] = single_btn
    cmds.popupMenu(parent=single_btn)
    ui_controls['opt_next_frame'] = cmds.menuItem(label=u'执行后跳到下一帧', checkBox=alignment_settings.get('time_next_frame', False))
    
    # 自定义范围
    cmds.rowLayout(numberOfColumns=5, columnAttach=[(1,'left',0),(2,'left',4),(3,'left',4),(4,'left',4)])
    ui_controls['time_mode_custom'] = cmds.radioButton(label=u'自定义', select=alignment_settings.get('time_mode')=='custom',
                                                        onCommand=lambda *args: _update_time_controls())
    ui_controls['custom_start'] = cmds.intField(value=alignment_settings.get('custom_start', int(cmds.currentTime(q=True))), width=60)
    cmds.text(label='~', width=12)
    ui_controls['custom_end'] = cmds.intField(value=alignment_settings.get('custom_end', int(cmds.currentTime(q=True))), width=60)
    cmds.setParent('..')
    
    # 时间轴范围
    ui_controls['time_mode_timeline'] = cmds.radioButton(label=u'时间轴范围', select=alignment_settings.get('time_mode')=='timeline',
                                                          onCommand=lambda *args: _update_time_controls())
    
    # 将单选按钮添加到集合
    cmds.radioCollection(ui_controls['time_mode_collection'], edit=True, 
                        select=ui_controls['time_mode_single'] if alignment_settings.get('time_mode')=='single' 
                        else (ui_controls['time_mode_custom'] if alignment_settings.get('time_mode')=='custom' 
                        else ui_controls['time_mode_timeline']))
    
    # 烘焙选项
    ui_controls['bake'] = cmds.checkBox(label=u'烘焙', value=alignment_settings.get('bake_all_frames', True))
    
    cmds.setParent('..'); cmds.setParent('..')
    
    # 执行按钮
    cmds.separator(height=6, style='none')
    exec_btn = cmds.button(label=u'执行对齐', height=26, command=execute_alignment, backgroundColor=(0.3, 0.5, 0.7))
    cmds.popupMenu(parent=exec_btn)
    cmds.menuItem(label=u'设置每帧执行次数（当前: {0}）'.format(alignment_settings.get('per_frame_iters',5)), 
                  command=lambda *args: _set_per_frame_iters())
    
    cmds.setParent(main_layout)
    cmds.showWindow(window)
    
    # 初始化对象列表显示
    _refresh_object_list()
    _update_time_controls()
    
    # 设置单帧按钮的联动
    cmds.radioButton(single_btn, e=True, onCommand=lambda *args: _update_time_controls())

# ----------------------- 执行器与辅助 -----------------------

def _add_object_pair():
    """录入选中的对象对（先源后目标）"""
    sel = cmds.ls(selection=True)
    if len(sel) < 2:
        cmds.warning(u'请先选择2个对象：源对象和目标对象')
        return
    
    source_obj = sel[0]
    target_obj = sel[1]
    
    # 添加到对象对列表
    pair = (source_obj, target_obj)
    alignment_settings['object_pairs'].append(pair)
    
    # 刷新显示
    _refresh_object_list()
    print(u'已录入对象对: {0} -> {1}'.format(source_obj, target_obj))

def _remove_selected_pair():
    """移除选中的对象对"""
    if not ui_controls.get('object_list'):
        return
    
    selected_items = cmds.textScrollList(ui_controls['object_list'], q=True, selectIndexedItem=True)
    if not selected_items:
        cmds.warning(u'请先在列表中选择要移除的项')
        return
    
    # 从后往前删除（避免索引问题）
    for idx in sorted(selected_items, reverse=True):
        if 0 < idx <= len(alignment_settings['object_pairs']):
            removed_pair = alignment_settings['object_pairs'].pop(idx - 1)
            print(u'已移除对象对: {0} -> {1}'.format(removed_pair[0], removed_pair[1]))
    
    _refresh_object_list()

def _clear_object_list():
    """清空对象列表"""
    alignment_settings['object_pairs'] = []
    _refresh_object_list()
    print(u'已清空对象列表')

def _refresh_object_list():
    """刷新对象列表显示"""
    if not ui_controls.get('object_list'):
        return
    
    cmds.textScrollList(ui_controls['object_list'], e=True, removeAll=True)
    
    for i, (source, target) in enumerate(alignment_settings['object_pairs'], 1):
        display_text = u'{0}. {1} -> {2}'.format(i, source, target)
        cmds.textScrollList(ui_controls['object_list'], e=True, append=display_text)

def _set_per_frame_iters():
    try:
        result = cmds.promptDialog(
            title='每帧执行次数',
            message='请输入每帧执行次数（>=1）:',
            button=['确定','取消'],
            defaultButton='确定',
            cancelButton='取消',
            dismissString='取消'
        )
        if result == '确定':
            text = cmds.promptDialog(q=True, text=True).strip()
            val = int(text)
            if val < 1:
                raise ValueError('次数需 >= 1')
            alignment_settings['per_frame_iters'] = val
            create_alignment_window()
    except Exception as e:
        cmds.warning(u'设置失败: {0}'.format(e))

def _update_time_controls(*args):
    """根据执行范围联动控件启用/灰化"""
    if not ui_controls:
        return
    
    # 判断当前选择的模式
    is_single = cmds.radioButton(ui_controls['time_mode_single'], q=True, select=True)
    is_custom = cmds.radioButton(ui_controls['time_mode_custom'], q=True, select=True)
    is_timeline = cmds.radioButton(ui_controls['time_mode_timeline'], q=True, select=True)
    
    # 自定义范围输入，仅在 custom 模式可用
    cmds.intField(ui_controls['custom_start'], e=True, enable=is_custom)
    cmds.intField(ui_controls['custom_end'], e=True, enable=is_custom)
    
    # 烘焙仅在范围模式（custom/timeline）可用
    cmds.checkBox(ui_controls['bake'], e=True, enable=(is_custom or is_timeline))

def _collect_frames_by_settings(settings, target_obj):
    """返回需要执行的帧列表
    
    参数:
        settings: 设置字典
        target_obj: 目标对象（用于查找关键帧）
    """
    mode = settings.get('time_mode', 'timeline')
    bake = settings.get('bake_all_frames', True)
    cur = int(cmds.currentTime(q=True))
    
    if mode == 'single':
        return [cur]
    
    # 确定帧范围
    if mode == 'custom':
        start = int(settings.get('custom_start', cur))
        end = int(settings.get('custom_end', cur))
        if start > end:
            start, end = end, start
    else:  # timeline
        start = int(cmds.playbackOptions(q=True, minTime=True))
        end = int(cmds.playbackOptions(q=True, maxTime=True))
    
    # 根据烘焙选项决定帧列表
    if not bake:
        # 只在目标有关键帧的帧执行
        try:
            keys = cmds.keyframe(target_obj, q=True, time=(start, end))
            if not keys:
                return []
            # 去重并排序为整数帧
            frames = sorted(set(int(round(k)) for k in keys))
            return [f for f in frames if start <= f <= end]
        except:
            # 如果目标没有关键帧，返回空列表
            return []
    else:
        # 烘焙模式：范围内每一帧
        return list(xrange(start, end + 1))

def execute_alignment_core(settings):
    """按设置执行（支持多组对象、单帧/范围/烘焙/迭代/跳帧）"""
    object_pairs = settings.get('object_pairs', [])
    if not object_pairs:
        cmds.warning(u'没有要执行的对象对')
        return
    
    per_iters = int(settings.get('per_frame_iters', 5))
    per_iters = max(1, per_iters)
    full_alignment = settings.get('full_alignment', False)
    time_mode = settings.get('time_mode', 'timeline')
    
    # 对每一组对象对执行对齐
    for source_obj, target_obj in object_pairs:
        # 检查对象是否存在
        if not cmds.objExists(source_obj):
            cmds.warning(u'源对象不存在: {0}'.format(source_obj))
            continue
        if not cmds.objExists(target_obj):
            cmds.warning(u'目标对象不存在: {0}'.format(target_obj))
            continue
        
        print(u'\n处理对象对: {0} -> {1}'.format(source_obj, target_obj))
        
        # 收集要执行的帧
        frames = _collect_frames_by_settings(settings, target_obj)
        
        if not frames:
            if time_mode != 'single':
                cmds.warning(u'对象 {0} 在范围内未找到关键帧'.format(target_obj))
            continue
        
        print(u'执行帧数: {0} 帧'.format(len(frames)))
        
        # 在每一帧执行对齐
        for f in frames:
            cmds.currentTime(f, edit=True)
            cmds.undoInfo(openChunk=True)
            try:
                for _ in xrange(per_iters):
                    if full_alignment:
                        align_object_to_target_full(source_obj, target_obj, settings=settings)
                    else:
                        align_object_to_target(source_obj, target_obj, settings=settings)
            except Exception as e:
                cmds.warning(u'第 {0} 帧执行失败: {1}'.format(f, e))
            finally:
                cmds.undoInfo(closeChunk=True)
    
    # 单帧模式下，执行后跳到下一帧
    if time_mode == 'single' and settings.get('time_next_frame', False):
        cmds.currentTime(int(cmds.currentTime(q=True)) + 1, edit=True)
    
    cmds.inViewMessage(amg=u'对齐完成', pos='topCenter', fade=True)

# 创建UI
create_alignment_window()