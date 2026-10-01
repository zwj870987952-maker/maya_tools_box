"""Write candidate knowledge/acceptance including original incomplete menu and legacy boundaries."""
import json
from prepare_retime_tools import RC, PKG

DOC = '''# eblabs Retime Tools 动画重定时候选

用途：用控制器 `timeWarp` 动画驱动目标 animCurve 的 `input`，支持启用、禁用、重置、反向、连接、断开、烘焙、洗牌和子帧清理。完整原 Qt 界面和 38 个旧 MEL 过程均保留，原始 28 文件包括压缩包、图片、空 Plugin.py、Qt 辅助库与安装脚本按字节归档。原始源码未执行安装；晋级包不依赖待整理池外部路径。

作者：Python/套件 eblabs，原界面标注“帝都儿汉化”；历史 MEL 注明 Eric Bates 2011，版本 2018-05-28。原官网指向 https://eblabs.com/shop/retime-tools/。没有随包独立再分发许可；个人本地整理不代表获得再分发许可。QTS 与顶层 LicenseManager 的版本模块/UXFramework 不全，原试用参数、许可代码不改不模拟；主 RetimeTools.py 未导入这些模块，实际主界面只使用 Qt。空 Plugin.py 不视为提供了一个 Maya 插件。

## API 与输入输出

`maya_toolkit.execute_tool('retime_tools', arguments, dry_run=True)` 调用标准 BaseMayaTool 协议。候选使用 launch_candidate.py 的 load_tool()，晋级后注册 RetimeToolsTool 并由现有面板发现。`validate`/dry_run 只读；不创建 Qt widget，不加载 MEL，不安装 Shelf，不写文件。所有 API 场景写入一个 UndoChunk，失败允许 Undo，不自动回滚；time/selection/namespace/autokey 用 finally 恢复。选中操作在界面由用户主动触发。剪贴板 copyKey/cutKey/pasteKey 与原算法一样会改变 Maya key clipboard，场景 Undo 不等于恢复剪贴板。

| action | 必要参数/行为 | 输出/影响 |
| --- | --- | --- |
| inspect | 无参数 | 只读控制器列表 |
| create | name 可选 | 原完整多形状控制器、timeWarp/offline/store/state 与动画范围线性关键帧 |
| connect | controller，nodes 或 curves；省略时当前选择 | 原列表深度 2 的关联 animCurveT，替换普通 time.outTime，拒绝其他 warp/驱动 |
| disconnect | controller，可给已连接 curves 子集 | 断开 warp 并显式恢复唯一 time.outTime，避免曲线冻结 |
| state | controller，state 为 Enable/Disable/Reset/Invert/Disconnect/Delete | 原启停离线槽、反向采样、删除逻辑；删除先恢复时间输入，拒绝外部 DAG 子项/消费者 |
| bake | controller | 原 bakeResults，sampleBy=1/simulation=True；原 preserveOutsideKeys=False，范围外关键帧可能丢失 |
| shuffle | controller，clean 可选 | 完整原复制/粘贴/切线/替换/Infinity 算法，用修正的逆查找移动关键帧；断开 warp，可同时清理子帧 |
| clean_subframes | controller 或 nodes/curves 或当前选择 | 保留完整原先插入整数帧再剪切子帧算法；负帧 round 以 floor(t+0.5) 修正 |
| rename | controller，name | 重命名所选控制器 |
| update_legacy | 明确旧 controller | 完整原添加 state/移除 shuffleData，不自动升级整个场景 |
| import_curve | file，name 可选 | 原一列值/两列帧值或 JSON frame:value 语义，完整控制器创建后应用关键帧并记录路径元数据 |
| export_curve | controller，file，overwrite 默认 False | .json 或 .txt/.ascii，写现有目录；临时文件+无覆盖硬链接或明确覆盖原子替换；不可 Maya Undo |
| open_ui/close_ui | 交互 Maya | 完整原 Qt 界面，私有 objectName；写回调转统一 API |
| open_legacy_ui | 交互 Maya、备份场景 | 完整历史 MEL UI，过程/UI/全局变量私有化；独立人工验收 |

返回 ToolResult.data 含 controller、curves、file、warnings；数据只描述实际 API 作用范围。curves 子集仅用于 connect/disconnect/clean_subframes，烘焙/洗牌/状态按整个控制器处理。所有 API 拒绝引用/锁定节点、其他时间驱动、共享到其他目标的 warp 动画曲线，以及不可编辑的目标输出；不支持动画层/约束输出重连。shuffle/Invert 要求有界且采样严格单调，平坦或非单调 warp 无唯一逆，使用 bake 后验收；这明确收窄了原代码容易零除/多解覆盖的输入范围。

## 算法演进与原始边界

完整原 32 类 211 方法保存在 native.py；五个业务类全体方法另提取 engine.py，不是演示替代。原 UI 的导入/导出菜单本来是禁用打印占位，仍保留这个事实，实际文件功能由明确 API 提供。原 Utilities 全部方法保留可追溯，但不走其缺失 ebLabs_createTimeWarpController MEL 全局依赖/忽略传入参数/取消文件对话框报错路径。

RetimeLookup 原源码两个 lerp 时间端点都写 min_index，邻接方向也不稳定。候选 API 在完整原分段/采样数据上逐相邻样本求逆、去重，得到 time=0/负帧及正确局部 warp 斜率；原全部辅助方法仍保留。ShuffleKeys 的原 `if not rt` 改为 `is None`，paste 使用 merge 避免插入时移动已粘贴时间，Infinity 直接读写原 curve 属性（源 query 会返回 None），临时曲线异常 finally 清理，替换失败不会被打印后当成功。原 Invert 包含末帧。原 bake 输出查询错误地每轮查询整个曲线列表，改为每条 output，仍保留完整原烘焙算法。

历史 MEL 套件保留完整旧算法，包括 calculator、velocityTimeWarp、迭代连接、字符集处理、旧 shuffle/bake、子帧清理与进度 UI。私有化并修复缺失 animscratch Python 连接桥，除此保留其原场景行为。**历史 MEL 回调不是 Python 安全 API：其旧的 force 连接、场景遍历、关键帧/播放设置及 Undo 行为须分别在备份场景验收，不作为无人值守场景写入入口。** 静态定义编译通过只能证明能加载，不证明每个按钮正常。

## 可组合与验证

输入是已有时间输入 animCurve 的 Maya 场景；输出是重定时连接、重排或烘焙的动画。可在动画清理/降帧工具之前先烘焙并检查断开连接；这只是潜在流程，不代表与正式工具联测通过。沿用框架 BaseMayaTool/Undo/ToolResult，不修改 core；原专有控制器形状和查找算法不适合未经多工具验收下沉。

离线 Python 测试核对全套 SHA256/211 方法/Schema/严格输入/ASCII/JSON/零负帧查找；隔离 Maya2025 五组检查覆盖完整控制器、连接、启停与 Undo、洗牌与临时清理、删除恢复时间、目标锁与外部子项拒绝、文件 IO、烘焙、Qt 类导入（不创建 QWidget）、38 MEL 定义编译。真实 GUI、生产 rig、引用/动画层、加权切线、非线性曲线、反向速度、跨 Maya 版本尚未验收。隔离通过不等于真人 Maya 验收。
'''

