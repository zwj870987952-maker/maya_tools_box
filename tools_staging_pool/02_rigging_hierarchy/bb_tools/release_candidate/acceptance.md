# BB Tools 真实 Maya 验收（not_run）

仅使用新场景、绑定备份和临时文件，不在生产原件或个人启动脚本上试清理。验收不仅是面板成功打开：记录 Maya/Python 版本、按钮/输入、实际结果、Script Editor Error 和 Undo 行为。

1. 在交互 Maya Script Editor 用 `importlib.util.spec_from_file_location` 加载本目录 `launch_candidate.py`，调用其 `show_ui()`。检查 21 个主菜单图标、折叠、行列滑条、左右停靠、右键选项，确保中文/帮助显示、路径含空格时资源可找到。关闭已有原 BB 界面后测试候选。额外 autoSkirt/masterCreate/PerVert 的原完整界面通过 `runtime.show_member` 的清单路径启动。
2. 新建两个网格和关节，核对重命名全部模式、父/点/旋转/缩放约束、属性复制与连接、16 种控制器、颜色/组/形状合并、四种属性、曲线/CV/关节/毛囊、BS 与对称功能。检查已有动画、长 DAG/namespace、锁定/引用/实例预检，逐个观察 Undo/Redo 是否恢复。
3. 对真实 ADV 5.74 角色备份逐项检查肩、颈、手指、眼、髋、DRV、显示、嘴唇次级和眉；确认附带 `.ma` 资产加载正确，其他 ADV 版本单独记录结果，不默认支持。
4. 临时目录及引用备份内测试 FBX 面板原完整引用转换、Y/Z Up、BS/骨骼/locator 选项、断开和 Bake；核对移除旧引用与输入节点影响。没有最终文件导出按钮属于原脚本行为，不把引用转换当通用导出。
5. 新网格检验 QC 检查、设置、修复、默认值与完整帮助；把配置导出为新 `.bb` 文件，含中文、空格和引号的数据保存/加载往返；既有文件应拒绝覆盖，恶意 MEL 行应拒绝执行。配置菜单用本会话缓存，重启后从已保存文件重新导入。
6. 临时纹理副本测试 FileTextureManager 的 Copy/Move/Set、自动/手动目录、替换/前缀/后缀及全部分析/帮助。已有目的文件必须保留原字节，带空格路径正常；Move 后副本可恢复，Undo 仅恢复场景路径，不能恢复外部搬移。
7. 有蒙皮的简单模型测试权重转 deform、毛囊、softMod、SkinList、动态链与自动裙摆。核对会话临时 XML、所有关节权重、动态模拟/Bake、场景对象及中断状态；随包 XML 不应变化。
8. FixError 用合成的无害回调和虚构测试文件；绝不修改真实 `userSetup.py`。确认仅列出指定文件、用户选择才搬入已有隔离目录、校验恢复副本、拒绝覆盖；感染场景节点有独立可 Undo 清理，界面回调清理的恢复限制如文档说明。检查 PerVert 颜色清理、masterCreate、纠正形状、选择、历史和复制的各个按钮。
9. GUI、所有核心功能和实际所需组合均满意后，制作与最新 `promotion.json` 对应 fingerprint 的 acceptance JSON（`tool_id=bb_tools`, `passed=true`, `maya_version`, `accepted_by`, `accepted_at`, `candidate_sha256`）。先 `promote_candidate.py --candidate <本目录> --acceptance <json>` 预览，再附 `--apply` 执行文件、文档、测试与 `ALL_TOOL_CLASSES` 注册；转正后运行目标测试并在 `maya_toolkit.show_ui()` 验证面板。

本轮只完成候选准备和隔离检查。未经以上真实 Maya 验收，不执行晋级，不修改正式库。
