#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理Maya场景中含有中文路径或乱码引用路径的节点
"""

import os
import re
import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMaya

def is_path_valid(path):
    """
    检查路径是否有效（不包含中文和乱码）
    
    Args:
        path: 要检查的文件路径
        
    Returns:
        bool: 如果路径有效返回True，否则返回False
    """
    if not path:
        return True  # 忽略空路径
        
    # 检查是否包含中文字符
    if re.search(u'[\u4e00-\u9fff]', path):
        return False
        
    # 检查是否包含可能的乱码（无法用UTF-8正确解码的字符）
    try:
        path.encode('ascii')
    except UnicodeEncodeError:
        return False
        
    return True

def get_file_nodes():
    """
    获取场景中的所有文件节点
    
    Returns:
        list: 文件节点列表
    """
    # 获取所有文件节点类型
    file_node_types = [
        # 标准Maya纹理节点
        'file',                   # 标准纹理文件
        'psdFileTex',             # Photoshop文件纹理
        'substance',              # Substance纹理
        'layeredTexture',         # 分层纹理
        'movie',                  # 电影纹理
        'noise',                  # 噪波纹理（可能有文件路径）
        'mentalrayTexture',       # Mental Ray纹理
        
        # 图像平面和相关节点
        'imagePlane',             # 图像平面
        
        # Arnold 节点
        'aiImage',                # Arnold图像
        'aiStandIn',              # Arnold Stand-in
        'aiPhotometricLight',     # Arnold测光灯（可能引用IES文件）
        
        # V-Ray 节点
        'VRayMtl',                # V-Ray材质
        'VRayBitmap',             # V-Ray位图
        'VRayHDRI',               # V-Ray HDRI
        'VRayTexture',            # V-Ray纹理
        'VRayPtex',               # V-Ray Ptex纹理
        'VRayVolumeGrid',         # V-Ray体积网格
        'VRayLightIES',           # V-Ray IES灯光
        
        # Redshift 节点 
        'RedshiftSprite',         # Redshift精灵
        'RedshiftNormalMap',      # Redshift法线贴图
        'RedshiftBitmap',         # Redshift位图
        'RedshiftIESLight',       # Redshift IES灯光
        'RedshiftDomeLight',      # Redshift穹顶灯
        'RedshiftProxy',          # Redshift代理
        
        # RenderMan 节点
        'PxrTexture',             # Renderman纹理
        
        # 缓存和引用节点
        'reference',              # 引用节点
        'AlembicNode',            # Alembic缓存
        'gpuCache',               # GPU缓存
        'cacheFile',              # 几何缓存
        
        # 其他资源文件
        'audio',                  # 音频文件
        'fluidTexture2D',         # 2D流体纹理
        'fluidTexture3D',         # 3D流体纹理
        
        # 通用文件节点（可能被第三方插件使用）
        'envBall',                # 环境球
        'envCube',                # 环境立方体
        'envChrome',              # 环境铬合金
        'envSky',                 # 环境天空
        'envSphere'               # 环境球体
    ]
    
    # 尝试检测场景中已加载的渲染器，动态添加对应的节点类型
    renderers = {
        'RenderMan_for_Maya': ['PxrMultiTexture', 'PxrLayer', 'PxrPtexture'],
        'mtoa': ['aiVolume', 'aiLightProfile', 'aiMixTexture'],
        'vrayformaya': ['VRayLightDomeShape', 'VRayEnvironment', 'VRayVolumetricGrid'],
        'redshift4maya': ['RedshiftEnvironment', 'RedshiftVolume']
    }
    
    for renderer, nodes in renderers.items():
        try:
            if cmds.pluginInfo(renderer, query=True, loaded=True):
                file_node_types.extend(nodes)
        except:
            pass
    
    result = []
    for node_type in file_node_types:
        try:
            # 尝试获取该类型的所有节点
            nodes = cmds.ls(type=node_type)
            if nodes:
                result.extend(nodes)
        except Exception as e:
            # 忽略不存在的节点类型
            pass
                
    return result

def get_path_from_node(node):
    """
    从节点获取文件路径
    
    Args:
        node: Maya节点名称
        
    Returns:
        str: 文件路径，如果没有找到则返回None
    """
    path = None
    node_type = cmds.nodeType(node)
    
    try:
        # 根据节点类型获取路径属性
        # 标准Maya纹理节点
        if node_type == 'file':
            path = cmds.getAttr(f"{node}.fileTextureName")
        elif node_type == 'psdFileTex':
            path = cmds.getAttr(f"{node}.fileTextureName")
        elif node_type == 'substance':
            path = cmds.getAttr(f"{node}.filename")
        elif node_type == 'movie':
            path = cmds.getAttr(f"{node}.fileTextureName")
        elif node_type == 'noise' and cmds.attributeQuery('noiseTextureName', node=node, exists=True):
            path = cmds.getAttr(f"{node}.noiseTextureName")
        elif node_type == 'layeredTexture':
            # 分层纹理需要检查其连接的所有file节点
            connections = cmds.listConnections(f"{node}.inputs", source=True, destination=False)
            if connections:
                # 返回第一个连接的file节点的路径作为示例
                for conn in connections:
                    # 检查连接的节点是否有文件路径
                    sub_path = get_path_from_node(conn)
                    if sub_path:
                        path = sub_path
                        break
        elif node_type == 'mentalrayTexture':
            path = cmds.getAttr(f"{node}.fileTextureName")
            
        # Arnold 节点
        elif node_type == 'aiImage':
            path = cmds.getAttr(f"{node}.filename")
        elif node_type == 'aiStandIn':
            path = cmds.getAttr(f"{node}.dso")
        elif node_type == 'aiPhotometricLight' and cmds.attributeQuery('aiFilename', node=node, exists=True):
            path = cmds.getAttr(f"{node}.aiFilename")
            
        # V-Ray 节点
        elif node_type == 'VRayBitmap':
            path = cmds.getAttr(f"{node}.bitmap")
        elif node_type == 'VRayHDRI':
            path = cmds.getAttr(f"{node}.filepath")
        elif node_type == 'VRayTexture':
            path = cmds.getAttr(f"{node}.texturePath")
        elif node_type == 'VRayPtex':
            path = cmds.getAttr(f"{node}.ptexFile")
        elif node_type == 'VRayVolumeGrid':
            path = cmds.getAttr(f"{node}.file")
        elif node_type == 'VRayLightIES':
            path = cmds.getAttr(f"{node}.iesFile")
        elif node_type == 'VRayMtl':
            # 查找连接到VRayMtl的纹理节点
            for attr in ['diffuseMap', 'bumpMap', 'reflectionMap']:
                if cmds.attributeQuery(attr, node=node, exists=True):
                    conn_nodes = cmds.listConnections(f"{node}.{attr}")
                    if conn_nodes:
                        sub_path = get_path_from_node(conn_nodes[0])
                        if sub_path:
                            path = sub_path
                            break
            
        # Redshift 节点
        elif node_type == 'RedshiftSprite':
            path = cmds.getAttr(f"{node}.tex0")
        elif node_type == 'RedshiftNormalMap':
            path = cmds.getAttr(f"{node}.tex0")
        elif node_type == 'RedshiftBitmap':
            path = cmds.getAttr(f"{node}.tex0")
        elif node_type == 'RedshiftProxy':
            path = cmds.getAttr(f"{node}.fileName")
        elif node_type == 'RedshiftDomeLight':
            path = cmds.getAttr(f"{node}.tex0")
        elif node_type == 'RedshiftIESLight':
            path = cmds.getAttr(f"{node}.profile")
            
        # RenderMan 节点
        elif node_type == 'PxrTexture':
            path = cmds.getAttr(f"{node}.filename")
            
        # 缓存和引用节点
        elif node_type == 'reference':
            path = cmds.referenceQuery(node, filename=True)
        elif node_type == 'AlembicNode' or node_type == 'gpuCache':
            path = cmds.getAttr(f"{node}.cacheFileName")
        elif node_type == 'cacheFile':
            path = cmds.getAttr(f"{node}.cachePath")
            
        # 其他资源文件
        elif node_type == 'audio':
            path = cmds.getAttr(f"{node}.filename")
        elif node_type == 'imagePlane':
            path = cmds.getAttr(f"{node}.imageName")
        elif node_type == 'fluidTexture2D' and cmds.attributeQuery('textureName', node=node, exists=True):
            path = cmds.getAttr(f"{node}.textureName")
        elif node_type == 'fluidTexture3D' and cmds.attributeQuery('textureName', node=node, exists=True):
            path = cmds.getAttr(f"{node}.textureName")
            
        # 环境节点
        elif node_type in ['envBall', 'envCube', 'envChrome', 'envSky', 'envSphere']:
            if cmds.attributeQuery('imageFileName', node=node, exists=True):
                path = cmds.getAttr(f"{node}.imageFileName")
                
        # 尝试通用方法寻找文件路径属性
        else:
            # 尝试常见的文件路径属性名称
            common_path_attrs = [
                'fileTextureName', 'filename', 'imageName', 'texturePath', 
                'bitmap', 'tex0', 'fileName', 'filepath', 'file'
            ]
            
            for attr in common_path_attrs:
                if cmds.attributeQuery(attr, node=node, exists=True):
                    try:
                        path = cmds.getAttr(f"{node}.{attr}")
                        if path and isinstance(path, str) and len(path) > 0:
                            break
                    except:
                        continue
    except Exception as e:
        print(f"获取节点 {node} 路径时发生错误: {str(e)}")
        
    return path

def find_invalid_path_nodes():
    """
    查找所有包含无效路径（中文或乱码）的节点
    
    Returns:
        dict: 包含无效路径的节点，格式为 {node_name: path}
    """
    invalid_nodes = {}
    file_nodes = get_file_nodes()
    
    for node in file_nodes:
        path = get_path_from_node(node)
        if path and not is_path_valid(path):
            invalid_nodes[node] = path
            
    return invalid_nodes

def remove_invalid_path_nodes(nodes_to_remove=None, confirm=True):
    """
    删除包含无效路径的节点
    
    Args:
        nodes_to_remove: 要删除的节点列表，如果为None则查找所有无效节点
        confirm: 是否在删除前显示确认对话框
        
    Returns:
        list: 已删除的节点列表
    """
    if nodes_to_remove is None:
        invalid_nodes = find_invalid_path_nodes()
        nodes_to_remove = list(invalid_nodes.keys())
    
    if not nodes_to_remove:
        cmds.confirmDialog(title='结果', message='未找到包含中文或乱码路径的节点！', button=['确定'])
        return []
        
    if confirm:
        result = cmds.confirmDialog(
            title='确认删除',
            message=f'找到 {len(nodes_to_remove)} 个包含中文或乱码路径的节点，是否删除？',
            button=['是', '否'],
            defaultButton='否',
            cancelButton='否',
            dismissString='否'
        )
        
        if result != '是':
            return []
    
    # 执行删除操作
    deleted_nodes = []
    for node in nodes_to_remove:
        try:
            cmds.delete(node)
            deleted_nodes.append(node)
        except Exception as e:
            print(f"无法删除节点 {node}: {str(e)}")
            
    return deleted_nodes

def show_invalid_path_nodes():
    """
    显示包含无效路径的节点
    
    Returns:
        int: 找到的无效节点数量
    """
    invalid_nodes = find_invalid_path_nodes()
    
    if not invalid_nodes:
        cmds.confirmDialog(title='结果', message='未找到包含中文或乱码路径的节点！', button=['确定'])
        return 0
        
    # 创建结果窗口
    if cmds.window('invalidPathsWindow', exists=True):
        cmds.deleteUI('invalidPathsWindow')
        
    window = cmds.window('invalidPathsWindow', title='包含中文或乱码路径的节点', width=800)
    
    cmds.columnLayout(adjustableColumn=True, columnOffset=['both', 10])
    cmds.text(label=f'找到 {len(invalid_nodes)} 个包含中文或乱码路径的节点:', height=30, align='left')
    
    # 创建滚动列表
    cmds.scrollLayout(childResizable=True, height=400)
    cmds.columnLayout(adjustableColumn=True)
    
    # 添加节点信息
    for node, path in invalid_nodes.items():
        node_type = cmds.nodeType(node)
        frame = cmds.frameLayout(label=f'{node} ({node_type})', collapsable=True, marginWidth=5, marginHeight=5,
                                 collapse=False, borderStyle='etchedIn')
        cmds.columnLayout(adjustableColumn=True)
        cmds.textField(text=path, editable=False)
        
        cmds.rowLayout(numberOfColumns=2)
        cmds.button(label='选择节点', command=f'import maya.cmds as cmds; cmds.select("{node}", replace=True)')
        cmds.button(label='删除此节点', command=f'import maya.cmds as cmds; cmds.delete("{node}")')
        cmds.setParent('..')
        
        cmds.setParent('..')
        cmds.setParent('..')
    
    cmds.setParent('..')
    cmds.setParent('..')
    
    # 底部按钮
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(200, 200, 200), columnAlign3=['center', 'center', 'center'])
    cmds.button(label='刷新', command='import maya.cmds as cmds; cmds.deleteUI("invalidPathsWindow"); show_invalid_path_nodes()')
    cmds.button(label='全部选择', command=f'import maya.cmds as cmds; cmds.select({list(invalid_nodes.keys())}, replace=True)')
    cmds.button(label='全部删除', 
                command='import maya.cmds as cmds; remove_invalid_path_nodes(confirm=True); cmds.deleteUI("invalidPathsWindow")')
    cmds.setParent('..')
    
    cmds.showWindow(window)
    return len(invalid_nodes)

def create_ui():
    """
    创建工具UI界面
    """
    window_name = "cleanInvalidPathsWindow"
    
    # 如果窗口已存在，则删除
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
        
    # 创建窗口
    window = cmds.window(window_name, title="清理中文/乱码路径节点工具", width=400)
    
    cmds.columnLayout(adjustableColumn=True, columnOffset=["both", 10])
    
    cmds.text(label="此工具用于查找并删除场景中包含中文或乱码路径的节点", height=30, align="left")
    cmds.separator(height=10, style="none")
    
    cmds.button(
        label="查找中文/乱码路径节点", 
        height=40,
        command="show_invalid_path_nodes()",
        annotation="查找场景中所有包含中文或乱码路径的节点并显示"
    )
    
    cmds.separator(height=10)
    
    cmds.button(
        label="直接删除中文/乱码路径节点", 
        height=40,
        command="remove_invalid_path_nodes(confirm=True)",
        annotation="直接查找并删除所有包含中文或乱码路径的节点"
    )
    
    cmds.separator(height=20)
    cmds.text(label="作者：Claude AI", align="center")
    
    cmds.showWindow(window)

# 自动运行UI创建函数
# 无论是直接执行脚本还是作为模块导入，都会自动创建UI
create_ui()

# 如果是作为主程序运行，则什么也不做 (UI已经被创建)
if __name__ == "__main__":
    pass 