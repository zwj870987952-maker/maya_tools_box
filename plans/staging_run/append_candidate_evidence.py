"""Append an additional isolated check only when its payload hashes match."""
import argparse,json
from pathlib import Path
import scan_pool
from run_mayapy_check import python_fingerprint,runtime_fingerprint
p=argparse.ArgumentParser();p.add_argument('--tool',required=True);p.add_argument('--report',required=True);a=p.parse_args()
candidate=scan_pool.POOL/a.tool/'release_candidate'
report=json.loads(Path(a.report).read_text(encoding='utf8'))
if report.get('python_source_sha256')!=python_fingerprint(candidate) or report.get('runtime_source_sha256')!=runtime_fingerprint(candidate):raise ValueError('Additional check differs from candidate')
report['evidence_path']=Path(a.report).as_posix()
data=json.loads((scan_pool.RUN/'manifest.json').read_text(encoding='utf8'))
item=next(r for r in data['tools'] if r['source_path']==a.tool)
item['offline_checks']=[r for r in item['offline_checks'] if r.get('evidence_path')!=report['evidence_path']]+[report]
if not report['passed']:item['status']='prepared_unverified'
scan_pool.dump(scan_pool.RUN/'manifest.json',data)
print(json.dumps({'tool':a.tool,'evidence':a.report,'passed':report['passed']}))
