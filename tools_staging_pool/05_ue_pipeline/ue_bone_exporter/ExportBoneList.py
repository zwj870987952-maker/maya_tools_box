# UE5 导出骨骼表脚本
# 使用方法：
# 1. 在 Content Browser 中选中骨骼网格体(Skeletal Mesh)
# 2. 在 UE5 菜单 Tools -> Execute Python Script 运行此脚本
# 3. 骨骼列表会保存到项目根目录

import unreal
import os

def export_bone_list():
    """导出选中骨骼网格体的骨骼名称列表"""
    
    # 获取选中的资产
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    if len(selected_assets) == 0:
        unreal.log_error("错误：请先在 Content Browser 中选中一个骨骼网格体！")
        return
    
    exported_count = 0
    
    # 加载骨骼修改器
    skeleton_modifier = unreal.SkeletonModifier()
    
    for asset in selected_assets:
        # 检查是否是骨骼网格体
        if not isinstance(asset, unreal.SkeletalMesh):
            unreal.log_warning(f"跳过 {asset.get_name()}（不是骨骼网格体）")
            continue
        
        skeletal_mesh = asset
        mesh_name = skeletal_mesh.get_name()
        
        # 设置骨骼网格体到修改器
        skeleton_modifier.set_skeletal_mesh(skeletal_mesh)
        
        # 获取所有骨骼名称
        bone_names = skeleton_modifier.get_all_bone_names()
        
        if len(bone_names) == 0:
            unreal.log_warning(f"无法获取 {mesh_name} 的骨骼信息")
            continue
        
        # 构建输出内容
        content_lines = [str(name) for name in bone_names]
        content = "\n".join(content_lines)
        
        # 保存到项目目录
        project_dir = unreal.Paths.project_dir()
        filename = f"{mesh_name}_BoneList.txt"
        full_path = os.path.join(project_dir, filename)
        
        # 写入文件
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            unreal.log(f"=== 导出成功 ===")
            unreal.log(f"骨骼网格体: {mesh_name}")
            unreal.log(f"骨骼数量: {len(bone_names)}")
            unreal.log(f"保存位置: {full_path}")
            exported_count += 1
            
        except Exception as e:
            unreal.log_error(f"保存失败: {str(e)}")
    
    if exported_count > 0:
        unreal.log(f"=== 共导出 {exported_count} 个骨骼表 ===")
    else:
        unreal.log_warning("没有成功导出任何骨骼表")

# 执行
export_bone_list()
