"""Build complete UE Python exporter and Editor C++ menu plugin candidate."""
from pathlib import Path
import shutil
import json
from prepare_external_candidate import ROOT, put, prepare

UNIT = ROOT / 'tools_staging_pool/05_ue_pipeline/ue_bone_exporter'
RC = UNIT / 'release_candidate'
PKG = RC / 'engine_toolkit/tools/ue_bone_exporter'

put(PKG / '__init__.py', '''"""UE mesh bone export. Imports are inert; no Maya dependency or asset mutation."""
from pathlib import Path
import hashlib
import re

TOOL_ID = 'ue_bone_exporter'
parameters_schema = {'type': 'object', 'additionalProperties': False, 'properties': {
    'action': {'type': 'string', 'enum': ['inspect', 'export'], 'default': 'inspect'},
    'output_dir': {'type': 'string', 'description': 'Existing directory; empty uses UE project root'},
    'asset_paths': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 1000,
                    'description': 'UE object paths; omitted uses selected Content Browser assets'}}}


def _unreal():
    import unreal
    return unreal


def validate(**kwargs):
    if set(kwargs) - set(parameters_schema['properties']):
        raise ValueError('Unknown parameters')
    action = kwargs.get('action', 'inspect')
    if action not in ('inspect', 'export'):
        raise ValueError('Invalid action')
    u = _unreal()
    paths = kwargs.get('asset_paths')
    if paths is not None:
        if not isinstance(paths, list) or not 1 <= len(paths) <= 1000 or any(not isinstance(p, str) or not p.startswith('/') for p in paths):
            raise ValueError('asset_paths requires 1..1000 absolute UE object paths')
        assets = [u.load_asset(p) for p in paths]
        if any(a is None for a in assets):
            raise ValueError('An explicit asset path could not be loaded')
    else:
        assets = list(u.EditorUtilityLibrary.get_selected_assets())
    if not assets or len(assets) > 1000:
        raise ValueError('Select 1..1000 assets')
    raw_dir = kwargs.get('output_dir', '')
    if not isinstance(raw_dir, str):
        raise ValueError('output_dir must be a string')
    directory = Path(raw_dir or u.Paths.project_dir()).resolve()
    if not directory.is_dir():
        raise ValueError('Output directory must already exist: ' + str(directory))
    if not hasattr(u, 'SkeletonModifier'):
        raise RuntimeError('Enable UE Skeleton Editing tools: SkeletonModifier unavailable; C++ mesh menu is an independent alternative')
    rows, skipped, seen, targets = [], [], set(), set()
    for asset in assets:
        if not isinstance(asset, u.SkeletalMesh):
            skipped.append(asset.get_path_name())
            continue
        path = asset.get_path_name()
        if path in seen:
            continue
        seen.add(path)
        name = asset.get_name()
        if not re.fullmatch(r'[^<>:"/\\\\|?*\\x00-\\x1f]+', name) or name.endswith(('.', ' ')):
            raise ValueError('Unsafe mesh name: ' + name)
        modifier = u.SkeletonModifier()
        if not modifier.set_skeletal_mesh(asset):
            raise ValueError('Cannot read mesh skeleton: ' + path)
        # Never call commit_skeleton_to_skeletal_mesh or any editing methods.
        bones = [str(n) for n in modifier.get_all_bone_names()]
        if not bones or any(not n or '\\n' in n or '\\r' in n for n in bones):
            raise ValueError('Empty/invalid bone names: ' + path)
        target = directory / (name + '_BoneList.txt')
        key = str(target).casefold()
        if key in targets:
            raise ValueError('Selected meshes produce the same file name: ' + str(target))
        if target.exists():
            raise ValueError('Existing output is protected: ' + str(target))
        targets.add(key)
        rows.append({'asset': path, 'scope': 'mesh', 'bones': bones, 'count': len(bones), 'output': str(target)})
    if not rows:
        raise ValueError('No SkeletalMesh selected')
    return {'action': action, 'rows': rows, 'skipped': skipped, 'asset_mutations': [],
            'file_impact': 'New UTF-8 without BOM txt files; no asset save/commit; files are outside UE Undo'}


def execute(**kwargs):
    plan = validate(**kwargs)
    if plan['action'] == 'inspect':
        return plan
    created = []
    try:
        for row in plan['rows']:
            target = Path(row['output'])
            data = ('\\n'.join(row['bones']) + '\\n').encode('utf-8')
            with target.open('xb') as stream:
                # Register ownership immediately so a partial write can be removed.
                created.append(target)
                stream.write(data)
            row['sha256'] = hashlib.sha256(data).hexdigest()
    except Exception:
        for target in reversed(created):
            target.unlink(missing_ok=True)
        raise
    plan['written'] = [str(p) for p in created]
    return plan


def run(dry_run=True, **kwargs):
    try:
        if not isinstance(dry_run, bool):
            raise ValueError('dry_run must be boolean')
        data = validate(**kwargs) if dry_run else execute(**kwargs)
        return {'success': True, 'tool_id': TOOL_ID, 'dry_run': dry_run, 'data': data, 'errors': []}
    except Exception as error:
        return {'success': False, 'tool_id': TOOL_ID, 'dry_run': dry_run, 'data': {}, 'errors': [str(error)]}


def show_ui():
    # Native plugin supplies actual SaveFileDialog/menu UI. Python preview is inert.
    u = _unreal()
    result = run(action='inspect')
    u.log(str(result))
    return result
''')

