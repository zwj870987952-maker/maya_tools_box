import maya.cmds as cmds
import maya.mel as mel

def unlock_and_freeze_transforms():
    """
    解锁选中物体的所有变换属性，然后冻结变换
    """
    # 获取当前选中的物体
    selected_objects = cmds.ls(selection=True)
    
    if not selected_objects:
        cmds.warning("请先选择至少一个物体")
        return
    
    for obj in selected_objects:
        try:
            # 定义需要解锁的变换属性
            transform_attrs = [
                "translateX", "translateY", "translateZ",
                "rotateX", "rotateY", "rotateZ",
                "scaleX", "scaleY", "scaleZ"
            ]
            
            # 选中物体
            cmds.select(obj)
            
            # 方法1：使用channelBoxCommand -unlock命令解锁所有变换属性
            mel.eval("channelBoxCommand -unlock;")
            
            # 方法2：使用CBunlockAttr逐个解锁属性（作为备选方案）
            for attr in transform_attrs:
                try:
                    mel.eval(f'CBunlockAttr "{obj}.{attr}";')
                except Exception as e:
                    print(f"使用CBunlockAttr解锁属性 {obj}.{attr} 时出错: {str(e)}")
            
            print(f"已解锁 {obj} 的变换属性")
            
            # 冻结变换
            cmds.makeIdentity(obj, apply=True, translate=True, rotate=True, scale=True)
            print(f"已冻结 {obj} 的变换")
        except Exception as e:
            print(f"处理 {obj} 时发生错误: {str(e)}")
    
    # 最后重新选中原来选中的所有物体
    cmds.select(selected_objects)
    print("操作完成，已重新选中原物体")

# 测试脚本
if __name__ == "__main__":
    unlock_and_freeze_transforms()