# 真实Maya验收 not_run

1. 在备份场景、已打开真实Maya中用launch_candidate.load_tool().show_ui()；完整主toolbar/QPainter图标/多slider/右键动态模式防重/Workspace窗口打开。注意这是UI原型，动画按钮缺业务算法是原项目事实；确认这与预期一致再验收，不能以动画菜单出现判断算法可用。
2. main/Graph Editor独立位置、独立工具勾选、Classic/Beginner/Compact/Expert/新名称preset；自建right/left回切正确，重名不覆盖；左右居中/单行拖拽滚轮/原子换行/边缘尺寸，回弹计时器，UI双向同步，隐藏模式防重。GraphEditor顶部/菜单下/底部与关闭重开，主timeline/shelf/status/floating位置；Viewport原映射限制如实确认。
3. dry_run config/preset前后配置/scene nodes/选择/dirty/Undo不变，坏最后id/location/非bool/重复id全表拒绝；configure只改对应toolbar，existing UI实时更新。无场景/文件保存、无外部硬编码图标依赖。原历史截图不是本轮测试证据。
4. 两个套件脚本同时存在仍互不关闭；连续开关主/Graph/Workspace至少三次，close无残留插入控件或signal callback报错、旧计时器停止，重开保持session配置；共享多tab不隐藏其他tab，独立tab关闭恢复原高度可见性。原Qt构造离线通过不替代这些真实GUI操作。跨Maya/Qt/系统实测记录版本；满意后填写candidate_sha256、maya_version、accepted_by/date/passed=true才可执行预制promotion。