PLUGIN = PKG / 'native/BoneListGenerator'
original = UNIT / 'BoneListGenerator_UPlugin'
for src in original.rglob('*'):
    if src.is_file():
        target = PLUGIN / src.relative_to(original)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
cpp = (original / 'Source/BoneListGenerator/Private/BoneListGenerator.cpp').read_text(encoding='utf-8')
cpp = cpp.replace('#include "BoneListGenerator.h"', '#include "BoneListGenerator.h"\n#include "ContentBrowserMenuContexts.h"\n#include "Misc/MessageDialog.h"\n#include "Misc/Paths.h"\n#include "HAL/FileManager.h"')
cpp = cpp.replace('// 获取 SkeletalMesh 资产的右键菜单', 'FToolMenuOwnerScoped OwnerScoped(this);\n\t// 获取 SkeletalMesh 资产的右键菜单')
# Two independent entries preserve old shared-Skeleton behavior and add exact mesh scope.
cpp = cpp.replace('Section.AddMenuEntry(', 'for (bool bSharedSkeleton : {false, true})\n\t\t{\n\t\tSection.AddMenuEntry(')
cpp = cpp.replace('"ExportBoneList",', 'bSharedSkeleton ? "ExportSharedSkeletonBoneList" : "ExportMeshBoneList",', 1)
cpp = cpp.replace('LOCTEXT("ExportBoneList", "生成骨骼表"),', 'bSharedSkeleton ? LOCTEXT("SharedList", "生成关联 Skeleton 骨骼表") : LOCTEXT("MeshList", "生成网格骨骼表"),')
cpp = cpp.replace('CreateLambda([](const FToolMenuContext& Context)', 'CreateLambda([bSharedSkeleton](const FToolMenuContext& Context)')
cpp = cpp.replace('if (!Skeleton)', 'if (bSharedSkeleton && !Skeleton)')
cpp = cpp.replace('Skeleton->GetReferenceSkeleton();', 'bSharedSkeleton ? Skeleton->GetReferenceSkeleton() : SkeletalMesh->GetRefSkeleton();')
cpp = cpp.replace('SkeletalMesh->GetName() + TEXT("_BoneList.txt")', 'SkeletalMesh->GetName() + (bSharedSkeleton ? TEXT("_SkeletonBoneList.txt") : TEXT("_BoneList.txt"))')
cpp = cpp.replace('// 保存文件', '''// Exclusive creation protects existing files, even after the dialog.
                            if (FPaths::GetExtension(OutFiles[0]).ToLower() != TEXT("txt"))
                            {
                                FMessageDialog::Open(EAppMsgType::Ok, LOCTEXT("TxtOnly", "请选择 .txt 输出路径"));
                                continue;
                            }
                            if (IFileManager::Get().FileExists(*OutFiles[0]))
                            {
                                FMessageDialog::Open(EAppMsgType::Ok, LOCTEXT("Protected", "已有文件受保护，请选择新文件名"));
                                continue;
                            }
                            // 保存文件''')
