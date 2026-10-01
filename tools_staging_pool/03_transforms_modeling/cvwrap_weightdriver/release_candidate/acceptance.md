# 完整套件真实 Maya 验收

1. 新Maya会话、备份场景，记录Maya/Python/Qt/PyMel及三个插件版本。候选show_ui可开，status/dry_run不修改场景、选择、时间、Undo、插件、菜单或路径。缺插件明确失败；显式load_plugin匹配二进制，确认无autoload配置变动，不使用候选以外来源mgear/cvwrap。
2. 两个测试mesh按原有序选择创建cvWrap，逐项name/radius/new_bind_mesh/现有binding选项。移动driver检查真实变形、AE模板、paint与Undo；不同拓扑文件失败结果明确。原完整选项和rebind窗口所有控件/滑条响应，取消不执行；明确vertices/faces局部rebind不动其它区域，Undo恢复。
3. 临时目录导出、导入真实绑定并核对变形。已有目标拒绝、文件不受Undo；失败不覆盖旧文件。坏路径、引用、锁、歧义短名和实例拒绝。插件导入损坏文件仅在测试场景试，不使用生产绑定。
4. weightDriver完整编辑器：创建driver/driven、采样多pose、编辑/删除/插值、评估更新与AE控件。RBF Manager节点和JSON preset全流程、SDK Manager的导入/编辑/保存/加载及Qt兼容。输出新临时文件、已有RBF preset拒绝覆盖，记录Undo实际边界和Script Editor错误。
5. 显式mgear_menu，已有mGear菜单应拒绝；新会话完整菜单所有family可打开。实际Shifter classic/EPIC最小guide构建rig、Simple Rig、Skinning基本JSON/gSkin权重往返、Rigbits、Animbits、CFX、Crank、Anim Picker保存加载、Synoptic、Flex替换与Utilities各在备份测试场景运行。模板/80 UI/原图片和29占位菜单图均可找到，不依赖池外路径。菜单/Qt/插件/数据失败逐项记录，不把按钮能打开当算法通过。
6. 对scene写入和外部文件分别核对Undo/保存影响。旧gSkin基本pickle可读，含自定义或执行对象文件明确拒绝。上游其它文件对话框按原行为，勿选择已有真实输出。跨版本和生产rig规模另外实测；满意且无致命Traceback后，才执行晋级脚本注册面板。当前全包留待整理池，GUI验收not_run。
