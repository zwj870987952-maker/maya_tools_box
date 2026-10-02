# 真实 Maya 直验（not_run）

1. 在备份场景准备中文/重音/ASCII缺失/替换字符路径、layeredTexture多层、可用渲染器/file/cache/audio/light节点，调用launch_candidate.show_ui()，检查主窗/结果窗/作者标注、刷新/路径详情/单选/全选。
2. 三种策略扫描应区分兼容性与真实缺失，空路径忽略。layered/VRayMtl多上游显示实际owner，不能自动删除容器。扫描/dry不加载插件或改scene/Undo。
3. 删除仅临时纹理/缓存/shape，检查连接影响、父transform保留、选区/时间/AutoKey、一次Undo/Redo；锁/default/引用owner/共享DAG实例后行应全表拒绝。
4. 使用独立原场景文件创建无edit顶层引用，默认删除拒绝；显式勾允许整引用后确认窗口列完整文件影响，取消不改。删除/Undo/Redo恢复load/RN名及lock，检查其他引用完整。nested/edited/源不可读拒绝。
5. 删除后重命名/占用名称/改来源文件等Undo异常只用可舍弃测试场景检查，不承诺此类变化可恢复。所有外部纹理/缓存/引用原文件始终不由本工具删除或改写。
6. 记录真实GUI、renderer和Maya版本结果；通过后才使用promotion转正，不提前改正式库。