cpp = cpp.replace('FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM)', 'FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), FILEWRITE_NoReplaceExisting)')
cpp = cpp.replace('\t\t);\n\t}', '\t\t);\n\t\t}\n\t}')
cpp = cpp.replace('int32 BoneCount = RefSkeleton.GetNum();', 'int32 BoneCount = RefSkeleton.GetNum();\n                    if (BoneCount == 0) { continue; }')
put(PLUGIN / 'Source/BoneListGenerator/Private/BoneListGenerator.cpp', cpp)
build = (original / 'Source/BoneListGenerator/BoneListGenerator.Build.cs').read_text(encoding='utf-8').replace('"EditorStyle",', '"AssetRegistry",')
put(PLUGIN / 'Source/BoneListGenerator/BoneListGenerator.Build.cs', build)

put(RC / 'tests/test_ue_bone_exporter.py', '''import hashlib
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_toolkit.tools import ue_bone_exporter as tool

class Mesh:
    def __init__(self, name, path=None, bones=None):
        self.name, self.path, self.bones = name, path or '/Game/' + name, bones or ['root', '腕']
    def get_name(self): return self.name
    def get_path_name(self): return self.path

class Modifier:
    def set_skeletal_mesh(self, mesh): self.mesh = mesh; return True
    def get_all_bone_names(self): return self.mesh.bones
    def commit_skeleton_to_skeletal_mesh(self): raise AssertionError('Asset mutation forbidden')

class Tests(unittest.TestCase):
    def fake(self, directory, assets):
        return types.SimpleNamespace(SkeletalMesh=Mesh, SkeletonModifier=Modifier,
            EditorUtilityLibrary=types.SimpleNamespace(get_selected_assets=lambda: assets),
            Paths=types.SimpleNamespace(project_dir=lambda: directory), load_asset=lambda path: None)
    def test_preview_export_and_preexisting_protection(self):
        with tempfile.TemporaryDirectory() as d, patch.object(tool, '_unreal', return_value=self.fake(d, [Mesh('Hero')])):
            result = tool.run(action='export')
            self.assertTrue(result['success']); self.assertEqual(list(Path(d).iterdir()), [])
            result = tool.run(dry_run=False, action='export')
            self.assertTrue(result['success'], result)
            target = Path(d) / 'Hero_BoneList.txt'; data = target.read_bytes()
            self.assertEqual(data, 'root\\n腕\\n'.encode())
            self.assertFalse(tool.run(dry_run=False, action='export')['success'])
            self.assertEqual(target.read_bytes(), data)
    def test_entire_batch_preflight_and_path_collision(self):
        with tempfile.TemporaryDirectory() as d:
            old = Path(d) / 'Bad_BoneList.txt'; old.write_bytes(b'preserve')
            with patch.object(tool, '_unreal', return_value=self.fake(d, [Mesh('Good'), Mesh('Bad')])):
                self.assertFalse(tool.run(dry_run=False, action='export')['success'])
            self.assertEqual([p.name for p in Path(d).iterdir()], ['Bad_BoneList.txt'])
            with patch.object(tool, '_unreal', return_value=self.fake(d, [Mesh('Hero', '/Game/A/Hero'), Mesh('Hero', '/Game/B/Hero')])):
                self.assertFalse(tool.run(dry_run=False, action='export')['success'])
    def test_failure_cleans_owned_file_and_preserves_racing_existing(self):
        with tempfile.TemporaryDirectory() as d, patch.object(tool, '_unreal', return_value=self.fake(d, [Mesh('A'), Mesh('B')])):
            open_original = Path.open
            def raced(path, mode='r', *a, **kw):
                if mode == 'xb' and path.name == 'B_BoneList.txt':
                    with open_original(path, 'wb') as stream: stream.write(b'other writer')
                return open_original(path, mode, *a, **kw)
            with patch.object(Path, 'open', raced):
                self.assertFalse(tool.run(dry_run=False, action='export')['success'])
            self.assertFalse((Path(d) / 'A_BoneList.txt').exists())
            self.assertEqual((Path(d) / 'B_BoneList.txt').read_bytes(), b'other writer')

if __name__ == '__main__': unittest.main()
''')

