import unreal
import os
import shutil
import datetime
import subprocess

# 设置保存路径为桌面
base_save_path = os.path.join(os.path.expanduser("~"), "Desktop")
unreal.log(f"保存路径: {base_save_path}")

# 获取当前选中的资产
selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()

if not selected_assets:
    unreal.log_warning("未选择任何资产")
else:
    # 创建一个字典来跟踪每个UE资产文件夹的资产信息
    ue_folders = {}
    
    # 创建一个字典来存储每个文件夹的日志信息
    folder_logs = {}
    
    # 记录所有已处理的文件夹，即使没有成功的资产
    all_folders = set()
    # 记录所有创建的目标文件夹路径，用于最后打开
    created_target_folders = []
    
    # 先获取所有资产信息
    for asset in selected_assets:
        try:
            # 获取资产在UE中的完整路径
            asset_path = asset.get_path_name()
            # 获取资产名称
            asset_name = asset.get_name()
            
            # 分割路径获取资产在UE中的文件夹
            path_parts = asset_path.split('.')
            if len(path_parts) > 1:
                package_path = path_parts[0]  # 获取包路径
                # 从包路径中提取文件夹名
                if '/' in package_path:
                    path_components = package_path.split('/')
                    ue_folder = path_components[-2]  # 获取上一级文件夹名
                else:
                    ue_folder = "Root"  # 如果没有上级文件夹，使用"Root"
            else:
                ue_folder = "Unknown"
            
            # 记录所有处理过的文件夹
            all_folders.add(ue_folder)
            
            # 初始化该文件夹的日志信息
            if ue_folder not in folder_logs:
                folder_logs[ue_folder] = {
                    "success": [],  # 成功复制的文件
                    "missing_source": [],  # 找不到源文件的资产
                    "failed": []  # 处理失败的资产
                }
            
            # 获取资产导入数据
            import_data = asset.get_editor_property("asset_import_data")
            if import_data:
                # 获取源文件路径
                source_path = import_data.get_first_filename()
                
                if source_path and os.path.exists(source_path):
                    # 将资产信息添加到对应的UE文件夹分类中
                    if ue_folder not in ue_folders:
                        ue_folders[ue_folder] = []
                    
                    # 保存资产名称和源文件路径
                    ue_folders[ue_folder].append({
                        'asset_name': asset_name,
                        'source_path': source_path,
                        'asset_path': asset_path
                    })
                    unreal.log(f"找到资产: {asset_name}, 源文件: {source_path}, UE文件夹: {ue_folder}")
                else:
                    # 记录找不到源文件的资产信息
                    folder_logs[ue_folder]["missing_source"].append({
                        'asset_name': asset_name,
                        'asset_path': asset_path,
                        'source_path': source_path if source_path else "无源文件路径"
                    })
                    unreal.log_warning(f"源文件不存在: {source_path if source_path else '无源文件路径'}")
            else:
                # 记录没有导入数据的资产信息
                folder_logs[ue_folder]["missing_source"].append({
                    'asset_name': asset_name,
                    'asset_path': asset_path,
                    'source_path': "无导入数据"
                })
                unreal.log_warning(f"资产 {asset_name} 没有导入数据")
                
        except Exception as e:
            # 记录处理失败的资产信息
            if 'ue_folder' in locals():
                if ue_folder not in folder_logs:
                    folder_logs[ue_folder] = {
                        "success": [], "missing_source": [], "failed": []
                    }
                folder_logs[ue_folder]["failed"].append({
                    'asset_name': asset_name if 'asset_name' in locals() else "未知资产",
                    'asset_path': asset_path if 'asset_path' in locals() else "未知路径",
                    'error': str(e)
                })
            unreal.log_error(f"处理资产时出错: {str(e)}")
    
    # 处理所有文件夹，包括没有成功资产的文件夹
    for ue_folder in all_folders:
        target_folder = os.path.join(base_save_path, ue_folder)
        
        # 确保文件夹存在
        try:
            os.makedirs(target_folder, exist_ok=True)
            unreal.log(f"创建文件夹: {target_folder}")
            # 记录创建的目标文件夹
            created_target_folders.append(target_folder)
            
            # 复制文件（如果有可复制的资产）
            if ue_folder in ue_folders:
                for asset_info in ue_folders[ue_folder]:
                    try:
                        source_path = asset_info['source_path']
                        asset_name = asset_info['asset_name']
                        asset_path = asset_info['asset_path']
                        
                        # 获取源文件的扩展名
                        _, source_extension = os.path.splitext(source_path)
                        source_filename = os.path.basename(source_path)
                        source_name_without_ext = os.path.splitext(source_filename)[0]
                        
                        # 如果源文件名(不含扩展名)与资产名不同，则使用资产名重命名
                        if source_name_without_ext != asset_name:
                            target_filename = asset_name + source_extension
                            was_renamed = True
                        else:
                            target_filename = source_filename
                            was_renamed = False
                        
                        target_file = os.path.join(target_folder, target_filename)
                        
                        try:
                            shutil.copy2(source_path, target_file)
                            # 记录成功复制的文件信息
                            folder_logs[ue_folder]["success"].append({
                                'asset_name': asset_name,
                                'asset_path': asset_path,
                                'source_path': source_path,
                                'target_path': target_file,
                                'target_filename': target_filename,
                                'renamed': was_renamed
                            })
                            unreal.log(f"已复制{'并重命名' if was_renamed else ''}: {source_path} -> {target_file}")
                        except Exception as e:
                            # 记录复制失败的信息
                            folder_logs[ue_folder]["failed"].append({
                                'asset_name': asset_name,
                                'asset_path': asset_path,
                                'source_path': source_path,
                                'error': str(e)
                            })
                            unreal.log_error(f"复制文件失败: {str(e)}")
                    except Exception as e:
                        unreal.log_error(f"处理资产时出错: {str(e)}")
                        continue  # 继续处理下一个资产，不中断
            
            # 生成各种日志文件，只有当有对应的记录时才生成
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 1. 成功复制的文件日志
            if folder_logs[ue_folder]["success"]:
                success_log_path = os.path.join(target_folder, f"{ue_folder}_成功复制_{timestamp}.txt")
                try:
                    with open(success_log_path, 'w', encoding='utf-8') as log_file:
                        log_file.write(f"===== UE资产复制成功日志 =====\n")
                        log_file.write(f"文件夹: {ue_folder}\n")
                        log_file.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        
                        for idx, info in enumerate(folder_logs[ue_folder]["success"], 1):
                            log_file.write(f"{idx}. 资产名称: {info['asset_name']}\n")
                            log_file.write(f"   资产路径: {info['asset_path']}\n")
                            log_file.write(f"   源文件: {info['source_path']}\n")
                            log_file.write(f"   目标文件: {info['target_path']}\n")
                            log_file.write(f"   是否重命名: {'是' if info['renamed'] else '否'}\n\n")
                        
                    unreal.log(f"已生成成功复制日志: {success_log_path}")
                    
                    # 生成成功复制文件名单 - 不带序号
                    file_list_path = os.path.join(target_folder, f"{ue_folder}_名单_{timestamp}.txt")
                    with open(file_list_path, 'w', encoding='utf-8') as list_file:
                        list_file.write(f"===== 成功复制文件名单 =====\n")
                        list_file.write(f"文件夹: {ue_folder}\n")
                        list_file.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        list_file.write(f"总文件数: {len(folder_logs[ue_folder]['success'])}\n\n")
                        
                        # 列出完整路径，不带序号
                        for info in folder_logs[ue_folder]["success"]:
                            list_file.write(f"{info['target_path']}\n")
                    
                    unreal.log(f"已生成文件名单: {file_list_path}")
                    
                except Exception as e:
                    unreal.log_error(f"创建成功复制日志失败: {str(e)}")
            
            # 2. 找不到源文件的资产日志
            if folder_logs[ue_folder]["missing_source"]:
                missing_log_path = os.path.join(target_folder, f"{ue_folder}_源文件缺失_{timestamp}.txt")
                try:
                    with open(missing_log_path, 'w', encoding='utf-8') as log_file:
                        log_file.write(f"===== UE资产源文件缺失日志 =====\n")
                        log_file.write(f"文件夹: {ue_folder}\n")
                        log_file.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        
                        for idx, info in enumerate(folder_logs[ue_folder]["missing_source"], 1):
                            log_file.write(f"{idx}. 资产名称: {info['asset_name']}\n")
                            log_file.write(f"   资产路径: {info['asset_path']}\n")
                            log_file.write(f"   源文件路径: {info['source_path']}\n\n")
                        
                    unreal.log(f"已生成源文件缺失日志: {missing_log_path}")
                except Exception as e:
                    unreal.log_error(f"创建源文件缺失日志失败: {str(e)}")
            
            # 3. 处理失败的资产日志
            if folder_logs[ue_folder]["failed"]:
                failed_log_path = os.path.join(target_folder, f"{ue_folder}_处理失败_{timestamp}.txt")
                try:
                    with open(failed_log_path, 'w', encoding='utf-8') as log_file:
                        log_file.write(f"===== UE资产处理失败日志 =====\n")
                        log_file.write(f"文件夹: {ue_folder}\n")
                        log_file.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                        
                        for idx, info in enumerate(folder_logs[ue_folder]["failed"], 1):
                            log_file.write(f"{idx}. 资产名称: {info['asset_name']}\n")
                            log_file.write(f"   资产路径: {info['asset_path'] if 'asset_path' in info else '未知路径'}\n")
                            if 'source_path' in info:
                                log_file.write(f"   源文件路径: {info['source_path']}\n")
                            log_file.write(f"   错误信息: {info['error']}\n\n")
                        
                    unreal.log(f"已生成处理失败日志: {failed_log_path}")
                except Exception as e:
                    unreal.log_error(f"创建处理失败日志失败: {str(e)}")
            
        except Exception as e:
            unreal.log_error(f"创建文件夹或日志失败: {str(e)}")
            continue  # 继续处理下一个文件夹
    
    # 输出总结信息
    total_assets = len(selected_assets)
    total_folders = len(all_folders)
    total_success = sum(len(logs["success"]) for logs in folder_logs.values())
    total_missing = sum(len(logs["missing_source"]) for logs in folder_logs.values())
    total_failed = sum(len(logs["failed"]) for logs in folder_logs.values())
    
    unreal.log(f"处理完成! 总资产数: {total_assets}, 处理文件夹: {total_folders}, 成功复制: {total_success}, 源文件缺失: {total_missing}, 处理失败: {total_failed}")
    
    # 打开已创建的文件夹
    for folder_path in created_target_folders:
        try:
            if os.path.exists(folder_path):
                subprocess.Popen(f'explorer "{folder_path}"')
                unreal.log(f"已打开文件夹: {folder_path}")
        except Exception as e:
            unreal.log_error(f"无法打开文件夹: {folder_path}, 错误: {str(e)}")