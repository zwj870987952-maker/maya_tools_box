# 真实 Maya 直验（not_run）

1. 用备份场景打开launch_candidate.show_ui()；检查完整两列表、计数、所有复选框/axis/version/prefix、设置窗、SSC/bake按钮、水印。
2. 添加多个对象为一组、不同namespace/同叶子、不同高亮范围（包含小数），检查列表数量必须配对，导出分组准确。untitled选择目录；已有文件追加序号且保prefix，不覆盖。
3. 导出ASCII/Binary、动画开关、skin/camera/triangulate/smooth等实际业务组合；再导入Maya/UE核对动画范围、法线、skin、axis/units。embeddedTextures与inputConnections有扩大内容影响，逐项记录。
4. 设置新JSON/dry/原两个版本配置加载；已有JSON拒绝覆盖、非法/mismatch/NaN拒绝后UI不部分应用。
5. 对临时joint关闭SSC，检查scale继承与一次Undo；对备份约束/骨架层级烘焙，检查值和外范围keys、Undo、选区/time/AutoKey恢复，引用/锁后行全表拒绝。
6. 导出前后分别记录FBX设置和animationStart/End、min/max四值、当前时间/选区/Undo；错误后也应恢复。跨格式不支持或插件失败如实记录，文件写入不能由Undo删除。
7. 实测满意后执行promotion，不把mayapy自动检查当真实GUI验收，候选保留池内。