put(RC / 'docs/tools/ue_bone_exporter.md', '''# UE 骨骼表导出器候选

完整保留 UE Python 选中 SkeletalMesh→逐骨骼 TXT，以及 Editor C++ 右键菜单→原生 SaveFileDialog→成功消息功能。源五文件逐字节 SHA 归档 upstream/catalog.json，原导入自动导出取消。原 Python 为网格骨骼、原 C++ 为共享 Skeleton；现 C++ 有两个明确入口，网格列表默认 _BoneList.txt，共享 Skeleton 列表 _SkeletonBoneList.txt，可能包含本 mesh 没有的骨骼。保留引用骨架顺序，不含 socket，LOD/虚拟骨骼跨版本差异必须实测。

本工具在 Unreal Editor 运行，目标 engine_toolkit/tools/ue_bone_exporter，自包含，未继承 Maya 基类，未修改 Maya 注册表/面板。Python 提供 parameters_schema、validate/execute/run、结构化 success/tool_id/dry_run/data/errors。读选区会加载资产；SkeletonModifier 仅 set/get，不调用骨骼编辑、commit、save；引擎加载与缓存不等于纯内存无变化，但不修改资产内容/场景。API import 不自动运行，dry_run 默认 True，action 默认 inspect。

```python
from engine_toolkit.tools import ue_bone_exporter as t
preview = t.run(action='export', output_dir=r'D:/UE_BoneLists')
result = t.run(dry_run=False, action='export', output_dir=r'D:/UE_BoneLists')
```

output_dir 必须已经存在；空值是 UE 项目根，asset_paths 为可选 UE object path 数组，缺省 Content Browser 选区。混选非 mesh 如原版跳过；坏网格、空骨骼、同名输出、已有目标在整批写入前拒绝。独占 UTF8 无 BOM 换行 TXT；进程内失败清理自己创建的文件，不删除竞争写者的已有文件。进程中断可能留下部分文件。文件不受 UE Undo 撤销，没有覆盖功能。

C++ native/BoneListGenerator 是完整 Editor 源插件，含 uplugin/Build.cs/Public/Private，修复明确 includes、Menu owner 生命周期；保留原保存窗口/日志/消息，新增 FILEWRITE_NoReplaceExisting 和已有文件拒绝，原骨骼表菜单拆为两范围，移除已不使用 EditorStyle 依赖、补 AssetRegistry。C++ 多资产逐项窗口，取消/坏资产跳过、失败可能保留此前文件，不承诺整批事务。无骨骼或无桌面平台时不写。已存在同名插件需先人工审查备份，不能叠装。

Python 需 Python Editor Script Plugin、Editor Scripting Utilities、提供 SkeletonModifier 的 Skeleton Editing Tools（模块/插件和 UE 版本相关）；缺失时报依赖错误，可独立使用 C++。C++ 需目标 UE 的 Editor SDK 与 C++ 工具链，必须本地 UBT 编译，不能把离线文本检查称为编译成功。本机未发现 Program Files/Epic Games，UE 编辑器/UBT/真实资产检查 not_run。

晋级文件清单 promotion.json；plans/staging_run/promote_candidate.py 默认只预览，--apply 需要 passed/tool_id/candidate_sha256/runtime_version/accepted_by/date 人工验收 JSON。将来仅复制 engine_toolkit/docs/tests；UE 插件安装为单独显式动作：把 native/BoneListGenerator 复制到临时 UE 项目 Plugins/BoneListGenerator，生成项目文件/编译 Editor 后启用。包内所有路径自包含；不自动改 .uproject 或用户启动脚本。人工验收前包保留待整理池。

可组合：从 Maya FBX 导出→UE 导入 SkeletalMesh→读取 mesh bones 校对；TXT 是名称序列，不验证蒙皮/父子关系或绑定姿态，不作为自动删除/重命名依据。共享 Skeleton 名称不能冒充该 mesh 实际骨骼。

API 依据：[SkeletonModifier](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SkeletonModifier)、[USkeletalMesh GetRefSkeleton](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/USkeletalMesh/GetRefSkeleton)、[菜单 Context](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Editor/ContentBrowser/UContentBrowserAssetContextMenuC-)、[FToolMenuOwnerScoped](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Developer/ToolMenus/FToolMenuOwnerScoped)、[SaveStringToFile](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Core/FFileHelper/SaveStringToFile)。仅依据文档补适配，目标 UE 编译/运行仍待验。
''')
put(RC / 'acceptance.md', '''# UE 人工验收（not_run）

1. 使用备份 UE 项目和空临时输出目录。启用 Python Editor Script/Editor Scripting Utilities/Skeleton Editing Tools；把候选根加入 sys.path，import engine_toolkit.tools.ue_bone_exporter，确认没有写文件或骨骼提交。
2. 两个实际 SkeletalMesh 共用 Skeleton 且 mesh 骨骼不同，含中文骨名/不同文件夹同名 mesh。run(action='export') 确认全表可读、没有文件/资产 dirty；执行 dry_run=False 核对 UTF8、网格骨名/顺序、非网格跳过；同名、已有文件、空选区、禁用依赖全表拒绝；资产和磁盘 uasset 哈希不变。
3. 将候选 native/BoneListGenerator 安装到备份 C++ UE 项目 Plugins（原插件若存在先备份审查，不覆盖），生成项目文件，通过目标引擎 UBT 编译。启用插件，SkeletalMesh 右键出现网格/共享 Skeleton 两个入口，逐项保存对话框、取消、成功消息与失败日志正常。对比共享 Skeleton 额外骨骼差异；已有目标即使对话框确认也不覆盖。
4. 卸载/重启/热重载检查菜单不重复且注销完整。Windows保存路径/中文/扩展名/无骨骼/只读目录/多资产 partial outputs检查。Python/C++ 实测均通过后记录版本、工具 ID、promotion 预览 SHA、操作者/日期，不用离线 mock 或静态 C++ 代替 UE 验收。
5. 用户验收 JSON 必含 passed=true/tool_id=ue_bone_exporter/candidate_sha256/runtime_version/accepted_by/date；晋级脚本只布置项目内最终路径，插件安装仍是 UE 原生操作。Maya验收对此纯UE工具不适用（不声称通过）。
''')
prepare('05_ue_pipeline/ue_bone_exporter', 'Complete UE Python mesh TXT export and C++ mesh/shared Skeleton menus; native runtime schema/dry-run/exclusive output; no Maya registry adapter', ['UE Editor PythonScriptPlugin/EditorScriptingUtilities/Skeleton Editing Tools', 'Editor UBT + C++ toolchain for native plugin'], ['Unreal Editor runtime and UBT compilation not_run', 'Target UE Python/C++ version and real skeletal assets unverified'], 'UE SkeletalMesh right-click two scope entries; native SaveFileDialog, Python inspection/log')
