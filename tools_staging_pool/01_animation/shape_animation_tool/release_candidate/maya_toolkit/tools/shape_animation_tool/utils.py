"""JSON persistence and read-only, primitive-only compatibility with old SAT data."""
import ast
import io
import json
import pickle
from pathlib import Path


class PrimitiveUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        raise ValueError('Legacy pickle class/global references are refused')

    def persistent_load(self, pid):
        raise ValueError('Legacy persistent references are refused')


def decode_legacy(text):
    if len(text) > 1_000_000:
        raise ValueError('Legacy metadata too large')
    if text.startswith(("b'", 'b"')):
        data = ast.literal_eval(text)
        if not isinstance(data, bytes):
            raise ValueError('Expected literal bytes')
    else:
        data = text.encode('latin1')
    value = PrimitiveUnpickler(io.BytesIO(data), encoding='utf-8').load()
    def primitive(v):
        if v is None or type(v) in (str, int, float, bool):
            return True
        if type(v) in (list, tuple):
            return all(primitive(x) for x in v)
        if type(v) is dict:
            return all(primitive(k) and primitive(x) for k,x in v.items())
        return False
    if not primitive(value):
        raise ValueError('Only primitive legacy metadata is supported')
    return value


def attrToPy(objAttr):
    import maya.cmds as cmds
    text = cmds.getAttr(objAttr)
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return decode_legacy(text)


def pyToAttr(objAttr, data):
    """Only write attrs on this candidate's marked session nodes."""
    import maya.cmds as cmds
    from .runtime import OWNER, BRAND
    node, attr = objAttr.rsplit('.',1)
    if not cmds.attributeQuery(OWNER,node=node,exists=True) or cmds.getAttr(node+'.'+OWNER) != BRAND:
        raise ValueError('Unowned scene metadata cannot be written')
    if not cmds.objExists(objAttr):
        cmds.addAttr(node,longName=attr,dataType='string')
    if cmds.getAttr(objAttr,type=True)!='string' or cmds.getAttr(objAttr,lock=True):
        raise ValueError('Metadata attribute is locked or not a string')
    cmds.setAttr(objAttr,json.dumps(data,ensure_ascii=False,allow_nan=False),type='string')


def compileUI():
    """Preserve the original developer entry; absent .ui sources cannot be compiled."""
    sources = [Path(__file__).parent/(name+'.ui') for name in ('mainWindow','aboutWindow')]
    if not all(p.is_file() for p in sources):
        raise FileNotFoundError('Original mainWindow.ui/aboutWindow.ui were not supplied; generated UI is complete')
    raise RuntimeError('UI compilation requires explicit authoring to a separate output; runtime files are not overwritten')
