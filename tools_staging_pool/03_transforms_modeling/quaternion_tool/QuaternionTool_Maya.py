# encoding=UTF-8

import maya.cmds as cmds
import maya.api.OpenMaya as om
import math

def clamp(value, minValue, maxValue):
    return max(minValue, min(maxValue, value))

def clamp01(value):
    return clamp(value, 0, 1)

# Maya自定义四元数工具
class Quaternion:
    def __init__(self, vector=None):
        if vector is None:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            self.w = 1.0
        elif isinstance(vector, om.MQuaternion):
            self.x = vector.x
            self.y = vector.y
            self.z = vector.z
            self.w = vector.w
        elif isinstance(vector, om.MVector) and len(vector) == 3:
            self.x = vector[0]
            self.y = vector[1]
            self.z = vector[2]
            self.w = 0.0
        elif hasattr(vector, "__len__") and len(vector) >= 4:
            self.x = float(vector[0])
            self.y = float(vector[1])
            self.z = float(vector[2])
            self.w = float(vector[3])
        else:
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
            self.w = 1.0

    @staticmethod
    def Identity():
        return Quaternion()

    def xyzw(self):
        return [self.x, self.y, self.z, self.w]

    def xyz(self):
        return om.MVector(self.x, self.y, self.z)

    def toMQuaternion(self):
        return om.MQuaternion(self.x, self.y, self.z, self.w)

    def __getitem__(self, key):  # 索引器
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        elif key == 3:
            return self.w
        else:
            raise IndexError("Quaternion index out of range")

    def __add__(self, quaternion):
        result = Quaternion(self.xyzw())
        result.x += quaternion.x
        result.y += quaternion.y
        result.z += quaternion.z
        result.w += quaternion.w
        return result

    def __sub__(self, quaternion):
        result = Quaternion(self.xyzw())
        result.x -= quaternion.x
        result.y -= quaternion.y
        result.z -= quaternion.z
        result.w -= quaternion.w
        return result

    def __mul__(self, quaternion):
        result = Quaternion()
        result.x = self.w * quaternion.x + self.x * quaternion.w - self.y * quaternion.z + self.z * quaternion.y
        result.y = self.w * quaternion.y + self.y * quaternion.w + self.x * quaternion.z - self.z * quaternion.x
        result.z = self.w * quaternion.z + self.z * quaternion.w - self.x * quaternion.y + self.y * quaternion.x
        result.w = self.w * quaternion.w - self.x * quaternion.x - self.y * quaternion.y - self.z * quaternion.z
        return result

    def Divides(self, quaternion):
        return self * (quaternion.Inversed())

    def MagnitudeSqr(self):
        return pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2) + pow(self.w, 2)

    def Magnituded(self):
        return pow(self.MagnitudeSqr(), 0.5)

    def Star(self):
        result = Quaternion(self.xyzw())
        result.x = -self.x
        result.y = -self.y
        result.z = -self.z
        result.w = self.w
        return result

    def Inversed(self):
        result = self.Star()
        moder = self.MagnitudeSqr()
        if moder > 0.00001:
            result.x /= moder
            result.y /= moder
            result.z /= moder
            result.w /= moder
            return result
        else:
            return self.Identity()

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z) + " " + str(self.w)

    def Normalize(self):
        moder = self.Magnituded()
        if moder > 0.00001:
            self.x /= moder
            self.y /= moder
            self.z /= moder
            self.w /= moder
            return self
        else:
            q = self.Identity()
            self.x = q.x
            self.y = q.y
            self.z = q.z
            self.w = q.w
            return self

    def Normalized(self):
        result = Quaternion(self.xyzw())
        moder = result.Magnituded()
        if moder > 0.00001:
            result.x /= moder
            result.y /= moder
            result.z /= moder
            result.w /= moder
            return result
        else:
            return self.Identity()

    @staticmethod
    def FromToRotation(fromDirection, toDirection):
        # 将输入转换为MVector
        if not isinstance(fromDirection, om.MVector):
            fromDirection = om.MVector(fromDirection[0], fromDirection[1], fromDirection[2])
        if not isinstance(toDirection, om.MVector):
            toDirection = om.MVector(toDirection[0], toDirection[1], toDirection[2])
            
        if fromDirection.length() < 0.00001 or toDirection.length() < 0.00001:
            return Quaternion.Identity()

        fromDirection.normalize()
        toDirection.normalize()

        # 检查两个向量是否相等
        if abs(fromDirection.x - toDirection.x) < 0.00001 and \
           abs(fromDirection.y - toDirection.y) < 0.00001 and \
           abs(fromDirection.z - toDirection.z) < 0.00001:
            return Quaternion.Identity()

        axis = fromDirection ^ toDirection  # 使用Maya的叉乘运算符
        sinA = axis.length()
        cosA = fromDirection * toDirection  # 使用Maya的点乘运算符

        sinHalfA = pow(((1 - cosA) * 0.5), 0.5)
        if sinA > 0.00001:
            cosHalfA = sinA / (2.0 * sinHalfA)
            axis.normalize()
            axis = axis * sinHalfA
            return Quaternion([axis.x, axis.y, axis.z, cosHalfA])
        else:
            # 处理180度旋转的特殊情况
            perpVector = om.MVector()
            if abs(fromDirection.x) < abs(fromDirection.y) and abs(fromDirection.x) < abs(fromDirection.z):
                perpVector = om.MVector(1, 0, 0)
            elif abs(fromDirection.y) < abs(fromDirection.z):
                perpVector = om.MVector(0, 1, 0)
            else:
                perpVector = om.MVector(0, 0, 1)
                
            axis = fromDirection ^ perpVector
            axis.normalize()
            return Quaternion([axis.x, axis.y, axis.z, 0])

    @staticmethod
    def FromEuler(euler):
        # Maya使用弧度，但我们保持接口一致，输入为角度
        Deg2Rad = math.pi / 180.0
        Cx = math.cos(euler[0] / 2.0 * Deg2Rad)
        Cy = math.cos(euler[1] / 2.0 * Deg2Rad)
        Cz = math.cos(euler[2] / 2.0 * Deg2Rad)

        Sx = math.sin(euler[0] / 2.0 * Deg2Rad)
        Sy = math.sin(euler[1] / 2.0 * Deg2Rad)
        Sz = math.sin(euler[2] / 2.0 * Deg2Rad)

        # Maya默认旋转顺序是XYZ
        qX = Quaternion([Sx, 0.0, 0.0, Cx])
        qY = Quaternion([0.0, Sy, 0.0, Cy])
        qZ = Quaternion([0.0, 0.0, Sz, Cz])
        
        result = qX * qY * qZ
        return result

    def RotateDirection(self, direction):
        # 将方向向量转换为MVector
        if not isinstance(direction, om.MVector):
            direction = om.MVector(direction[0], direction[1], direction[2])
            
        result = self.Normalized()
        qDirection = Quaternion([direction.x, direction.y, direction.z, 0])
        resultDirection = result.Inversed() * qDirection * result
        return om.MVector(resultDirection.x, resultDirection.y, resultDirection.z)

    def Euler(self):
        # 四元数转欧拉角（角度）
        euler = [0.0, 0.0, 0.0]
        q = self.Normalized()

        # XYZ旋转顺序
        euler[0] = math.atan2(2 * (q.w * q.x + q.y * q.z), 1 - 2 * (q.x * q.x + q.y * q.y))
        euler[1] = math.asin(clamp(2 * (q.w * q.y - q.x * q.z), -1, 1))
        euler[2] = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))

        Rad2Deg = 180.0 / math.pi
        euler[0] *= Rad2Deg
        euler[1] *= Rad2Deg
        euler[2] *= Rad2Deg
        
        return euler

    @staticmethod
    def FromAxisAngle(axis, angle):
        # 角度转弧度
        angle_rad = angle * math.pi / 180.0
        
        # 将轴向量转换为MVector并归一化
        if not isinstance(axis, om.MVector):
            axis = om.MVector(axis[0], axis[1], axis[2])
        
        if axis.length() < 0.00001:
            return Quaternion.Identity()
            
        axis.normalize()
        
        sin_half = math.sin(angle_rad / 2.0)
        cos_half = math.cos(angle_rad / 2.0)
        
        return Quaternion([axis.x * sin_half, axis.y * sin_half, axis.z * sin_half, cos_half])

    @staticmethod
    def FromMQuaternion(mquaternion):
        return Quaternion([mquaternion.x, mquaternion.y, mquaternion.z, mquaternion.w])

    @staticmethod
    def Slerp(q1, q2, t):
        # 球面线性插值
        t = clamp01(t)
        q1 = q1.Normalized()
        q2 = q2.Normalized()
        
        dot = q1.x * q2.x + q1.y * q2.y + q1.z * q2.z + q1.w * q2.w
        
        # 如果点积为负，则取q2的反方向，保证走最短路径
        if dot < 0:
            q2.x = -q2.x
            q2.y = -q2.y
            q2.z = -q2.z
            q2.w = -q2.w
            dot = -dot
            
        # 处理非常接近的四元数
        if dot > 0.9995:
            result = Quaternion([
                q1.x + (q2.x - q1.x) * t,
                q1.y + (q2.y - q1.y) * t,
                q1.z + (q2.z - q1.z) * t,
                q1.w + (q2.w - q1.w) * t
            ])
            return result.Normalized()
            
        # 计算球面线性插值
        theta_0 = math.acos(dot)
        theta = theta_0 * t
        
        sin_theta = math.sin(theta)
        sin_theta_0 = math.sin(theta_0)
        
        s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
        s1 = sin_theta / sin_theta_0
        
        return Quaternion([
            s0 * q1.x + s1 * q2.x,
            s0 * q1.y + s1 * q2.y,
            s0 * q1.z + s1 * q2.z,
            s0 * q1.w + s1 * q2.w
        ])

