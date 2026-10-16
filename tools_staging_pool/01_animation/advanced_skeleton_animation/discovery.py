"""Find installed ADV copies without loading MEL or mutating Maya preferences."""
from decimal import Decimal, InvalidOperation
from functools import lru_cache
import os
from pathlib import Path
import re
import time

_CACHE = {}


def version_key(version):
    parts = version.split('.')
    try:
        return (Decimal('.'.join(parts[:2])), tuple(int(p) for p in parts[2:]))
    except (InvalidOperation, ValueError):
        raise ValueError('无法识别 ADV 版本: ' + version)


@lru_cache(maxsize=48)
def _inspect(path, mtime_ns, size):
    source = Path(path)
    text = source.read_text(encoding='utf-8-sig', errors='replace')
    match = re.search(r'//\s*Version\s+([\d.]+)', text[:1800])
    if not match or not re.search(r'^global proc asMirror\s*\(', text, re.M):
        raise ValueError('不是可识别的 ADV 原版入口: ' + path)
    version = match.group(1)
    if version_key(version)[0] < 6:
        raise ValueError('需要 ADV 6.x 或更新版本。')
    if not (source.parent / 'AdvancedSkeletonFiles').is_dir():
        raise ValueError('缺少 AdvancedSkeletonFiles 资源目录: ' + path)
    return {'source_path': source.as_posix(), 'version': version,
            'verified_version': version == '6.640',
            'procedures': frozenset(re.findall(r'^global proc (?:\w+(?:\[\])? )?(\w+)\s*\(', text, re.M))}


def inspect(path):
    source = Path(path).expanduser().resolve()
    if source.suffix.lower() != '.mel' or not source.is_file():
        raise ValueError('请指定存在的 AdvancedSkeleton.mel 文件。')
    stat = source.stat()
    return dict(_inspect(str(source), stat.st_mtime_ns, stat.st_size))


def _roots(extra_roots=()):
    roots = list(extra_roots)
    roots.extend(p for p in os.environ.get('ADVANCED_SKELETON_PATH', '').split(os.pathsep) if p)
    roots.extend(p for p in os.environ.get('MAYA_SCRIPT_PATH', '').split(os.pathsep) if p)
    roots.extend([Path.home()/'Documents/maya/scripts'])
    for drive in ('C:', 'D:', 'E:', 'F:'):
        roots.extend([Path(drive+'/TOOLS/adv_rig'), Path(drive+'/Tools/AdvancedSkeleton')])
    try:
        import maya.cmds as cmds
        import maya.mel as mel
        roots.append(cmds.internalVar(userScriptDir=True))
        for key in ('mayaToolkitAdvancedSkeletonSearchRoots', 'mayaToolkitAdvancedSkeletonMirrorSource'):
            if cmds.optionVar(exists=key):
                value = cmds.optionVar(q=key)
                roots.extend(value if isinstance(value, list) else [value])
        loaded = mel.eval('whatIs asMirror')
        if loaded.startswith('Mel procedure found in: '):
            roots.append(loaded.split('Mel procedure found in: ', 1)[1])
    except ImportError:
        pass
    expanded = []
    for root in roots:
        p = Path(root).expanduser()
        if p.suffix.lower() == '.mel':
            expanded.extend([p, p.parent.parent])
        else:
            expanded.append(p)
    return sorted({str(p.resolve()) for p in expanded if p.exists()})


def discover(extra_roots=(), refresh=False):
    """Bounded installed-location discovery; never recursively scan entire drives."""
    roots = _roots(extra_roots)
    key = tuple(roots)
    cached = _CACHE.get(key)
    if not refresh and cached and time.monotonic()-cached[0] < 60:
        return [dict(item) for item in cached[1] if Path(item['source_path']).is_file()]
    found = {}
    for root in roots:
        path = Path(root)
        paths = [path] if path.is_file() else []
        if path.is_dir():
            for pattern in ('AdvancedSkeleton*.mel', '*/AdvancedSkeleton*.mel', '*/*/AdvancedSkeleton*.mel'):
                paths.extend(path.glob(pattern))
        for candidate in paths:
            try:
                info = inspect(candidate)
                # Local project vendor is a fallback, not an installation preference.
                info['project_backup'] = 'tools_closed_source_pool' in candidate.parts
                info.pop('procedures')
                found[info['source_path'].lower()] = info
            except (OSError, ValueError):
                pass
    result = sorted(found.values(), key=lambda i: (not i['project_backup'], version_key(i['version']), i['source_path'].lower()), reverse=True)
    _CACHE[key] = (time.monotonic(), result)
    return [dict(item) for item in result]


def resolve(source_path=None, required_procedures=(), refresh=False):
    if source_path:
        info = inspect(source_path)
    else:
        candidates = discover(refresh=refresh)
        if not candidates:
            raise ValueError('未找到本机 ADV 6.x 安装。请指定 source_path 或设置 ADVANCED_SKELETON_PATH 搜索目录。')
        info = inspect(candidates[0]['source_path'])
    missing = set(required_procedures)-info['procedures']
    if missing:
        raise ValueError('本机最新版 ADV 缺少所需入口，未自动回退旧版: ' + ', '.join(sorted(missing)))
    info.pop('procedures')
    return info
