import hashlib
import json
from pathlib import Path
from .contracts import preset_data

ATTR = 'mtbCGShakeCache'
OWNER = 'maya_toolkit.cg_shake_py3.v1'


def default_data_root():
    from maya import cmds
    return Path(cmds.internalVar(userAppDir=True)) / 'maya_toolkit/cgshake'


def plugin_loaded():
    from maya import cmds
    try:
        return bool(cmds.pluginInfo('animImportExport', query=True, loaded=True))
    except RuntimeError:
        return False


def path(value, suffix, write=False, overwrite=False):
    target = Path(value)
    if not value or not target.is_absolute() or target.suffix.casefold() != suffix:
        raise ValueError('需要绝对' + suffix + '路径')
    target = target.resolve()
    if target.exists() and not target.is_file():
        raise ValueError('目标不是普通文件: ' + str(target))
    if write and target.exists() and not overwrite:
        raise ValueError('文件已存在；覆盖需overwrite_file=True: ' + str(target))
    if not write and not target.is_file():
        raise ValueError('文件不存在: ' + str(target))
    return target


def digest(target):
    return hashlib.sha256(Path(target).read_bytes()).hexdigest()


def cache_record(node, explicit=''):
    from maya import cmds
    if not cmds.attributeQuery(ATTR, node=node, exists=True):
        raise ValueError('目标没有本候选cache记录')
    if cmds.getAttr(node + '.' + ATTR, type=True) != 'string':
        raise ValueError('cache属性非本候选格式')
    record = json.loads(cmds.getAttr(node + '.' + ATTR))
    if record.get('owner') != OWNER or record.get('uuid') != cmds.ls(node, uuid=True)[0]:
        raise ValueError('cache Owner/目标UUID不匹配')
    target = path(explicit or record['path'], '.anim')
    if str(target) != str(Path(record['path']).resolve()) or digest(target) != record['sha256']:
        raise ValueError('cache路径/内容已变化，不允许清键后猜测恢复')
    sidecar = Path(str(target) + '.json')
    if not sidecar.is_file() or json.loads(sidecar.read_text(encoding='utf-8')) != record:
        raise ValueError('cache sidecar不匹配')
    return record


def load_preset(target):
    return preset_data(json.loads(Path(target).read_text(encoding='utf-8')))
