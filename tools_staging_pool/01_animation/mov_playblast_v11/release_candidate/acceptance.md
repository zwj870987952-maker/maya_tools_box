# 多相机MOV拍屏真人验收

仅在备份场景和新建临时输出目录验收；输出覆盖不能Maya Undo。mayapy里的viewport/QT拍屏是shim，不作为图像或音画验收。

1. 在真实Maya Python Script Editor运行候选：

```python
import runpy
tool = runpy.run_path(r"E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\mov_playblast_v11\release_candidate\launch_candidate.py")["load_tool"]()
print(tool.run(action="open_ui").to_dict())
```

2. 确认完整原窗口、单/多相机（含正交/当前view）、全选/反选、输出名/目录、缩放、音频偏移、增序、MP4/GIF、几拍一、覆盖、FFmpeg设置/刷新正常。打开窗口不创建Documents设置、shelf或另一原窗口；检查Script Editor无Fatal。
3. 在3..8整数测试范围做高分辨率单机MOV，确认实际图像、尺寸、连续6帧、首尾内容正确；MP4/GIF有正确文件。几拍一2/3检查每组首帧重复，末尾不足组仍补齐，尾时长可能延长，这是原规则。高模式scale不改变采图百分比。
4. 低模式QT/H.264，.5/.1/1缩放结果可播放；若本机codec不可用，记录实际错误，不能算通过。QT不支持几拍一，勾选时需明确拒绝或切回高模式。不把FFmpeg测试通过当QT可用。
5. 多相机加namespace、同短名camera/引用camera，生成私有UUID后缀文件，分别核对构图正确，拍完原viewport相机、时间、选择、AutoKey恢复；当前view也正确。其他modelPanel不被永久改。默认未选多机不允许API传多个实际camera。
6. 绑定一段测试音频，节点offset与手动正/负偏移组合，高/低都听验同步和片长。请求音频但没有有效文件必须拒绝；不改audio节点或真实文件。fps与Maya时序一致，低QT后音轨处理尤其需检查。
7. 同名MOV或仅同名MP4/GIF存在时，未勾覆盖与增序须整个预检拒绝，原内容保持。增序从_1选所有后缀均空闲的同名组；覆盖勾选后才允许替换，明确记录不可撤销。只用临时文件，别覆盖生产影片。失败第二相机/转码错误应报告已发布路径并保留它们、清掉自有临时目录。
8. FFmpeg设置验证版本、手动路径、切回PATH、会话保存提示；新增JSON导出/导入仅作用明确文件，重复目标默认拒绝覆盖。重启会话后导入恢复；没有自动Documents配置写入。刷新窗口不重复/不加载旧v9模块。
9. 运行inspect与dry_run，确认不拍屏、不运行转码、不创建输出/临时文件或改变view。模拟坏路径/坏音频/坏JPEG只用测试资产，真实错误可见、原目标不被失败转码破坏。

记录Maya/Python、viewport renderer、codec、FFmpeg版本及每项结果。通过并用户确认后按promotion.json映射与plans/staging_run/promote_candidate.py预制注册/面板晋级；本轮仅预览，未迁移正式库。
