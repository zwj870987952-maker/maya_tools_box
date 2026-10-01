"""Record actual caller-observed quota and verified ACTIVE heartbeat, without using credits."""
import argparse
import datetime
import json
from pathlib import Path
import tomllib
import scan_pool


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--five-hour-used',required=True,type=float)
    p.add_argument('--weekly-used',required=True,type=float)
    p.add_argument('--next-tool',required=True)
    a=p.parse_args()
    if not all(0<=v<=100 for v in (a.five_hour_used,a.weekly_used)):
        raise ValueError('Actual usage required')
    cfg=tomllib.loads((Path.home()/'.codex/automations/automation/automation.toml').read_text(encoding='utf-8'))
    if cfg['id']!='automation' or cfg['status']!='ACTIVE':
        raise ValueError('App heartbeat must be confirmed ACTIVE before recording wait')
    path=scan_pool.RUN/'manifest.json'
    manifest=json.loads(path.read_text(encoding='utf-8'))
    following=next(x for x in manifest['tools'] if x['source_path']==a.next_tool)
    if following.get('candidate_complete'):
        raise ValueError('Next tool is already complete')
    # Preserve incomplete working packages so the next round resumes them.
    has_partial_candidate = (scan_pool.POOL/a.next_tool/'release_candidate').is_dir()
    if not has_partial_candidate:
        following['status']='pending'
    boundary = 'Saved incomplete working candidate; resume its existing files and finish verification.' if has_partial_candidate else 'Stopped at completed candidate boundary.'
    manifest['execution'].update(state='waiting_for_quota',heartbeat_status='ACTIVE',heartbeat_verified=True,heartbeat_transition_verified=True,current_tool=a.next_tool,reset_guard='disabled_by_user_no_cards',resume_note=boundary+' Resume only with five-hour remaining >95%, weekly allowed, and no other active round. Do not consume reset credits or purchase quota.')
    manifest['execution']['last_usage']={'five_hour_used_percent':a.five_hour_used,'weekly_used_percent':a.weekly_used,'recorded_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'note':'Actual caller-observed usage; percentages record used quota, not remaining quota.'}
    scan_pool.dump(path,manifest)
    print(json.dumps({'state':'waiting_for_quota','heartbeat':'ACTIVE','completed':sum(bool(x.get('candidate_complete')) for x in manifest['tools']),'next':a.next_tool}))


if __name__=='__main__':
    main()
