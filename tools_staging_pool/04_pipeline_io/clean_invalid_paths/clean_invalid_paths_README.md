# Maya中文/乱码路径节点清理工具

## 简介
该工具用于查找并删除Maya场景中包含中文或乱码路径的节点。在工作流程中，有时会出现一些引用了中文路径或包含乱码的文件节点，这些节点可能导致项目在不同机器之间迁移时出现问题。本工具可以帮助您识别并清理这些节点。

## 功能
1. 扫描场景中的各种文件节点（纹理、引用、缓存等）
2. 识别包含中文字符或乱码的路径节点
3. 显示详细的节点信息，包括节点名称、类型和路径
4. 提供批量或单独选择/删除节点的功能

## 支持的节点类型
### 标准Maya纹理节点
- 标准纹理文件节点（`file`）
- Photoshop文件纹理节点（`psdFileTex`）
- Substance纹理节点（`substance`）
- 分层纹理节点（`layeredTexture`）
- 电影纹理节点（`movie`）
- 噪波纹理节点（`noise`）
- Mental Ray纹理节点（`mentalrayTexture`）

### Arnold 节点
- Arnold图像节点（`aiImage`）
- Arnold Stand-in节点（`aiStandIn`）
- Arnold测光灯节点（`aiPhotometricLight`）

### V-Ray 节点
- V-Ray材质（`VRayMtl`）
- V-Ray位图（`VRayBitmap`）
- V-Ray HDRI（`VRayHDRI`）
- V-Ray纹理（`VRayTexture`）
- V-Ray Ptex纹理（`VRayPtex`）
- V-Ray体积网格（`VRayVolumeGrid`）
- V-Ray IES灯光（`VRayLightIES`）

### Redshift 节点
- Redshift精灵（`RedshiftSprite`）
- Redshift法线贴图（`RedshiftNormalMap`）
- Redshift位图（`RedshiftBitmap`）
- Redshift IES灯光（`RedshiftIESLight`）
- Redshift穹顶灯（`RedshiftDomeLight`）
- Redshift代理（`RedshiftProxy`）

### RenderMan 节点
- Renderman纹理（`PxrTexture`）

### 缓存和引用节点
- 引用节点（`reference`）
- Alembic缓存节点（`AlembicNode`）
- GPU缓存节点（`gpuCache`）
- 几何缓存节点（`cacheFile`）

### 其他资源文件节点
- 音频节点（`audio`）
- 图像平面节点（`imagePlane`）
- 2D流体纹理（`fluidTexture2D`）
- 3D流体纹理（`fluidTexture3D`）

### 环境节点
- 环境球（`envBall`）
- 环境立方体（`envCube`）
- 环境铬合金（`envChrome`）
- 环境天空（`envSky`）
- 环境球体（`envSphere`）

此外，本工具还会动态检测场景中已加载的第三方渲染器插件，并支持其对应的文件节点类型。

## 安装方法
1. 下载`clean_invalid_paths.py`文件
2. 将文件放置在Maya的脚本目录中，例如：
   - Windows: `文档\maya\scripts\`
   - Mac: `~/Library/Preferences/Autodesk/maya/scripts/`
   - Linux: `~/maya/scripts/`

## 使用方法
### 方法1：直接在脚本编辑器中执行
1. 打开Maya
2. 打开脚本编辑器（Windows > General Editors > Script Editor）
3. 在Python选项卡中，使用下面任一方法：
```python
# 方式1：直接执行脚本文件 (推荐)
execfile('D:/path/to/clean_invalid_paths.py')  # Windows路径示例，请替换为您的实际路径

# 方式2：导入模块 (导入时会自动运行)
import clean_invalid_paths
```

### 方法2：创建Maya架子工具按钮
1. 打开Maya的工具架编辑器
2. 新建一个按钮，并在Python命令区域输入：
```python
# 直接执行脚本
execfile('D:/path/to/clean_invalid_paths.py')  # 请替换为您的实际脚本路径

# 或者：导入模块 (导入时会自动打开界面)
import clean_invalid_paths
```
3. 点击保存，即可在工具架上使用该工具

## 工具使用流程
1. 点击"查找中文/乱码路径节点"按钮，工具会扫描场景并显示找到的节点列表
2. 在弹出的窗口中，您可以：
   - 查看每个节点的详细信息
   - 选择单个节点
   - 删除单个节点
   - 选择所有节点
   - 删除所有节点
3. 或者直接点击"直接删除中文/乱码路径节点"按钮，工具会扫描并询问是否删除所有找到的节点

## 注意事项
- 删除节点前，请确保它们不是场景中必要的部分
- 建议在删除节点前先进行场景备份
- 某些引用节点的删除可能会影响场景中的其他元素

## 作者
Claude AI