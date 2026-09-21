import maya.cmds as cmds
import os

def select_abc_export_set_members():
    # 检查是否存在名为 "abc_export" 的选择集
    if cmds.objExists('abc_export'):
        # 获取选择集成员
        members = cmds.sets('abc_export', query=True)

        # 选中选择集成员
        if members:
            cmds.select(members, replace=True)
            print 'Selected members of "abc_export" set:', members
        else:
            print 'No members found in "abc_export" set.'
    else:
        print 'Selection set "abc_export" not found in the scene.'
def export_selected_abc_with_options():
    # 调用选择集中的物体
    select_abc_export_set_members()

    # 获取当前选择的物体
    selected_objects = cmds.ls(selection=True)
    
    if not selected_objects:
        print 'No objects selected. Please select at least one object.'
        return

    # 获取当前文件路径和文件名
    current_file_path = cmds.file(query=True, sceneName=True)
    
    # 使用Python的标准库os.path来获取文件名和路径
    current_file_name, current_file_extension = os.path.splitext(os.path.basename(current_file_path))
    current_file_path = os.path.dirname(current_file_path)

    # 设置导出文件路径和文件名
    export_path = current_file_path.rstrip('\\')  # 移除文件名并确保路径以反斜杠结尾
    export_filename = current_file_name + '.abc'  # 使用新的文件名

    # 获取文件的起始帧和结束帧
    start_frame = int(cmds.playbackOptions(query=True, minTime=True))
    end_frame = int(cmds.playbackOptions(query=True, maxTime=True))

    # 构建导出选项
    export_options = {
        'frameRange': '{start} {end}'.format(start=start_frame, end=end_frame),  # 时间滑块范围
        'uvWrite': True,  # UV写入
        'writeColorSets': True,  # 写入颜色集
        'writeFaceSets': True,  # 写入面集
        'worldSpace': True,  # 世界空间
        'writeVisibility': True,  # 写入可见性
        'writeUVSets': True,  # 写入UV集
        'detail': True,  # 详细
    }

    # 构建导出命令，将选择的物体列表作为根物体传递进去
    root = ' '.join(['-root {}'.format(obj) for obj in selected_objects])
    export_command = '-frameRange {frameRange} -uvWrite {uvWrite} -writeColorSets {writeColorSets} ' \
                     '-writeFaceSets {writeFaceSets} -worldSpace {worldSpace} -writeVisibility {writeVisibility} ' \
                     '-writeUVSets {writeUVSets} -detail {detail} -file {file} {root}'.format(
                         frameRange=export_options['frameRange'],
                         uvWrite=export_options['uvWrite'],
                         writeColorSets=export_options['writeColorSets'],
                         writeFaceSets=export_options['writeFaceSets'],
                         worldSpace=export_options['worldSpace'],
                         writeVisibility=export_options['writeVisibility'],
                         writeUVSets=export_options['writeUVSets'],
                         detail=export_options['detail'],
                         file=(export_path + '\\' + export_filename),  # 使用反斜杠
                         root=root
                     )

    # 执行导出命令
    cmds.AbcExport(j=export_command, verbose=True)


def run_script_in_folder(folder_path):
    # 获取文件夹中所有的Maya文件
    maya_files = [f for f in os.listdir(folder_path) if f.endswith('.ma') or f.endswith('.mb')]

    if not maya_files:
        print 'No Maya files found in the specified folder.'
        return

    # 循环遍历每个Maya文件
    for maya_file in maya_files:
        file_path = os.path.join(folder_path, maya_file)

        # 打开Maya文件
        cmds.file(file_path, open=True, force=True)

        # 执行你的脚本
        export_selected_abc_with_options()

        # 关闭当前文件而不保存
        cmds.file(force=True, new=True)

    print 'Script execution completed for all Maya files in the folder.'
def browse_folder(*args):
    # 使用对话框让用户选择文件夹路径
    folder_path = cmds.fileDialog2(fileMode=3, caption="Select Folder")
    if folder_path:
        # 更新文本字段为选中的文件夹路径
        cmds.textField('folderPathTextField', edit=True, text=folder_path[0])

def execute_script(*args):
    # 从文本字段读取文件夹路径
    folder_path = cmds.textField('folderPathTextField', query=True, text=True)
    if os.path.isdir(folder_path):
        # 调用函数来处理文件
        run_script_in_folder(folder_path)
    else:
        cmds.warning("Invalid folder path. Please enter a valid folder path.")

def create_ui():
    # 如果窗口已经存在，先删除后重新创建
    if cmds.window("abcExportWindow", exists=True):
        cmds.deleteUI("abcExportWindow", window=True)

    # 创建新窗口
    cmds.window("abcExportWindow", title="ABC Export Tool", widthHeight=(300, 100))

    # 创建布局
    cmds.columnLayout(adjustableColumn=True)
    
    # 添加文本输入框
    cmds.textField('folderPathTextField', placeholderText="Enter folder path here or browse...")
    
    # 添加浏览按钮
    cmds.button(label="Browse", command=browse_folder)
    
    # 添加执行按钮
    cmds.button(label="Export ABC", command=execute_script)
    
    # 显示窗口
    cmds.showWindow("abcExportWindow")

# 调用函数创建UI
create_ui()
