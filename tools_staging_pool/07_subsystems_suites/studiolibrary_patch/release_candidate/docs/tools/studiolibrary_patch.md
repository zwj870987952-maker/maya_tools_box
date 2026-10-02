# Studio Library PlusPatch 完整待验候选

保留用户17个原文件精确SHA归档，完整世界空间姿态/动画、Save/Load widgets、中文菜单/表单/历史版本、ModernDark CSS；补齐官方 krathjen/studiolibrary 固定提交 d2173f64460f3fa413ebb3696c28efacc60ef0dd 的257文件（StudioLibrary 2.21.7、studioqt/studiovendor/mutils/studiolibrarymaya、字体/图标/UI/XML/配置及 LGPL3/各嵌入组件通知）。vendor/dependency_provenance.json记录逐文件SHA及公开CDN下载来源，全部未来正式目录自包含，第三方库保留模块名和许可。candidate native修改源与精确依赖原档可对比，未推定原自有扩展有另行公开授权。

默认inspect/validate不导入Studio/Qt，不注册hooks、启动callback或写cache；install_extension/show_ui才显式激活。若用户先加载另一个Studio Library/mutils/Qt shim，明确拒绝混用，需新Maya会话加载本候选。完整库窗口 name=MTB_StudioLibraryPlusPatch，选择已有资产root，禁用本窗口更新检查，不修改系统安装、userSetup；原有标准pose/anim/set/mirror item通过原config注册，扩展增加WPose/WAnimation。世界姿态保持匹配、父层级优先、blend/key/mirrorTable/additive，世界动画保持完整non-world attrs、replace/merge/insert、自定义SaveWidget和采样收集器。高级镜像/名称替换/连接bake选项保留完整原GUI；公开API使用显式objects以避免不明确目标。

API类 StudioLibraryPatchTool，actions见Schema：inspect、show/close_ui、install/uninstall_extension、capture/save/load_pose与animation、apply_theme、install/uninstall_theme、repair_cache、set_language、show_history。frame_start/end/sample_by正有限与样本数量上限，JSON重复key/非有限值/不正确matrix/向量/时间次序拒绝，1–4096精确非wildcard transforms，全部目标锁定/外部非animCurve驱动先检，坏末项不会先cutKey。world捕获时间/选择恢复在Base UndoChunk内；load返回native failed/cancelled即fail，不能把半成功称全通过。底层UI world入口同样加数据/目标预检，不自动覆盖锁轴；生产约束/joint/shear/负scale/跨rotateOrder的最终匹配仍须真实验收。

save仅已有parent的新绝对.wpose/.wanim资产：标准pose.json与world_pose.json，或完整mutils Animation原生anim.ma/pose.json及world_transform.json；不是仅world JSON壳。异常保留本次新建的部分资产供恢复，不能scene Undo文件写入。原GUI safeSave可明确覆盖资产并生成.history/v####只读虚拟item：覆盖前完整snapshot与历史移入同卷自有stage；失败重建整个原资产+历史，失败半成品留stage，不只恢复历史。历史合并遇到同名版本拒绝并留恢复stage，不删除旧版本；symlink/未知stage拒绝。成功后历史版本与元数据保留原时间/类型，原base删除到trash和外部保存不由scene Undo撤销，需备份库验收。

ModernDark在候选自有窗口内用Theme.options解析CSS所有颜色/资源/DPI token；apply_theme不改磁盘或外来窗口。standalone install/uninstall_theme须明确外部resource_path（css/default.css已存在、非symlink、不可本bundle）：先exclusive精确备份+hash核验+receipt，再同卷atomic换CSS；已有receipt只允许同内容重入，外部修改或备份损坏拒绝卸载、不覆盖用户变动；restore原CSS，保留backup供检查。不再备份失败仍覆盖、不全局热重载/自动saveSettings。主题、资产、QSettings、cache均外部写入，不能Maya Undo；set_language/show_history反向动作恢复偏好。

repair_cache仅显式自有窗口，数据库必须chosenroot内，先精确备份；扫描/旧cachedpath限定root，不自动修复所有实例。安装hook记录每class原callable/Field/item注册，失败回滚，uninstall只还原自身仍持有的函数和item，foreign后安装wrapper拒绝强覆盖。关闭UI不等同卸载扩展；使用uninstall_extension明确撤hooks。组合：标准pose和动画可衔接时间/关键帧整理工具；不是仅静态import就证明复杂rig跨工具链成功。

离线history/theme恢复与外部改动拒绝、Schema/defaultinspect纯导入及未来完整layout检查；mayapy世界捕获/保存/加载/一次Undo与坏末项预检，单独Qt核验基础组件及原integration接口。均不替代真实Maya GUI；全部真实窗口/交互/标准和扩展资产生产rig/镜像/cache/覆盖历史/跨版本为not_run，验收前不迁正式。
