# DOF Control v1.0 候选

Dirk Bialluch，2000 年原 MEL，头部允许自由分发并声明修改自负风险。完整 dofControl.mel 与 dofControl.xpm 原字节随 upstream，private runtime.mel 的参数/所有权适配差异见 dof_control_changes.diff；不依赖原文件的待整理路径。

用途是在相机下创建显示立方体，通过平移/缩放调相机焦距/fStop。原文件没有窗口，本候选增加轻量标准动作 UI，不替换渲染器的景深实现，也不自动开启 camera.depthOfField。

## 输入与接口

`dof_control_v1_0` / DofControlTool / category `animation`；统一 `run(dry_run=False, **kwargs)`、ToolResult、Schema、execute_tool。`inventory` 离线读取 catalog；`open_ui` 真实 GUI；`create` 接 cameras 的 camera shape 或其直接 transform，空数组使用当前选择，shape+transform 重复去重；只查直接 shape，不递归普通场景组。拒绝组件/通配符/歧义/实例化相机、引用/锁定相机及父节点、已有动画/连接/锁定 focusDistance/fStop、已有本工具记录、Undo 关闭。

`cleanup` / `set_template` 接明确 `record_ids` UUID 数组；未指定不自动扫全场景清理。`template` bool 默认 False，create 时可设 True，set_template 切 shape.template 画法；不隐藏相机或改 DepthOfField。

```python
preview = tool.run(dry_run=True, action='create', cameras=['shotCamera'])
result = tool.run(action='create', cameras=['shotCamera'], template=True)
uid = result.data['results'][0]['record_uuid']
tool.run(action='set_template', record_ids=[uid], template=False)
tool.run(action='cleanup', record_ids=[uid])
```

## 原算法、输出与影响

完整原 polyCube 无构建历史，tx/ty/rx/ry/rz 锁定；初始 tz=-原 focusDistance，sz=原 fStop，relative parent 到 camera transform，跟随相机。tz 同时连接 sx/sy，保持原负的 XY 缩放。完整 `tz → addDoubleLinear(input2=1) → reverse → camera.focusDistance`；sz→camera.fStop。默认厘米场景实测最终 focusDistance=-tz，sz=fStop；自动 unitConversion 随 graph 记录。原“ScaleZ=focus range”措辞不是物理焦深模型：实际是 fStop。其他单位、camera scale/父级变换、渲染器效果仍需实测。

真实 mesh shape 的 castsShadows/primaryVisibility/visibleInReflections/visibleInRefractions 关闭，符合原隐藏渲染意图；现代 renderer 自有 visibility 属性与实际渲染/Viewport 未验收。原渲染开关的合成 transform 路径改为真实 shape 路径，长 DAG/nameSpace 不影响生成独立私有 helper 名。不 force 覆盖任何旧连接。

输出 results 每台有 camera/cube/record_uuid/resources，含注意警告。network record 记录 token/Owner、camera UUID/message、原 focusDistance/fStop、cube 与 reverse/add/unitConversion/mesh 真 UUID 及实际相机源 plug 身份；重命名/另存重开后可查找。只改相机两个参数的连接和新增辅助；不写外部文件、不改播放区间/refresh/OGS。finally 恢复时间/选择/guard。MEL 私有过程需来源检查与内部 guard，dry_run 不 source、不建节点、不打键、不改选择。

cleanup 校验全部记录后先断开本 graph 的相机输出，恢复**创建前** focusDistance/fStop 数值，然后删 owned cube/mesh/reverse/add/unitConversion/network，保护 camera。它不会保留创建后 cube 编辑得到的焦距；希望保留该值请先记录，再清理后手动设回。外部后代/外部驱动/额外相机输出/接线变化/资源缺失/锁定/引用拒绝清理；cube 自建动画曲线属于后续外部输入，须明确解除后清理或 Undo，避免删掉别的动画。Maya材质和 objectSet membership 允许自动断开，集合/材质不删除。

所有场景操作用一个标准 Undo chunk；部分 MEL 失败输出错误及已记 record_uuid，可能部分写入，需立即 Undo，无自动回滚。cleanup/set_template 可 Undo。关闭窗口只关 UI，不能替代 cleanup。

## 复用、组合与证据

复用 core/context 标准 Undo、framework BaseMayaTool/ToolResult；本小型原 MEL 图保持完整，无未直验 core 抽象。可在相机运动工具完成后创建焦距控制器，但本项目未验收组合；相机已有焦距动画/rig 驱动需先决定接管方法，本工具直接拒绝。其他工具不得把 owned cube 当生产控制器迁移/删除。

普通 Python 2 项、Maya2025 隔离 6 项、临时正式布局注册/面板/Schema 与指纹通过：实际图值/四渲染flags/negative XY/DepthOfField不变、focus/fStop编辑、cleanup恢复与Undo/redo、namespace双相机/模板Undo、预检/锁/原动画拒绝、外部后代/额外连接拒绝、重命名保存重载和部分故障Undo。尚未真实 GUI/Viewport/render，prepared_unverified，转正必须按 acceptance.md 人工验收。