# 四元数工具GUI
class QuaternionToolUI:
    def __init__(self):
        self.window_name = "quaternionToolWindow"
        self.title = "四元数工具"
        self.size = (400, 600)
        
        # 当前四元数
        self.current_quaternion = Quaternion()
        
        # 创建UI
        self.create_ui()
        
    def create_ui(self):
        # 如果窗口已存在，则删除
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
            
        # 创建窗口
        cmds.window(self.window_name, title=self.title, widthHeight=self.size)
        
        # 主布局
        main_layout = cmds.columnLayout(adjustableColumn=True, columnAttach=('both', 5), rowSpacing=10, columnWidth=self.size[0])
        
        # 标题
        cmds.text(label="Maya 四元数工具", font="boldLabelFont")
        cmds.separator(height=10, style='double')
        
        # 创建四元数部分
        cmds.frameLayout(label="创建四元数", collapsable=True, collapse=False)
        
        # 从欧拉角创建
        cmds.frameLayout(label="从欧拉角创建", collapsable=True, collapse=False)
        euler_layout = cmds.columnLayout(adjustableColumn=True)
        
        cmds.rowLayout(numberOfColumns=4, columnWidth4=(40, 80, 80, 80), adjustableColumn=4, columnAlign=(1, 'right'))
        cmds.text(label="欧拉角:")
        self.euler_x = cmds.floatField(value=0.0, precision=2)
        self.euler_y = cmds.floatField(value=0.0, precision=2)
        self.euler_z = cmds.floatField(value=0.0, precision=2)
        cmds.setParent('..')
        
        cmds.button(label="从欧拉角创建四元数", command=self.create_from_euler)
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 从轴角创建
        cmds.frameLayout(label="从轴角创建", collapsable=True, collapse=False)
        axis_angle_layout = cmds.columnLayout(adjustableColumn=True)
        
        cmds.rowLayout(numberOfColumns=4, columnWidth4=(40, 80, 80, 80), adjustableColumn=4, columnAlign=(1, 'right'))
        cmds.text(label="轴:")
        self.axis_x = cmds.floatField(value=0.0, precision=2)
        self.axis_y = cmds.floatField(value=1.0, precision=2)
        self.axis_z = cmds.floatField(value=0.0, precision=2)
        cmds.setParent('..')
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(40, 80), adjustableColumn=2, columnAlign=(1, 'right'))
        cmds.text(label="角度:")
        self.angle = cmds.floatField(value=0.0, precision=2)
        cmds.setParent('..')
        
        cmds.button(label="从轴角创建四元数", command=self.create_from_axis_angle)
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 从向量创建
        cmds.frameLayout(label="从向量创建", collapsable=True, collapse=True)
        vector_layout = cmds.columnLayout(adjustableColumn=True)
        
        cmds.rowLayout(numberOfColumns=5, columnWidth5=(80, 60, 60, 60, 60), adjustableColumn=5, columnAlign=(1, 'right'))
        cmds.text(label="四元数值:")
        self.quat_x = cmds.floatField(value=0.0, precision=4)
        self.quat_y = cmds.floatField(value=0.0, precision=4)
        self.quat_z = cmds.floatField(value=0.0, precision=4)
        self.quat_w = cmds.floatField(value=1.0, precision=4)
        cmds.setParent('..')
        
        cmds.button(label="从向量创建四元数", command=self.create_from_vector)
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 从两个方向创建
        cmds.frameLayout(label="从两个方向创建", collapsable=True, collapse=True)
        from_to_layout = cmds.columnLayout(adjustableColumn=True)
        
        cmds.text(label="起始方向:")
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 80, 80), adjustableColumn=3)
        self.from_x = cmds.floatField(value=1.0, precision=2)
        self.from_y = cmds.floatField(value=0.0, precision=2)
        self.from_z = cmds.floatField(value=0.0, precision=2)
        cmds.setParent('..')
        
        cmds.text(label="目标方向:")
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 80, 80), adjustableColumn=3)
        self.to_x = cmds.floatField(value=0.0, precision=2)
        self.to_y = cmds.floatField(value=1.0, precision=2)
        self.to_z = cmds.floatField(value=0.0, precision=2)
        cmds.setParent('..')
        
        cmds.button(label="从两个方向创建四元数", command=self.create_from_to_rotation)
        cmds.setParent('..')
        cmds.setParent('..')
        
        cmds.setParent('..')  # 退出创建四元数框架
        
        # 当前四元数显示
        cmds.frameLayout(label="当前四元数", collapsable=False)
        self.current_quat_text = cmds.textField(editable=False, text="0 0 0 1")
        cmds.setParent('..')
        
        # 四元数操作
        cmds.frameLayout(label="四元数操作", collapsable=True, collapse=False)
        
        # 旋转向量
        cmds.frameLayout(label="旋转向量", collapsable=True, collapse=False)
        rotate_layout = cmds.columnLayout(adjustableColumn=True)
        
        cmds.text(label="输入向量:")
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 80, 80), adjustableColumn=3)
        self.vec_x = cmds.floatField(value=1.0, precision=2)
        self.vec_y = cmds.floatField(value=0.0, precision=2)
        self.vec_z = cmds.floatField(value=0.0, precision=2)
        cmds.setParent('..')
        
        cmds.button(label="旋转向量", command=self.rotate_vector)
        
        cmds.text(label="旋转结果:")
        self.rotated_vector = cmds.textField(editable=False)
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 获取欧拉角
        cmds.frameLayout(label="获取欧拉角", collapsable=True, collapse=False)
        euler_out_layout = cmds.columnLayout(adjustableColumn=True)
        
        cmds.button(label="获取欧拉角", command=self.get_euler)
        self.euler_result = cmds.textField(editable=False)
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 应用到选中物体
        cmds.frameLayout(label="应用到选中物体", collapsable=True, collapse=False)
        apply_layout = cmds.columnLayout(adjustableColumn=True)
        
        cmds.button(label="应用旋转到选中物体", command=self.apply_to_selection)
        cmds.setParent('..')
        cmds.setParent('..')
        
        cmds.setParent('..')  # 退出四元数操作框架
        
        # 帮助信息
        cmds.frameLayout(label="帮助", collapsable=True, collapse=True)
        help_layout = cmds.columnLayout(adjustableColumn=True)
        
        help_text = """
四元数工具使用说明:

1. 创建四元数:
   - 从欧拉角创建(角度制)
   - 从轴角创建
   - 从四元数分量创建
   - 从两个方向创建旋转四元数

2. 四元数操作:
   - 旋转向量
   - 获取欧拉角
   - 应用旋转到选中物体

注意: 所有角度均为角度制(非弧度)
        """
        cmds.text(label=help_text, align="left")
        cmds.setParent('..')
        cmds.setParent('..')
        
        # 显示窗口
        cmds.showWindow(self.window_name)
    
    def create_from_euler(self, *args):
        x = cmds.floatField(self.euler_x, query=True, value=True)
        y = cmds.floatField(self.euler_y, query=True, value=True)
        z = cmds.floatField(self.euler_z, query=True, value=True)
        
        self.current_quaternion = Quaternion.FromEuler([x, y, z])
        cmds.textField(self.current_quat_text, edit=True, text=str(self.current_quaternion))
    
    def create_from_axis_angle(self, *args):
        x = cmds.floatField(self.axis_x, query=True, value=True)
        y = cmds.floatField(self.axis_y, query=True, value=True)
        z = cmds.floatField(self.axis_z, query=True, value=True)
        angle = cmds.floatField(self.angle, query=True, value=True)
        
        self.current_quaternion = Quaternion.FromAxisAngle([x, y, z], angle)
        cmds.textField(self.current_quat_text, edit=True, text=str(self.current_quaternion))
    
    def create_from_vector(self, *args):
        x = cmds.floatField(self.quat_x, query=True, value=True)
        y = cmds.floatField(self.quat_y, query=True, value=True)
        z = cmds.floatField(self.quat_z, query=True, value=True)
        w = cmds.floatField(self.quat_w, query=True, value=True)
        
        self.current_quaternion = Quaternion([x, y, z, w])
        cmds.textField(self.current_quat_text, edit=True, text=str(self.current_quaternion))
    
    def create_from_to_rotation(self, *args):
        from_x = cmds.floatField(self.from_x, query=True, value=True)
        from_y = cmds.floatField(self.from_y, query=True, value=True)
        from_z = cmds.floatField(self.from_z, query=True, value=True)
        
        to_x = cmds.floatField(self.to_x, query=True, value=True)
        to_y = cmds.floatField(self.to_y, query=True, value=True)
        to_z = cmds.floatField(self.to_z, query=True, value=True)
        
        from_dir = om.MVector(from_x, from_y, from_z)
        to_dir = om.MVector(to_x, to_y, to_z)
        
        self.current_quaternion = Quaternion.FromToRotation(from_dir, to_dir)
        cmds.textField(self.current_quat_text, edit=True, text=str(self.current_quaternion))
    
    def rotate_vector(self, *args):
        x = cmds.floatField(self.vec_x, query=True, value=True)
        y = cmds.floatField(self.vec_y, query=True, value=True)
        z = cmds.floatField(self.vec_z, query=True, value=True)
        
        vector = om.MVector(x, y, z)
        rotated = self.current_quaternion.RotateDirection(vector)
        
        result_text = "{:.4f} {:.4f} {:.4f}".format(rotated.x, rotated.y, rotated.z)
        cmds.textField(self.rotated_vector, edit=True, text=result_text)
    
    def get_euler(self, *args):
        euler = self.current_quaternion.Euler()
        result_text = "{:.2f} {:.2f} {:.2f}".format(euler[0], euler[1], euler[2])
        cmds.textField(self.euler_result, edit=True, text=result_text)
    
    def apply_to_selection(self, *args):
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning("没有选中物体")
            return
            
        euler = self.current_quaternion.Euler()
        for obj in selection:
            cmds.rotate(euler[0], euler[1], euler[2], obj, absolute=True)

# 创建并显示UI
def show_ui():
    ui = QuaternionToolUI()
    return ui

# 如果直接运行此脚本，显示UI
if __name__ == "__main__":
    show_ui() 