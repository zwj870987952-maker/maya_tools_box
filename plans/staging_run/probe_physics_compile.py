"""Disposable Maya source-parser probe, definitions only; never opens original UI."""
import os
from pathlib import Path
import json
import sys

if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Isolated mayapy required')
sys.path.insert(0, str(Path(__file__).parent))
from review_physics_tools import SOURCE, procedures
import maya.standalone
maya.standalone.initialize(name='python')
from maya import mel, cmds

source = SOURCE.read_text(encoding='utf-8-sig')
rows = []
for row in procedures(source):
    text = 'global proc %s() {\n%s\n}' % (row['name'], row['body'])
    try:
        mel.eval(text)
        rows.append({'name': row['name'], 'passed': True})
    except Exception as error:
        rows.append({'name': row['name'], 'passed': False, 'error': str(error)})
help_text = cmds.help('diskCache')
node = cmds.createNode('diskCache')
attrs = {}
for a in cmds.listAttr(node) or []:
    try:
        attrs[a] = cmds.getAttr(node + '.' + a)
    except Exception:
        pass
cmds.delete(node)
result = {'procedures_compiled': rows, 'diskCache_help': help_text, 'diskCache_node_attrs': attrs, 'source_entry_executed': False, 'gui_acceptance': False}
(Path(__file__).parent / 'physics_tools_compile_probe.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'compiled': sum(r['passed'] for r in rows), 'failed': [r['name'] for r in rows if not r['passed']], 'entry_executed': False}, ensure_ascii=True))
