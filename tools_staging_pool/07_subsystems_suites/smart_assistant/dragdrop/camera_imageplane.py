import maya.cmds as cmds
import os

def create_camera_with_sequence(folder_path):
    # 获取图片序列中的第一张图片
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.bmp'))]
    if not images:
        cmds.confirmDialog(title='提示', message='文件夹内无图片序列', button=['OK'])
        return
    images.sort()
    first_image = os.path.join(folder_path, images[0])

    # 创建新相机
    camera_name = cmds.camera(name='bg_cam')[0]
    # 创建图像平面
    image_plane_name = cmds.imagePlane(camera=camera_name, showInAllViews=True, width=10, height=10)[0]
    # 设置图像平面路径
    cmds.setAttr(f"{image_plane_name}.imageName", first_image, type="string")
    # 打开图像序列选项
    cmds.setAttr(f"{image_plane_name}.useFrameExtension", 1)
    # 只在当前相机显示
    cmds.setAttr(f"{image_plane_name}.displayOnlyIfCurrent", 1)
    # 相机可见性隐藏
    cmds.setAttr(f"{camera_name}.visibility", 0)

    # 创建新窗口并显示相机视图
    window_name = 'Custom_View_Window'
    counter = 1
    while cmds.window(window_name, exists=True):
        window_name = f'Custom_View_Window{counter}'
        counter += 1
    cmds.window(window_name, title='Custom View Window')
    pane_layout = cmds.paneLayout()
    model_panel = cmds.modelPanel()
    cmds.modelEditor(model_panel, edit=True, allObjects=False, imagePlane=True, grid=False)
    cmds.showWindow(window_name)
    cmds.modelPanel(model_panel, edit=True, camera=camera_name)
    cmds.modelEditor(model_panel, edit=True, camera=camera_name) 