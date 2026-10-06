"""Build the Animo staging catalog without importing or running vendor scripts."""
import argparse
import ast
import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIT = ROOT / 'tools_staging_pool/07_subsystems_suites/animo'
ORIGINAL = UNIT / 'upstream/Animo_v10.6.0'
CANDIDATE = UNIT / 'release_candidate'
PACKAGE = CANDIDATE / 'maya_toolkit/tools/animo'
DOCS = ROOT / 'docs/tools/animo'

GROUPS = {
    'Recommended': ('推荐工具', '按动画制作常见操作组合显示；重复项只保留一个执行 ID。', '视口或选择状态'),
    'Viewport Display': ('视口显示', '切换视口中的对象类型、辅助显示、灯光和遮罩。', '视口显示状态'),
    'Selection': ('选择管理', '改变对象或曲线选择，供后续动画编辑使用。', '当前选择'),
    'Manipulator': ('操纵器', '调整 Move/Rotate/Scale 工具的坐标系或轴向行为。', 'Maya 工具设置'),
    'Keys': ('关键帧操作', '对当前对象、通道或所选关键帧进行增删、复制和编辑。', '关键帧或选择'),
    'Nudge Keys': ('关键帧微移', '按入口预设偏移关键帧时间。', '关键帧时间'),
    'Locator': ('定位器与父级', '创建定位器或在保留动画的流程中改变父级关系。', 'DAG 节点、父级、约束或关键帧'),
    'Color Keys': ('关键帧颜色', '调整关键帧的显示标记。', '关键帧显示属性'),
    'Offset Keys': ('关键帧偏移', '按固定步长或交互选项偏移关键帧。', '关键帧时间或数值'),
    'Fast Bake': ('快速烘焙', '按入口标注的帧间隔烘焙动画；输入帧区间由原工具读取。', '生成/替换关键帧'),
    'Tracify (Track Arcs)': ('运动弧线', '跟踪世界或摄像机空间运动轨迹，调整缓存和显示。', '插件节点、轨迹缓存和视口'),
    'Spacify': ('临时空间切换', '建立世界、相对、摄像机、Aim、临时 IK/FK 等辅助系统，并烘焙清理。', 'DAG、约束、集合和关键帧'),
    'Xform World': ('世界变换', '复制/粘贴世界空间变换、烘焙区间或锁定脚部。', '变换、关键帧或缓存文件'),
    'Align': ('对齐', '根据选择顺序将前面的对象对齐到目标对象，可针对时间范围。', '变换或关键帧'),
    'Mirror': ('姿态与动画镜像', '建立默认姿势/镜像设置，按当前姿势或关键帧区间镜像。', '变换、关键帧和镜像配置文件'),
    'Reset Pose': ('姿态复位', '恢复原工具记录的默认属性，支持位移、旋转、缩放或全部。', '属性或关键帧'),
    'Graph Editor': ('曲线编辑器', '打开或改变编辑器布局，过滤、循环、反转、平滑或裁剪曲线。', '编辑器 UI、曲线或切线'),
    'Channel Box': ('通道面板', '改变通道面板的显示或编辑方式。', 'Maya UI'),
    'Global Offset': ('全局偏移', '在动画上叠加整体偏移，支持范围和动画层相关操作。', '变换、曲线、辅助控制器'),
    'Twosify': ('风格化动画', '通过动画层、步进或间隔处理制作有限帧数风格动画。', '动画层和关键帧'),
    'Xform Relationships': ('相对变换关系', '记录并应用对象之间的变换关系，可烘焙区间。', '变换、关键帧或缓存文件'),
    'Pickify (Selection Sets)': ('选择集', '建立、编辑并使用角色选择集。', '选择、集合和偏好文件'),
    'Temp Pivot': ('临时轴心', '建立或重置临时轴心控制器。', '辅助节点、变换或关键帧'),
    'Rotate Order': ('旋转顺序', '为整段旋转动画转换至入口指定的 Euler 顺序。', 'rotateOrder 和旋转关键帧'),
    'Keys Time': ('关键帧时间传递', '复制/粘贴通道或姿势间的关键帧时间，清理时间分布。', '关键帧时间及本机缓存'),
    'Animation Layers': ('动画层', '创建、选择、管理或合并动画层；合并可能改变原层结构。', '动画层、成员与关键帧'),
    'Copy Animation': ('跨场景动画传递', '保存 JSON 动画数据并插入或替换；分层对象可能要求先合并。', '曲线及动画 JSON 文件'),
    'Copy Pose': ('姿态传递', '保存、读取姿态 JSON，按对象或命名空间应用。', '属性及姿态 JSON 文件'),
    'Constraints': ('约束', '为选定对象创建 Point/Orient/Scale 或组合约束。', '约束节点与连接'),
    'Physics': ('物理辅助', '调用原工具的物理运动辅助入口。', '辅助节点或关键帧，具体输出待实测'),
    'Tangents': ('切线', '按当前帧或全部范围设置 Auto、Linear、Stepped 等切线。', '关键帧切线'),
    'Tweenify (Sliders Quick Pop Up)': ('滑块弹出面板', '打开包含滑块的轻量交互界面。', 'UI 及使用滑块时的曲线'),
}
SLIDERS = {
    'Tween': ('补间', '按左右边界值调整所选关键帧；不是按关键帧时间比例插值。'),
    'Blend to Default': ('混合至默认值', '将动画数值混合至默认属性。'),
    'Blend to Neighbors': ('混合至邻帧', '将所选数值向相邻关键帧混合。'),
    'Blend to World': ('混合至世界空间', '调整世界空间相关动画值。'),
    'Blend to Mirror': ('混合至镜像', '按镜像配对结果混合姿态或动画。'),
    'Blend to Infinity': ('混合至 Infinity', '按曲线 Infinity 行为混合动画。'),
    'Blend to Ease': ('混合至缓动', '向缓动曲线形态混合动画。'),
    'Ease': ('缓入缓出', '改变关键帧数值分布的缓动形态。'),
    'Push and Pull': ('推拉幅度', '增强或收缩动画相对差值。'),
    'Scale Average': ('围绕均值缩放', '围绕均值调整动画幅度。'),
    'Scale Left': ('围绕左侧缩放', '围绕左侧参考值调整动画幅度。'),
    'Scale Right': ('围绕右侧缩放', '围绕右侧参考值调整动画幅度。'),
    'Scale from Average': ('从均值缩放', '按原入口的均值参考缩放动画幅度。'),
    'Scale from Default': ('从默认值缩放', '按默认属性参考缩放动画幅度。'),
    'Scale from Left': ('从左侧缩放', '按左侧参考缩放动画幅度。'),
    'Scale from Right': ('从右侧缩放', '按右侧参考缩放动画幅度。'),
    'Time Offset': ('时间偏移', '移动动画时间，固定入口的数值由脚本预设。'),
    'Time Offset Stagger': ('错开时间', '按对象顺序错开动画时间。'),
    'Wave and Noise': ('波形与噪声', '按预设强度向动画加入波形或噪声变化。'),
    'Connect To Neighbor': ('衔接邻帧', '按邻帧边界调整动画衔接。'),
    'Simplify - Bake': ('简化与烘焙', '减少关键帧或补充采样关键帧。'),
    'Smooth - Harsh': ('平滑与强化', '平滑或强化动画数值变化。'),
}
for key, (name, description) in SLIDERS.items():
    GROUPS[key] = (name, description, '关键帧数值、时间或切线')

