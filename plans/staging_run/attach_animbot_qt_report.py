"""Record bounded offscreen evidence separately from real Maya GUI acceptance."""
import json
from pathlib import Path
from run_mayapy_check import python_fingerprint, runtime_fingerprint

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
rc = ROOT / 'tools_staging_pool/07_subsystems_suites/animbot_copy/release_candidate'
report = json.loads((RUN / 'animbot_copy_qt.json').read_text(encoding='utf-8'))
assert report['passed'] and report['returncode'] == 0
assert report['python_source_sha256'] == python_fingerprint(rc)
assert report['runtime_source_sha256'] == runtime_fingerprint(rc)
report['kind'] = 'qt_offscreen_widget_construction'
report['maya_initialized'] = False
report['gui_acceptance'] = False
report['limitations'] = ['No actual Maya docking or user mouse interaction', 'SWIG MObject leak warning on exit; exit code 0, real Maya repeated close/reopen pending']
manifest_path = RUN / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
item = next(t for t in manifest['tools'] if t['source_path'] == '07_subsystems_suites/animbot_copy')
item['offline_checks'] = [c for c in item['offline_checks'] if c['kind'] != report['kind']] + [report]
assert item['maya_acceptance']['status'] == 'not_run'
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'kind':report['kind'],'passed':True,'gui_acceptance':False}))
