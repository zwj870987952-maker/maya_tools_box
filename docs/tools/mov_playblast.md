# mov_playblast：多相机MOV拍屏与MP4/GIF候选

原v11.1用户脚本完整43类方法/7全局函数及两个Python版本、检查安装.bat共3资源字节保留。UTF8主版作为转换来源，alt的GB18030原字节归档.py.original；原始声明不等于编码实情。未附独立再分发许可，本轮只作用户本地整理，未发布。所有原资源及完整业务/原生cmds UI在payload内，修改对照mov_playblast_changes.diff。现有core/正式工具无等价多相机拍屏与编码流水线；只复用BaseMayaTool/ToolResult/Undo，不改正式core。

保留高分辨率JPG序列→MOV、低分辨率原生QT/H.264→MOV，单/多相机、正交相机/当前view、输出命名、增序、覆盖、音频、MP4/GIF、图像序列几拍一及完整FFmpeg设置/刷新窗口。安装bat/Maya drop shelf写入器不执行，原import即开UI移除，候选启动显式open_ui，窗口/设置窗口使用私有名称。

## 调用协议

tool_id=mov_playblast，category=animation，version=11.1-candidate.1。

| action | 必要参数/效果 |
| --- | --- |
| inspect（默认） | 返回会话FFmpeg设置、PATH发现结果，读而不运行进程 |
| export | 已存在output_dir绝对本地目录、basename；mode=images/qt，cameras空→当前viewport，多相机需multi_camera=true；生成MOV，可附convert_mp4/convert_gif |
| encode_images | image_folder已存在，capture/renamed_capture.整数.jpg，fps>0，output_dir/basename；读源复制到自有临时序列后MOV编码 |
| convert_mp4 | source_file现有非空媒体、output_dir/basename；libx264 medium crf23、AAC128k |
| convert_gif | 同上加fps、width、height；原fps/scale/lanczos滤镜 |
| ffmpeg_version | 显式执行FFmpeg-version，超时最多30秒 |
| open_ui | 真实Maya界面，完整原生窗口，无自动用户配置文件写入 |
| settings_export/import | 明确settings_file.json；导入验证后更新会话，导出受overwrite保护 |

参数Schema为完整字段；实际校验由validate执行，框架不自动校验Schema。overwrite默认False，increment默认False且开启时始终从_1起，与原增序规则一致；同时检查一组MOV/MP4/GIF，某个衍生文件已存在也不默默覆盖。multi_camera文件后缀由清洗相机label+UUID前8位生成，避免namespace、DAG路径或同名相机碰撞；原直接把camera字符串拼路径的规则已改变。单相机无suffix。

export start/end默认播放范围int截断，显式必须±1000000整数；范围≤10000帧，总相机帧≤100000。width/height=0使用defaultResolution，实际1..8192；fps=0读取Maya API2 UI时间单位真实fps。没有强制改场景时间单位。scale=.1..1、保留原1位小数规则，只影响QT百分比，images仍100%。hold默认1，images支持2..10；源每组取首帧复制hold次，末尾不足一组仍补齐组（原行为）；QT不支持几拍一，明确拒绝。序列按负/正整数帧排序，输入只读且最多20000张唯一编号JPG。

include_audio=False默认；开启可用audio_node、audio_file或当前timeline绑定audio，绑定节点offset-start加audio_offset_frames，换为秒送FFmpeg。相对节点文件路径按场景目录解析。请求音频但没有有效文件报失败，不偷偷改为无声。QT新增使用图像同一规则音频复用/偏移，原低模式未使用手动偏移现已生效；Qt先出无声临时MOV后FFmpeg复用视频并加AAC，不改audio节点，fps需与拍屏时序一致。没有制作音频轨或口型实测质量保证。

ffmpeg_path默认PATH发现，明确路径必须现有可执行文件；不下载/安装。超时默认600秒，范围1..3600，shell=False、返回码/错误尾部检查，Windows隐藏进程窗口。只有真正转码才需要FFmpeg；QT无音频且无衍生转换仍取决于Maya QT codec可用性。高模式libx264 yuv420p补齐偶数宽高，可比原分辨率多1像素；GIF保持请求缩放尺寸，未承诺跨版本或所有视频编码。