EXTRA = {
    'toolbar': ('主工具栏', 'Animo_Launcher/Animo_Launcher.py', '完整原生工具栏，含停靠、滑块和工具设置。'),
    'tools_editor': ('工具编辑器', 'Animo_Launcher/tools_editor_launcher.py', '搜索工具、配置快捷键与 Shelf。'),
    'vectorify': ('路径重定向', 'Animo_Launcher/vectorify_launcher.py', '用临时控制器将动画重新沿路径行进，并可吸附地面。'),
    'multi_camera_playblast': ('多摄像机预览', 'Animo_Launcher/fast_multi_view_playblaster_launcher.py', '从多个摄像机输出 Playblast，写入外部媒体文件。'),
    'quick_export_import': ('快速对象导入导出', 'Animo_Launcher/quick_exporer_launcher.py', '保存和读取对象资产文件，可能覆盖磁盘文件。'),
    'pickify': ('选择集面板', 'Animo_Launcher/pickify_launcher.py', '创建和管理竖排/横排选择集。'),
    'spacify': ('空间工具面板', 'Animo_Launcher/spacify_launcher.py', '打开完整临时空间工具面板。'),
    'transify': ('动画传递面板', 'Animo_Launcher/transify_launcher.py', '复制、插入、替换动画和姿态，处理命名空间。'),
    'tracify_settings': ('运动弧线设置', 'Animo_Launcher/tracify_launcher.py', '管理轨迹颜色、帧范围和摄像机空间。'),
    'tweenify': ('滑块面板', 'Animo_Launcher/tweenify_launcher.py', '弹出 19 个滑块的交互界面。'),
    'twosify': ('风格化动画面板', 'Animo_Launcher/twosify_launcher.py', '动画层与步进风格配置。'),
    'temp_pivot': ('临时轴心面板', 'Animo_Launcher/temp_pivot_launcher.py', '创建并配置临时轴心。'),
    'reference_dropper': ('参考媒体拖放插件', 'Animo_Reference_Dropper/load_anim_ref_dropper.py', '加载拖放插件；后续媒体导入可能运行 FFmpeg 并生成图片序列。'),
}


