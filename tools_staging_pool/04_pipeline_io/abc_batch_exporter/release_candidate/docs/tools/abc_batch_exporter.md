# ABC 模型列表与选择集批量导出候选

`abc_batch_exporter`，`pipeline_io`，对应用户两份完整Python2原稿。保留模型列表版全部布局（模型载入/清空、时间/步长、六导出开关、文件浏览、输出、新建随机Lambert）与文件夹选择集批量版全部布局（文件夹输入/浏览/执行）；字符串回调和动态exec改为Python3函数回调。原两文件逐字节归档、catalog SHA，不推断未提供的授权许可。模块导入不开窗。

## 操作与输入

- `action=inspect` 默认只读解析当前选择或指定 scope；`objects` 指定整体mesh/transform/joint层级（有mesh）；或 `set_name` 指定精确 objectSet，两者互斥。缺集/空集/组件/嵌套选择集/歧义等拒绝，无缺集旧选择fallback。解析可见非intermediate mesh的直接父transform，按首次出现去重，拒绝含child transform的mesh owner以防扩入rig/相机子树。读取引用模型可以；实例路径歧义拒绝，明确单路径只读导出按原生处理。
- `action=export` 必须给绝对、未存在 `.abc` 的 `output`。不改scene selection。`start/end` 包含端点，未给读取播放范围；可小数；`step=1` 正有限，最多100000采样。用 native AbcExport，execute才加载AbcExport，dry不加载plug-in。
- options 布尔键 `uv_write/world_space/write_uv_sets/write_face_sets/write_visibility` 默认True，`strip_namespaces/write_color_sets` 默认False；batch的color默认True对应原稿。均构造成有或无flag，不把True/False文本塞入job；原无效detail转真实verbose=True。根与文件名双引号并规范路径，拒绝引号/换行token；支持空格路径。去namespace先检查导出DAG名冲突。
- `action=materials` 给指定/current models分别创建随机RGB Lambert与独立SG，整模型 forceElement 赋材质，保留原功能。整模型替换可能覆盖原per-face材质；不改变原材质节点，不保存scene。全部目标/shape引用、锁、真实实例预检，selection恢复，创建与assignment一次Undo。
- `action=batch` 必须给绝对存在的 `folder/output_dir`，不递归读其中最多1000个 .ma/.mb；默认每个scene精确 `abc_export` 集，输出 `<stem>.abc`。同stem/大小写输出冲突、任何已存在目标、目录缺失先整批拒绝。UI保持原同输入文件夹输出语义；API允许独立输出目录。`timeout=180` 秒/scene（10..3600）。起止未给时各scene按自己播放范围；其它export options同API。

## 预检、输出、影响与失败

scene dry 返回 roots/start/end/step/options/output；batch dry 返回 scenes/outputs/mayapy/set_name、`scene_contents_checked=False`。batch dry 不打开或扫描scene内部选择集，因此并非所有scene内容已验过。正式执行每个scene启动新的当前Maya版本mayapy，关闭窗口的进程方式，禁用Maya script nodes并加载references；仅在隔离子进程开文件，当前dirty/untitled场景、选择、时间、modified状态保持。每scene结果有success/message/data/returncode，坏文件/缺集/导出错误保留失败证据后继续；有任一失败总ToolResult.fail，成功外部文件保留。无用户scene force-open/new/save动作，无偏好写入。

native export先写输出目录中独有temp文件夹，验证存在且非空，再以 `xb` 独占创建最终文件；提交竞争绝不覆盖已有缓存。正常失败清理本次新建不完整文件和临时目录；进程被kill/机器掉电可能留 mtb_abc_ 临时目录或不完整最终文件，需人工核对后再重试，candidate不泛删用户目录。执行可能加载native exporter，加载状态不由scene Undo撤销。文件导出不可由Maya Undo撤回。当前时间/selection/AutoKey finally恢复，已有曲线和geometry不改。导出数据受Maya实际插件/资产支持约束，原生export异常可能部分输出，不能用Undo假称文件回滚。

materials返回 `data.materials:[node,shader,shading_group,color]`；export返回output/bytes/roots/start/end/step。异常ToolResult记录traceback；batch返回所有scene结果、成功outputs、current_scene_preserved=True。不能将prepared_unverified当作UI/生产导出验收通过。

```python
from maya_toolkit.tools.abc_batch_exporter import ABCBatchExporterTool
t=ABCBatchExporterTool()
args=dict(action='export',set_name='abc_export',output=r'E:\\temp\\shot01.abc',start=1,end=24,options={'strip_namespaces':False})
preview=t.run(dry_run=True,**args)
if preview.success:
    print(t.run(**args).to_dict())
```

关联：`export_sets_to_fbx`共享选择集资产范围概念，但FBX含骨架/动画与ABC几何缓存不同；`gpu_cache_to_mesh`可用于已有GPU缓存转换后供本工具导出mesh；`uv_set_renamer`可先整理UV名称再设置write_uv_sets。传递roots/精确set_name/output，组合生产GUI尚未验证。复用现有Base/ToolResult/Undo框架；不改正式FBX工具及core。

## 验证与晋级

两原稿完整资源归档、Python3候选/API/Schema/UI/worker/知识/测试/acceptance/promotion齐备；临时未来布局验证实际注册/panel，正式库不动。真实interactive两窗/材质按钮/颜色面集/生产参考场景/插件跨版本接受程度仍not_run。Maya2025隔离回读及真实childworker结果见manifest。修正原强制丢弃当前scene、缺set导出旧selection、未引用quotedpath/flag含bool、多输出覆盖等行为，应集中Maya验收满意后晋级。
