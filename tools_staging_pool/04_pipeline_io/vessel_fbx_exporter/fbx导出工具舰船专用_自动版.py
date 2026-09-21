import maya.cmds as cmds
import maya.mel as mel
import os

# 重置变换的默认参数设置（可根据需要修改）
RESET_TRANSLATE_X = 0
RESET_TRANSLATE_Y = 0
RESET_TRANSLATE_Z = 0
RESET_ROTATE_X = -90
RESET_ROTATE_Y = 0
RESET_ROTATE_Z = 0
RESET_SCALE_X = 1
RESET_SCALE_Y = 1
RESET_SCALE_Z = 1

def reference_exported_fbx(export_path, export_filename):
    """
    引用导出的FBX文件并高亮选择。
    """
    reference_namespace = os.path.splitext(export_filename)[0]
    try:
        cmds.file(export_path, reference=True, namespace=reference_namespace)
        print("Referenced: {} with namespace: {}".format(export_path, reference_namespace))
        
        # Retrieve and select the nodes under the new namespace
        referenced_nodes = cmds.namespaceInfo(reference_namespace, listOnlyDependencyNodes=True, dp=True)
        if referenced_nodes:
            cmds.select(referenced_nodes, r=True)
            print("Selected referenced nodes in namespace: {}".format(reference_namespace))
    except Exception as e:
        print("Failed to reference {}: {}".format(export_path, e))

def select_fbx_export_sets_only():
    """
    选择所有名称中包含 '_FBXExport' 的对象集本身，而不选择其中的对象。
    """
    # 获取所有对象集
    all_sets = cmds.ls(type='objectSet')
    
    # 初始化一个列表来存储匹配的对象集
    fbx_export_sets = []

    # 遍历所有对象集，寻找名称中包含 '_FBXExport' 的集
    for obj_set in all_sets:
        if '_FBXExport' in obj_set:
            fbx_export_sets.append(obj_set)
    
    # 确保仅选择对象集本身
    if fbx_export_sets:
        cmds.select(clear=True)  # 清除当前选择
        for fbx_set in fbx_export_sets:
            cmds.select(fbx_set, add=True, noExpand=True)  # 确保不展开集合选择
        print(f"选中了 {len(fbx_export_sets)} 个 '_FBXExport' 对象集。")
    else:
        print("没有找到包含 '_FBXExport' 的对象集。")

# 在选择对象之后调用 remove_namespaces
def remove_selected_namespaces():
   # 获取当前选中的对象
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("No objects selected.")
        return

    # 获取所有选中对象的名称空间
    namespaces = set()
    for obj in selected_objects:
        if ':' in obj:
            namespace = obj.rpartition(':')[0]
            namespaces.add(namespace)

    # 删除名称空间并合并到根名称空间
    for ns in namespaces:
        # 检查名称空间是否存在
        if cmds.namespace(exists=ns):
            try:
                cmds.namespace(removeNamespace=ns, mergeNamespaceWithRoot=True)
                print(f'Removed namespace: {ns}')
            except Exception as e:
                print(f'Failed to remove namespace {ns} due to: {e}')
                cmds.warning(f'Failed to remove namespace {ns}. Check the console for details.')

def import_references():
    references = cmds.file(q=True, r=True)
    for ref in references:
        try:
            cmds.file(ref, ir=True)
        except Exception as e:
            print(f"Failed to import reference {ref}: {e}")


def bake_animation_for_export_sets():
    all_sets = cmds.ls(type='objectSet')
    export_sets = [s for s in all_sets if '_FBXExport' in s]
    
    for sel_set in export_sets:
        objects = cmds.sets(sel_set, q=True)
        if not objects:
            continue

        # 选择这些物体
        cmds.select(objects, r=True)

        # 获取当前帧范围
        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)

        # 烘焙动画
        cmds.bakeResults(objects, t=(start_frame, end_frame), simulation=True)

        print(f"Baked animation for set: {sel_set}")

def rename_root_object():
    # 查找所有以 'root' 开头的对象
    root_objects = cmds.ls('root*')
    
    # 如果没有找到任何以 'root' 开头的对象，并且存在名为 'root' 的对象
    if not root_objects and cmds.objExists('root'):
        cmds.rename('root', 'root_001')
        print("Renamed 'root' to 'root_001'.")
        return
    
    # 如果找到了以 'root' 开头的对象
    if root_objects:
        # 提取现有对象名称中的数字序号
        existing_numbers = []
        for obj in root_objects:
            parts = obj.split('_')
            if len(parts) > 1 and parts[-1].isdigit():
                existing_numbers.append(int(parts[-1]))
        
        # 找到下一个可用的序号
        next_number = 1
        if existing_numbers:
            next_number = max(existing_numbers) + 1
        
        # 确保 'root' 存在并重命名
        if cmds.objExists('root'):
            new_name = f'root_{next_number:03d}'
            cmds.rename('root', new_name)
            print(f"Renamed 'root' to '{new_name}'.")


