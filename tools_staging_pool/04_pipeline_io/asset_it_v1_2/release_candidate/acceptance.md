# AssetIt 原套件真实验收（not_run）

1. 核对AssetIt EULA及个人使用条件，在支持PySide2/shiboken2/PyMel/Arnold的真实Maya版本、备份scene/库测试。import候选不导入nativeUI、不移动原文件、不创建shelf或写真实偏好。
2. Adapter清单290图库模型、图与metadata显示准确，额外3份创建模板scene不当图库模型；metadata范围拒绝..和symlink逃逸。试1个原模型独占namespace导入/scale/group、时间selection/AutoKey、一次Undo以及所有DG、namespace；不存在namespace方可重用，不共享原材质网络或执行scriptNodes。
3. 新建空安装父目录，install dry不创建file；fresh install只新复制code与library、配置指向独立副本，原包SHA保持；已有install立即拒绝。自定义非原Maya版本路径可备份复制但不能假称可原版启动。
4. 原完整窗口以原version/scripts路径打开，验证图库、搜索、主/副标签、收藏、Info、主题/尺寸/点击模式、导入/参考/五放置模式/拖拽/replace、缩放等；检查旧作者贴图路径和Arnold支持。原始225函数与全部资源保留，但这些原GUI操作尚未自动通过。
5. 单资产保存/多scene/多文件创建、缩略图相机/renderSetup与HDR材质、Metadata/Rename/Delete/收藏均用专门备份库，检查所有输出与场景变化。原Delete直接递归删文件及文件写不可sceneUndo，记录效果；关窗fixedname cleanup/job不得误删其它资产，试已有同名thumbnail node时入口拒绝。
6. 收集Script Editor fatal errors、各button/drag/slider响应、版本/许可/满意度；完整实际通过后才按promotion晋级并重新从正式面板测试。
