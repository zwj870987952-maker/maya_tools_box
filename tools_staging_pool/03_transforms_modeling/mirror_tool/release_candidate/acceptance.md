# 真实 Maya 验收（not_run）

1. 在备份场景加载候选/显式 show_ui，核对左右标识、层级、三平面、三个模式、预检/执行和反馈，Script Editor 无 Error/Fatal Traceback。
2. 创建位置(2,4,6)、旋转(10,20,30)、缩放(2,3,4)的左右 transform，逐一九组合对照原公式。复制模式应复制局部旋转，另试不同父旋转/rotateOrder/pivot，不将 Euler 方案宣传为任意严格几何对称。
3. 同时选择左右两侧，应按操作前源值双向处理；选父层级，应按目标父子顺序忽略 shape。检查一 Undo/Redo、选区/时间/AutoKey/原 keys 保持。
4. 多 namespace 与重复短名使用精确匹配/明确 pairs；缺对侧、坏后行、锁/引用/动画驱动/实例/非正缩放/非均匀父链/offsetParentMatrix 拒绝前无写。生产 rig 拷贝静态版本测试，不自动解锁/删驱动。
5. 满意才运行 plans/staging_run/promote_candidate.py --candidate 本目录，先预览后按验收结果晋级；完整资源/知识/测试/面板注册已备好，当前仍留待整理池。