def export_fbx_from_selection_sets():
    scene_path = cmds.file(q=True, sn=True)
    scene_name = os.path.splitext(os.path.basename(scene_path))[0]
    scene_dir = os.path.dirname(scene_path)
    
    export_dir = os.path.join(scene_dir, 'FBXExport')
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    export_options = [
        "FBXExportSmoothingGroups -v true",
        "FBXExportSmoothMesh -v true",
        "FBXExportEmbeddedTextures -v true",
        "FBXExportBakeComplexAnimation -v true",
        "FBXExportShapes -v true",
        "FBXExportSkins -v true",
        "FBXExportCameras -v true",
        "FBXExportIncludeChildren -v true",
        "FBXExportInputConnections -v false",
        "FBXExportInAscii -v true",
        "FBXExportUpAxis y",
        "FBXExportFileVersion -v FBX202000",
        "FBXProperty \"Export|IncludeGrp|Animation\" -v true;"
    ]
    

    
   


    all_sets = cmds.ls(type='objectSet')
    export_sets = [s for s in all_sets if '_FBXExport' in s]
    
    if not export_sets:
        print("No _FBXExport sets found.")
        return

    # 弹出对话框获取关键字
    keyword = cmds.promptDialog(
        title='Export FBX',
        message='Enter keyword:',
        text=scene_name,  # 默认填入当前场景文件名
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
    )

    if keyword != 'OK':
        print("Export canceled.")
        return

    keyword = cmds.promptDialog(query=True, text=True)

    for sel_set in export_sets:
        objects = cmds.sets(sel_set, q=True)
        if not objects:
            continue
        
        cmds.select(objects, r=True)
    
        
        
        # Call the function
        remove_selected_namespaces()     
            
        # 去除 _FBXExport 后缀并替换关键字
        set_name = sel_set.replace('_FBXExport', '')
        export_filename = set_name.replace('AAA', keyword) + '.fbx'
        export_path = os.path.join(export_dir, export_filename)
        export_path = export_path.replace("\\", "/")
        
        for option in export_options:
            mel.eval(option)
        
        export_cmd = 'FBXExport -f "{}" -s'.format(export_path)
        try:
            mel.eval(export_cmd)
            print("Exported: {}".format(export_path))
                        
            # 新增：引用导出的FBX文件并选择
            #######reference_exported_fbx(export_path, export_filename)                                    
            

        except Exception as e:
            print("Failed to export {}: {}".format(export_path, e))
                        
        # 重命名根骨骼
        rename_root_object()


# 添加动画烘焙步骤
#########bake_animation_for_export_sets()

def bake_all_joints_sets():
    """
    识别场景中带All_joints字样的选择集，把该集成员选中并烘焙动画。
    """
    all_sets = cmds.ls(type='objectSet')
    joints_sets = [s for s in all_sets if 'All_joints' in s]
    
    if not joints_sets:
        print("没有找到包含 'All_joints' 的对象集。")
        return
    
    for joints_set in joints_sets:
        objects = cmds.sets(joints_set, q=True)
        if not objects:
            continue

        # 选择这些物体
        cmds.select(objects, r=True)

        # 获取当前帧范围
        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)

        # 烘焙动画
        cmds.bakeResults(
            objects,
            t=(start_frame, end_frame),
            simulation=True,
            sampleBy=1,
            sparseAnimCurveBake=False,
            removeBakedAttributeFromLayer=False,
            bakeOnOverrideLayer=False,
            preserveOutsideKeys=True,
            minimizeRotation=True
        )

        print(f"已为选择集 '{joints_set}' 中的对象烘焙动画。")

def reset_transform_sets():
    """
    识别场景中带Reset_Trans字样的选择集，把该集成员选中并在首帧清除所有动画帧，
    并修改他们的位移旋转缩放属性为预设值。
    """
    all_sets = cmds.ls(type='objectSet')
    reset_sets = [s for s in all_sets if 'Reset_Trans' in s]
    
    if not reset_sets:
        print("没有找到包含 'Reset_Trans' 的对象集。")
        return
    
    # 设置当前帧为首帧
    start_frame = cmds.playbackOptions(q=True, min=True)
    cmds.currentTime(start_frame)
    
    for reset_set in reset_sets:
        objects = cmds.sets(reset_set, q=True)
        if not objects:
            continue

        # 选择这些物体
        cmds.select(objects, r=True)
        
        # 对每个对象应用变换重置
        for obj in objects:
            # 删除所有动画帧
            cmds.cutKey(obj, clear=True)
            
            # 应用预设的变换值
            cmds.setAttr(f"{obj}.translateX", RESET_TRANSLATE_X)
            cmds.setAttr(f"{obj}.translateY", RESET_TRANSLATE_Y)
            cmds.setAttr(f"{obj}.translateZ", RESET_TRANSLATE_Z)
            
            cmds.setAttr(f"{obj}.rotateX", RESET_ROTATE_X)
            cmds.setAttr(f"{obj}.rotateY", RESET_ROTATE_Y)
            cmds.setAttr(f"{obj}.rotateZ", RESET_ROTATE_Z)
            
            cmds.setAttr(f"{obj}.scaleX", RESET_SCALE_X)
            cmds.setAttr(f"{obj}.scaleY", RESET_SCALE_Y)
            cmds.setAttr(f"{obj}.scaleZ", RESET_SCALE_Z)
            
            # 在首帧设置键
            cmds.setKeyframe(obj, time=start_frame)

        print(f"已重置选择集 '{reset_set}' 中对象的变换。")

# 第一步：处理All_joints选择集并烘焙动画
bake_all_joints_sets()

# 第二步：处理Reset_Trans选择集并重置变换
reset_transform_sets()

# 第三步：导入所有reference并执行后续导出步骤
import_references() 

# 调用函数以选择对象集
select_fbx_export_sets_only()

# Call the function
remove_selected_namespaces()                                                                                    
                                                                                                                           
# 调用函数
export_fbx_from_selection_sets()