ACCEPT = '''# Retime Tools 真人 Maya 验收（not_run）

所有结果待用户填写；仅在备份动画场景与临时目录进行，候选不转正。

```python
import runpy
tool = runpy.run_path(r"E:/GitHub/maya_tools_box/tools_staging_pool/01_animation/retime_tools/release_candidate/launch_candidate.py")['load_tool']()
tool.show_ui()
```

1. 原中文 Qt 窗口正常打开；控制器列表、连接树、重命名、颜色、确认按钮、折叠/编辑标签和关闭/重新打开逐项响应；Script Editor 不应出现致命错误。
2. 用两个不同命名空间的有动画控制器 Create/Add/Remove；确认只连接目标 animCurve，另一个 warp/约束/引用/锁定输出拒绝写入；移除后恢复 time 输入、动画没有冻结。
3. 修改 timeWarp 后 Enable/Disable/Reset；offline 槽保留动画，各操作一次 Undo/Redo，选择/time/autokey/namespace 恢复；保存 .ma 重开后行为一致。
4. 正负关键帧、零帧、线性/非线性/加权切线测 Shuffle；匹配原期望姿态与时间。单调反向另验切线、Infinity，非单调/hold 要拒绝逆操作并改用 Bake。逐帧检查 Bake，重点检查范围外关键帧影响。
5. Clean subframes 先复制曲线：核对负帧取整、整数帧保留及视觉变化。不得把数学取整变化当原界面已验收。
6. Invert 的末帧、短范围及状态列表响应；Delete 保留动画对象并恢复 time，控制器外部子节点存在时应拒绝删除；一次 Undo 应恢复控制器与原连接。
7. 用 API 将原两列 ASCII/一列值和 JSON 导入，再导出到临时目录；取消/坏文件/重复帧/NaN/已有文件/overwrite/读写权限失败逐项测试。导出的外部文件不可 Undo。
8. 复制历史 MEL 控制器，明确 update_legacy，验证 state 与旧 offline 状态，Undo 后可回到旧结构。
9. `tool.run(action='open_legacy_ui')` 在另一份备份场景验历史 MEL calculator、velocityTimeWarp、全部连接/筛选、shuffle/bake、子帧和进度 UI。其回调保留旧行为，与受预检保护的 Python API 分别记录；失败先修候选，不晋级。
10. 根据 docs/tools/retime_tools.md 末尾全体 211 方法/38 过程目录记录套件测试覆盖；Maya2025 以外版本、生产 rig、材质/动画层等不能由离线检查代替。

验收通过后生成带 tool_id、candidate_sha256、passed、maya_version、accepted_by、date 的验收文件，先运行 plans/staging_run/promote_candidate.py --candidate 本目录 查看晋级清单，再按已记录真人验收执行晋级。注册和面板变更由该脚本预制；本轮不 apply。
'''


def main():
    cat=json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
    index='\n## 完整原方法与 MEL 过程目录\n\n'
    for k,v in cat['classes'].items():
        index += '* `'+k+'`: '+', '.join('`'+x+'`' for x in v)+'\n'
    index+='\n历史 MEL：'+', '.join('`'+x+'`' for x in cat['mel_procedures'])+'\n'
    (RC/'docs/tools/retime_tools.md').write_text(DOC+index,encoding='utf-8')
    (RC/'acceptance.md').write_text(ACCEPT,encoding='utf-8')
    print('Wrote full suite knowledge and acceptance')


if __name__=='__main__':
    main()
