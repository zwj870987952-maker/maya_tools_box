# 真实 Maya 验收（not_run）

1. 备份scene打开完整两版窗口，确认列表/清空/时间/步长/六flags/文件浏览/导出/新建材质，以及batch输入/浏览/执行。模块import不打开UI，不自动加载plugin或写文件。
2. 输出唯一临时带空格路径，加载导出的ABC到备份scene，核对真实动画/世界空间/UV/UVSets/colors/visibility/faceSets。测试step与各flag开关，含namespace和可见/隐藏模型。
3. 尝试既有目标、非法quote路径、组件/空或缺set/歧义根、stripNamespace重复根，全部拒绝，不覆盖，不导出旧选择。新建材质更换整模型材质，原face assignment覆盖符合预期，一次Undo精确恢复；引用/锁/实例拒绝。
4. 建立独立临时scene文件夹，两个含abc_export的合法scene，一个缺集，一个故意坏scene；dry明确未检查文件内容。execute真实mayapy逐scene出文件与失败清单，当前未保存scene仍完整，时间/选区/modified不变，成功文件保留。
5. 输出同stem .ma/.mb与大小写重名，batch preflight拒绝。测试worker timeout，检查只本次临时文件夹，避免误删其它数据。File导出/plugin加载无sceneUndo保证；scene材质有Undo。
6. 在生产资产备份验证参考/namespaces/多shape/per-face材质导出；跨版本与interactive callback均需实测。通过后记录Maya/插件版本和满意度，才按promotion注册并复验正式面板。
