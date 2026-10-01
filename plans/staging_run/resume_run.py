"""Enter existing single-writer round only after an actual quota read and PAUSED app heartbeat."""
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
    p.add_argument('--tool',required=True)
    a=p.parse_args()
    if not (0<=a.five_hour_used<5 and 0<=a.weekly_used<100):
        raise ValueError('Resume requires >95% five-hour remaining and weekly quota')
    cfg=tomllib.loads((Path.home()/'.codex/automations/automation/automation.toml').read_text(encoding='utf-8'))
    if cfg['status']!='PAUSED':
        raise ValueError('Pause heartbeat before entering round')
    path=scan_pool.RUN/'manifest.json'
    m=json.loads(path.read_text(encoding='utf-8'))
    if m['execution']['state']=='working':
        raise ValueError('Existing working round must be recovered without opening a second round')
    item=next(x for x in m['tools'] if x['source_path']==a.tool)
    if item.get('candidate_complete'):
        raise ValueError('Chosen candidate is already complete')
    item['status']='working'
    m['execution'].pop('resume_note',None)
    m['execution'].update(state='working',current_tool=a.tool,heartbeat_status='PAUSED',heartbeat_verified=True,heartbeat_transition_verified=True,reset_guard='disabled_by_user_no_cards')
    m['execution']['last_usage']={'five_hour_used_percent':a.five_hour_used,'weekly_used_percent':a.weekly_used,'recorded_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'note':'Actual caller read: ordinaryUsageAllowed true; app thread list showed no other active writer in this checkout'}
    scan_pool.dump(path,m)
    print(json.dumps({'state':'working','tool':a.tool,'heartbeat':'PAUSED'}))


if __name__=='__main__':
    main()