def digest(path):
    with path.open('rb') as stream:
        h = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def slug(value):
    value = value.replace('-', ' minus ').replace('+', ' plus ').replace('%', ' percent ')
    return re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def resolved_entry(library_file, source_data):
    """Resolve wrapper filenames using the literal fallback path, never execute them."""
    tree = ast.parse(library_file.read_text(encoding='utf-8-sig'))
    filename = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_TOOL_FILENAME' for t in node.targets):
            filename = ast.literal_eval(node.value)
    if not filename:
        return library_file
    candidates = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'join':
            values = [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            if 'Animo_Data' in values:
                suffix = values[values.index('Animo_Data') + 1:]
                candidate = source_data.joinpath(*suffix, filename)
                if candidate.is_file():
                    candidates.add(candidate)
    if not candidates:
        # Some wrappers assemble the path in variables or nested joins. Only use
        # a unique exact filename; never choose the first fuzzy match.
        matches = list(source_data.rglob(filename))
        if len(matches) == 1:
            candidates.add(matches[0])
    if len(candidates) != 1:
        raise ValueError('Cannot uniquely resolve {}: {}'.format(library_file, sorted(map(str, candidates))))
    return candidates.pop()


def source_details(path):
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    functions = []
    calls = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
            functions.append({'name': node.name, 'line': node.lineno, 'arguments': [a.arg for a in node.args.args]})
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            try:
                values = [ast.literal_eval(a) for a in call.args]
            except (ValueError, TypeError):
                continue
            calls.append({'call': ast.unparse(call.func), 'literal_arguments': values, 'line': node.lineno})
    return {'public_functions': functions, 'top_level_calls': calls}


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    if not (ORIGINAL / 'Animo_Data').is_dir():
        raise SystemExit('请先把官方原包解压到 ' + str(ORIGINAL))
    archive = UNIT / 'archives/Animo_v10.6.0.zip'
    expected_zip = '0a99ff64227047a6423f6c6e2a2ac081acbdfb58dd53e5fad6de9879b987c502'
    if not archive.is_file() or digest(archive) != expected_zip:
        raise SystemExit('原包缺失或指纹不匹配；拒绝从不同版本构建。')
    data = ORIGINAL / 'Animo_Data'
    editor = data / 'Animo_Tools_Editor'
    settings = json.loads((editor / 'animo_tools.json').read_text(encoding='utf-8-sig'))
    aliases = {}
    display_count = 0
    for category in settings['custom_categories']:
        for row in category.get('tools_data', []):
            display_count += 1
            aliases.setdefault(row['file_path'].replace('\\', '/'), []).append(category['name'])
    operations = []
    source_hashes = {}
    for path in sorted((editor / 'tools_library').rglob('*.py')):
        category = path.parent.name
        zh, desc, effects = GROUPS[category]
        rel_library = path.relative_to(editor / 'tools_library').as_posix()
        target = resolved_entry(path, data)
        suffix = hashlib.sha1(rel_library.encode()).hexdigest()[:8]
        op_id = slug(category) + '.' + slug(path.stem) + '_' + suffix
        operations.append({
            'id': op_id, 'name': path.stem, 'category': category, 'category_zh': zh,
            'description': '{}：{}。{}'.format(zh, path.stem, desc),
            'description_evidence': 'category_review_and_source_static_analysis',
            'display_categories': aliases.get(rel_library, [category]),
            'original_library': 'Animo_Data/Animo_Tools_Editor/tools_library/' + rel_library,
            'entrypoint': target.relative_to(ORIGINAL).as_posix(),
            'input': {'selection': '当前对象、通道/Graph Editor 关键帧选择；具体入口条件由原脚本检查', 'parameters': '原入口固定预设；本适配器不接受任意函数参数或代码'},
            'output': '返回分派状态和操作后选择；原算法没有统一业务结果，需人工观察',
            'effects': effects, 'undo': '场景由框架 Undo Chunk 分组；原生 Undo 行为待检验，UI、文件、插件和偏好不由 Maya Undo 撤回',
            'maya_verified': False, **source_details(target),
        })
    for key, (name, relative, desc) in EXTRA.items():
        target = data / relative
        if not target.is_file():
            raise ValueError('Supplemental entry missing: ' + str(target))
        operations.append({'id': 'suite.' + key, 'name': name, 'category': 'Suite UI', 'category_zh': '完整套件入口',
                           'description': desc, 'description_evidence': 'reviewed_launcher_source',
                           'entrypoint': 'Animo_Data/' + relative, 'original_library': None,
                           'display_categories': ['Suite UI'],
                           'input': {'selection': '原生 UI/入口读取当前 Maya 上下文', 'parameters': '原生面板中设置'},
                           'output': '入口已分派；UI 由原生 Qt timer 延迟创建，需人工检查',
                           'effects': 'UI、偏好、插件；实际操作还可能写场景或文件',
                           'undo': 'UI、偏好和外部文件不由 Maya Undo 撤回', 'maya_verified': False,
                           **source_details(target)})
    if len({row['id'] for row in operations}) != len(operations):
        raise ValueError('Duplicate operation IDs')
    # Preserve source+resources byte for byte, except two explicitly scoped lifecycle patches.
    native = PACKAGE / 'native'
    patches = []
    for original in sorted(data.rglob('*')):
        if not original.is_file() or '__pycache__' in original.parts or original.suffix == '.pyc':
            continue
        relative = original.relative_to(ORIGINAL).as_posix()
        destination = native / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative == 'Animo_Data/Animo_Launcher/Animo_Launcher.py':
            code = original.read_text(encoding='utf-8-sig')
            for call in ('enable_usersetup_security()', '_check_first_run_startup()'):
                token = '\n' + call + '\n'
                if code.count(token) != 1:
                    raise ValueError('Lifecycle patch no longer matches ' + call)
                code = code.replace(token, '\n# Staging: automatic startup/configuration disabled: ' + call + '\n')
            content = code.encode('utf-8')
            patches.append({'path': relative, 'change': '移除导入时启用启动脚本及首次运行写 userSetup 的两个顶层调用；保留显式 UI 配置函数。'})
        elif relative == 'Animo_Data/Animo_Launcher/toggle.py':
            code = original.read_text(encoding='utf-8-sig')
            token = 'if name.endswith("UIWindow"):'
            if code.count(token) != 1:
                raise ValueError('Window patch no longer matches')
            content = code.replace(token, 'if name.startswith("Animo") and name.endswith("UIWindow"):').encode('utf-8')
            patches.append({'path': relative, 'change': '窗口清理只匹配 Animo 前缀，避免误关其他 UI。'})
        else:
            content = None
        desired_hash = hashlib.sha256(content).hexdigest() if content is not None else digest(original)
        if destination.exists() and digest(destination) != desired_hash:
            raise ValueError('候选文件已有本机改动，拒绝覆盖：' + str(destination))
        if not destination.exists():
            if content is None:
                shutil.copy2(original, destination)
            else:
                destination.write_bytes(content)
        source_hashes[relative] = desired_hash
    write_json(PACKAGE / 'operations.json', {'source_version': '10.6.0', 'status': 'prepared_unverified', 'operations': operations})
    write_json(PACKAGE / 'runtime_files.json', source_hashes)
    write_json(CANDIDATE / 'patches.json', patches)
    write_json(CANDIDATE / 'manifest.json', {'tool_id': 'animo', 'status': 'prepared_unverified', 'official_registration': False,
        'maya_acceptance': {'status': 'pending_user', 'verified_versions': []},
        'license': 'author_permission_user_confirmed',
        'publication_authority': '../AUTHOR_PERMISSION.md',
        'zip_sha256': expected_zip, 'library_entries': len(operations) - len(EXTRA), 'display_records': display_count,
        'supplemental_entries': len(EXTRA), 'operation_count': len(operations), 'native_files': len(source_hashes),
        'source_data': 'maya_toolkit/tools/animo/native/Animo_Data', 'patch_log': 'patches.json',
        'registration_after_acceptance': {'module': 'animo', 'class_name': 'AnimoTool'},
        'promotion': '人工检验通过后另行处理；本构建脚本不会复制正式工具、修改 ALL_TOOL_CLASSES 或注册到面板。'})
    DOCS.mkdir(parents=True, exist_ok=True)
    category_dir = DOCS / 'categories'
    category_dir.mkdir(exist_ok=True)
    categories = Counter(row['category'] for row in operations)
    index = ['# Animo 功能与代码目录', '', '> 待整理候选，所有入口均未通过 Maya 人工检验。用户确认已获原作者授权，源码与资源随仓库同步。', '',
             '540 个库入口 + {} 个套件补充入口；573 条原显示记录按文件路径去重。'.format(len(EXTRA)), '',
             '每个操作使用固定 operation ID；当前选择、通道、时间范围和原生配置由 Maya 上下文提供。', '',
             '| 分类 | 中文用途 | 入口数 | 详细索引 |', '| --- | --- | ---: | --- |']
    for category in sorted(categories):
        rows = [row for row in operations if row['category'] == category]
        zh, desc, _ = GROUPS.get(category, ('完整套件入口', '完整面板及媒体插件等补充入口。', 'UI'))
        filename = slug(category) + '.md'
        index.append('| {} | {} | {} | [{}](categories/{}) |'.format(category, zh, len(rows), zh, filename))
        lines = ['# ' + zh + '（' + category + '）', '', desc, '',
                 '- 状态：prepared_unverified，等待人工 Maya 直验。',
                 '- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。',
                 '- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。',
                 '- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。', '',
                 '| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |', '| --- | --- | --- | --- |']
        for row in rows:
            lines.append('| `{}` | {} | `{}` | {}；{} |'.format(row['id'], row['name'].replace('|', '\\|'), row['entrypoint'], row['description'].replace('|', '\\|'), row['effects']))
        lines += ['', '## 调用', '', '```python', 'tool.run(dry_run=True, action="invoke", operation_id=' + repr(rows[0]['id']) + ')', '# 阅读预检结果后再执行：', '# tool.run(action="invoke", operation_id=' + repr(rows[0]['id']) + ')', '```', '',
                  '所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。', '']
        (category_dir / filename).write_text('\n'.join(lines), encoding='utf-8')
    (DOCS / 'INDEX.md').write_text('\n'.join(index) + '\n', encoding='utf-8')
    print(json.dumps({'library_entries': len(operations) - len(EXTRA), 'supplemental_entries': len(EXTRA), 'categories': len(categories), 'native_files': len(source_hashes), 'patches': len(patches)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