## 只读与输出影响

validate/dry_run仅读参数/节点/实际cameraShape/实例/范围/音频路径/FFmpeg文件存在/全部输出冲突，不调用playblast、FFmpeg、viewer，不建目录/不写文件、不改时间/选择/AutoKey/当前相机。模块import不创建UI。相机可以是引用中的camera，因为只读其信息与切本viewport，不改引用节点；实例camera拒绝。实际capture需要真实GUI，batch明确拒绝。

临时目录只在明确输出目录内创建，验证解析后父目录与私有prefix，执行期间登记所有权；每相机采图/转换与后续衍生文件全部在私有临时目录。结果非空且FFmpeg成功后才发布；未覆盖授权以同文件系统hardlink原子创建，已授权覆盖先核对预检签名未改变再os.replace。需支持hardlink的输出文件系统（本机NTFS隔离验证）；不支持则报失败，不偷偷改为覆盖。相机切换/时间/选择/AutoKey无论成功失败均分别尝试恢复；某个恢复失败不会阻止其他恢复尝试，错误会报告。

输出/覆盖媒体和JSON属于外部文件，**Maya Undo不能恢复**；BaseMayaTool仍标准chunk，不把文件输出宣称为可撤销。按相机发布，前一相机已发布后后一相机失败，结果fail.data.completed_files列出已产生文件；不会自动删除这批已交付文件或恢复被明确覆盖的旧文件。临时文件finally清理。API从不启动播放器；UI拍屏按钮完成后按原行为打开MOV播放器。窗口“打开路径”只打开已有目录，不自动创建。旧capture/rename/cleanup内部助手保留完整原实现，但禁止在标准export事务之外绕过范围/自有临时目录保护；标准流水线使用参数化media/runtime实现。

原Documents/playblast_tool_settings.json自动创建/读写改为会话设置；设置保存明确提示本次会话，跨会话通过新增导入/导出JSON按钮或标准API。不是原旧version/last_updated四字段格式的自动迁移；新JSON只有ffmpeg_mode/ffmpeg_custom_path，修改应先备份。未写Documents、shelf、userSetup、注册或正式库。

dry输出规划outputs（含before签名）与真实参数；inspect返回settings/ffmpeg_found；媒体写入返回files/action；设置导入返回settings；ffmpeg_version返回path/version；UI返回ui_open。部分失败data.completed_files/external_undo=False，errors包含原因，warnings注明文件不可撤销。FFmpeg缺失/codec失败/源坏数据/权限/路径冲突/硬链接不支持等如实报错。

## 示例与组合

转正后：

```python
import maya_toolkit
args = {"action": "export", "mode": "images", "output_dir": r"E:\renders\review", "basename": "shot_010", "cameras": ["shotCamera"], "convert_mp4": True}
preview = maya_toolkit.execute_tool("mov_playblast", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("mov_playblast", args)
    print(result.to_dict())
```

候选先用launch_candidate.py load_tool，不复制进正式库。可在lock_to_world、gimbal_lock_fix等动画处理后显式export审片，输出files中的MOV可再convert_mp4/convert_gif；不会替调用者保存场景。timeline_marker只影响时间轴注释，不保证出现在viewport影片；组合尚未联合GUI实测。

## 已有证据与限制

普通Python3项检查完整资源/43方法/7函数、参数、负帧hold、源只读、全部衍生冲突/增序/覆盖竞争保护。Maya2025隔离mayapy：实际FFmpeg6.1生成JPEG/音频，MOV→逐帧PNG确认hold首帧重复与尾补齐、MP4/GIF、音频输出、坏JPEG真实非零退出保持原输出、设置I/O及只读dry。高/低export测试使用真实Maya camera/audio/time/selection和真实FFmpeg，但modelPanel/playblast是明确shim；不证明viewport图像、QT格式、声音同步或GUI有效。

真实Maya窗口/viewport/本机QT codec/高分辨率/重名引用相机/音画时序/播放者与生产多相机未验，prepared_unverified。acceptance.md与promotion.json预制；正式布局注册/面板只在临时副本检查，待真人确认后晋级。
