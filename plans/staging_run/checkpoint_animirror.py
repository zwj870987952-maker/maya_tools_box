"""Save explicit incomplete work and last actual usage before quota wait."""
import datetime
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'plans/staging_run/manifest.json'
manifest = json.loads(PATH.read_text(encoding='utf-8'))
item = next(row for row in manifest['tools'] if row['source_path'] == '01_animation/animirror_v2_0')
item.update(status='working', candidate_complete=False, candidate_path='tools_staging_pool/01_animation/animirror_v2_0/release_candidate',
            work_notes='plans/staging_run/animirror_v2_0_notes.md', exploratory_probe='plans/staging_run/animirror_suite_probe.json',
            change_summary='Original MEL/PDF archived, all 9 embedded procedures extracted and namespaced, strict axis-based JSON contract drafted. Isolated compile and actual X-translation mirror/cleanup with UI query stubs passed. API/ownership/Undo/UI/promotion/acceptance incomplete.',
            issues=['Incomplete candidate; do not count as processed or promote', 'lookdevKit/floatMath must be explicitly loaded by user; preflight should query only',
                    'GUI/rotation/other axes/center transforms/bake pending', 'UUID deletion protection and persistent Undo-aware ownership not implemented'])
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
manifest['execution'].update(state='waiting_for_quota', current_tool='01_animation/animirror_v2_0', heartbeat_status='PAUSED',
                             last_usage={'five_hour_used_percent': 95, 'weekly_used_percent': 56, 'recorded_at': stamp, 'note': 'Actual tool read before checkpoint; 5 percent primary remaining. Partial complex item saved before hard limit.'})
manifest['updated_at'] = stamp
PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'complete_candidates': sum(bool(row.get('candidate_complete')) for row in manifest['tools']), 'incomplete': item['source_path'], 'remaining_five_hour': 5}))
