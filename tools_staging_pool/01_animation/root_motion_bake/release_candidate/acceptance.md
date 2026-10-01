# Root Motion 真人 Maya 验收（not_run）

仅在备份动画场景，原始脚本不要直接import以免自动呼出未经适配的UI。

```python
import runpy
tool=runpy.run_path(r"E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py")['load_tool']()
tool.show_ui()
```

1. 原窗口/三个字段/选择与重新扫描按钮/六轴/保持偏移/时间范围/执行/成功对话框响应，Script Editor无致命错误；重复呼出不冲掉其他工具窗口。
2. Root、RootX_M、main三对象完整流程；不同轴与maintain_offset逐帧检查Root烘焙和新增offsetLayer起末帧。检查所有Root keyable属性及范围外关键帧影响，不能只看所选z轴。
3. center位于Root下时默认快照不会出现循环警告；独立质心用snapshot_center=False对照原直接约束语义；输入中心有pivot/所有RO/JO/RA/非均匀scale时逐项检查世界姿态。
4. 无ring只执行约束与烘焙，API/手动UI均可；有ring保持原世界位置/Euler差值语义，验证大角度旋转、层权重和插值，不能当成严格相对matrix。
5. 已有同名root_offsetLayer必须保留；新增层唯一；层flag/选择/time/autokey/namespace恢复；一次Undo/Redo恢复整个批次，.ma保存重开后动画/层可恢复。
6. 相似名字、多层namespace、重复Root/祖先交叠、多个自动候选、非法/锁定/引用Root、非animCurve驱动与已有层Root：明确拒绝而不半处理批次；只读引用输入不应创建引用编辑。
7. 高亮时间滑块与timeline/animation/explicit分别核对实际烘焙范围；没框选时报错。分数起止帧与sampleBy=1的末端行为在实际场景确认。
8. 故障或中断后检查临时约束/定位器/副本清理，已有对象不被删；失败已写动画按提示Undo。不覆盖任何文件，不运行Obsidian同步。

逐项记录Maya版本/结果，未通过修候选。真人通过后生成含tool_id/candidate_sha256/passed/maya_version/accepted_by/date的验收文件，先用plans/staging_run/promote_candidate.py --candidate 本目录预览清单，再按验收晋级；本轮不执行apply。
