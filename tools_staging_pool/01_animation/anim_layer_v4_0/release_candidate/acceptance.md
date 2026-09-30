# 真人验收：Anim Layer v4.0 整套编辑器

需要干净的交互 Maya、备份/临时场景和临时输出目录。原自定义许可/Autodesk 通知均保留；本轮仅本地候选，不声称公开分发授权。NoUI mayapy 通过不等于整套验收通过。

1. 启动候选外层网关：

```python
from pathlib import Path
candidate = Path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_layer_v4_0\release_candidate')
namespace = {'__name__': 'candidate_launch', '__file__': str(candidate / 'launch_candidate.py')}
exec(compile((candidate / 'launch_candidate.py').read_text(encoding='utf-8'), str(candidate / 'launch_candidate.py'), 'exec'), namespace)
tool = namespace['load_tool']()
window = tool.show_ui()
```

确认开网关未 source 原 MEL，四色按钮/版本/签名/参数 JSON/日志/原帮助图工作。NoUI 列表 33 global，全版列表 197；不是只有菜单启动器。

2. inventory 与 invoke dry_run：查签名、填写正确/错误 arguments；检查字符串/数组/数值/多层/时间区间、未知参数、缺资源。预检不改原键/选择/Undo，不创建 UI、不 source。BaseAnimation 查询 sentinel 在没有层节点时仍能查基础曲线。
3. 明确加载 NoUI、打开原工具菜单；检查所有原按钮及原内置图标。NoUI 名称不代表无桌面依赖，Channel Box/层面板/时间滑块须正常存在。验证重复 load 不重新 source，force_reload 明确重新加载。
4. 另一个干净 Maya 会话加载 full：观察 Channel Box/动画、渲染、显示层编辑器和扩展权重条/范围；Script Editor 查 source/编码/重定义/遗失 legacy render pass 错误。原文件有非 UTF-8 字节和 getLayerDisplayType global/local 重复定义，重点测试其加载与切页，不更改原文件掩盖失败。失败即记录 prepared_unverified，不转正。
5. 测试小型两个控制器、多个层、平移/旋转/通道高亮以及键/框选区间：创建层（0/1 rotate accumulation）、Channel Box 层、当前区间层、选层跨度层、零层键、最佳层/对象选择。对照原 readme 与帮助图，检查输入层、键、priority/父级/选择输出。
6. 用备份动画分别测试基础/叠加/覆盖提取、全部/选定对象快速与智能合并（fidelity 0/1、tolerance）、播放范围/区间烘焙、Euler filter。逐次记录删除层/成员、键/切线、世界姿态、锁定/静音状态、Undo 结果；每项回到原备份再测下一项。原 catchQuiet 警告必须检查实际结果，不能仅凭 ToolResult.success 判断动画正确。
7. 按过程目录测试完整编辑器的动画/渲染/显示层成员、权重/关键权重、层排序/锁定/静音/solo、改名、选择、legacy render pass/contribution map 与界面刷新。无法支持的当前 Maya 版本功能明确记录，保留原源不删成缩减版。
8. 原 UI 回调不经过新增框架预检，单独验证撤销与失败状态恢复；适配器 API 也测试一键 Undo、异常下 evaluation/refresh 恢复。disable/enable_viewport 保留明确开关作用需配对。MEL 定义/UI/options/scriptJobs/文件不是场景 Undo 保证；full→NoUI 不卸载 full 定义，重启干净 Maya 才作版本间对比。
9. 导出仅临时目录：直接 API animLayersSaveExportClbc 已存在路径应预检拒绝，新路径 dry_run 不建文件；正式执行验证目标文件。原 animLayersExport 对话框及后续 MEL 回调保留原行为，另测路径/覆盖提示；不用于真实资产输出。安装器作为归档，不执行修改 Shelf/scripts。
10. 填 actual Maya/Python 版本、许可/使用范围、验收人/日期、所有类别结果和复现步骤。可选择先不验收 full，但整套不能据此记通过；修复外层确定问题后重测，不自动删减第三方功能。

验收通过后只读预览晋级：

```powershell
python plans/staging_run/promote_candidate.py --candidate tools_staging_pool/01_animation/anim_layer_v4_0/release_candidate
```

将输出 candidate_sha256 填验收 JSON（passed=true、tool_id=anim_layer_v4_0、candidate_sha256、maya_version、date、accepted_by），再带 --apply --acceptance <文件> 完成完整 6 资源/代码/catalog/知识目录/tests 与注册合并。该操作是本地转正，不等于许可允许公开发布。更改候选后旧指纹验收失效。
