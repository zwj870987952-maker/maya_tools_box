"""Read-only long-task decisions. Never operates accounts, files or automations."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path


STATES = {'preparing', 'running', 'checkpointing', 'waiting_for_quota',
          'paused_by_user', 'needs_input', 'completed', 'stopped'}


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp must include a timezone')
    return result


def percent(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(label + ' must be a number')
    if not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError(label + ' must be finite and between 0 and 100')
    return float(value)


def result(action, reason, heartbeat, **details):
    return dict(action=action, reason=reason, suggested_heartbeat=heartbeat, **details)


def decide(state, snapshot, now=None, owner_round=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('now must include a timezone')
    status = state['state']
    if status not in STATES:
        raise ValueError('Unknown execution state')
    if status in {'completed', 'stopped'}:
        return result('remain_stopped', status, 'PAUSED')
    if status in {'paused_by_user', 'needs_input'}:
        return result('remain_paused', status, 'PAUSED')
    quota, stop = state['quota_policy'], state['stop_policy']
    if stop.get('operator', 'any') != 'any':
        raise ValueError('This helper supports any stop conditions; implement all conditions in the task controller')
    pause = percent(quota['pause_five_hour_remaining_pct'], 'pause threshold')
    resume = percent(quota['resume_five_hour_remaining_pct'], 'resume threshold')
    weekly_reserve = percent(quota['weekly_reserve_pct'], 'weekly reserve')
    if not pause < resume < 100 or weekly_reserve >= 100:
        raise ValueError('Require pause < resume < 100 and weekly reserve < 100')
    max_age = quota['snapshot_max_age_seconds']
    if isinstance(max_age, bool) or not isinstance(max_age, (int, float)) or not math.isfinite(max_age) or max_age <= 0:
        raise ValueError('Snapshot maximum age must be finite and positive')
    rounds = state.get('rounds_started', 0)
    maximum = stop.get('max_rounds')
    if isinstance(rounds, bool) or not isinstance(rounds, int) or rounds < 0:
        raise ValueError('rounds_started must be a nonnegative integer')
    if maximum is not None and (isinstance(maximum, bool) or not isinstance(maximum, int) or maximum <= 0):
        raise ValueError('max_rounds must be a positive integer or null')
    stop_reason = None
    if stop.get('deadline') and now >= timestamp(stop['deadline']):
        stop_reason = 'deadline_reached'
    if maximum is not None and rounds >= maximum and status in {'preparing', 'waiting_for_quota'}:
        stop_reason = stop_reason or 'maximum_rounds_reached'
    writer = state.get('writer')
    if writer:
        if not isinstance(writer, dict) or not writer.get('round_id'):
            raise ValueError('Writer must identify its round')
        if owner_round != writer['round_id']:
            return result('busy', 'Another round owns the checkpoint; verify actual liveness',
                          'PAUSED', pending_stop_reason=stop_reason)
    if state.get('completion_verified') is True:
        return result('finish', 'Completion was verified by the task controller', 'PAUSED')
    if stop_reason:
        return result('stop', stop_reason, 'PAUSED')
    if status in {'running', 'checkpointing'} and not writer:
        return result('retry_state', 'Unowned active state; inspect handoff and processes first', 'PAUSED')
    try:
        age = (now - timestamp(snapshot['observed_at'])).total_seconds()
        if not 0 <= age <= max_age:
            raise ValueError('Quota snapshot is stale or from the future')
        data = snapshot['data']
        if type(data.get('ordinaryUsageAllowed')) is not bool:
            raise ValueError('Ordinary usage permission is unknown')
        bucket_id = quota['bucket_id']
        if data.get('rateLimitsByLimitId') is not None:
            bucket = data['rateLimitsByLimitId'][bucket_id]
        else:
            bucket = data['rateLimits']
            if bucket.get('limitId') not in (bucket_id, None):
                raise ValueError('Legacy bucket does not match the selected limit')
        if bucket['primary']['windowDurationMins'] != 300 or bucket['secondary']['windowDurationMins'] != 10080:
            raise ValueError('Expected five-hour and weekly windows; adapt to actual account')
        five = 100 - percent(bucket['primary']['usedPercent'], 'five-hour usage')
        week = 100 - percent(bucket['secondary']['usedPercent'], 'weekly usage')
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        return result('retry_usage', str(error), 'PAUSED' if writer else 'KEEP',
                      save_checkpoint_first=bool(writer))
    details = dict(five_hour_remaining_pct=five, weekly_remaining_pct=week)
    for key, remaining in (('five_hour_remaining_floor_pct', five), ('weekly_remaining_floor_pct', week)):
        floor = stop.get(key)
        if floor is not None and remaining <= percent(floor, key):
            return result('stop', 'Permanent reserve floor reached: ' + key, 'PAUSED', **details)
    if not data['ordinaryUsageAllowed'] or five < pause or week < weekly_reserve:
        return result('save_and_wait' if writer else 'wait', 'Quota reserve or usage permission',
                      'ACTIVE', **details)
    estimate = state.get('next_unit_estimated_cost_pct')
    if estimate is not None and five - percent(estimate, 'next-unit estimate') <= pause:
        return result('save_and_wait' if writer else 'wait', 'Next unit crosses reserve; split or checkpoint',
                      'ACTIVE', **details)
    if status == 'waiting_for_quota':
        if five > resume and week > weekly_reserve:
            return result('prepare_resume', 'Pause heartbeat, verify ownership, then resume', 'PAUSED', **details)
        return result('wait', 'Recovery thresholds have not been exceeded', 'ACTIVE', **details)
    if status == 'preparing':
        return result('start_round', 'Confirmed plan can start its first round', 'PAUSED', **details)
    if status == 'checkpointing':
        return result('save_and_wait', 'Finish the already-started checkpoint transition', 'ACTIVE', **details)
    return result('continue', 'Current round can advance to its next safe step', 'PAUSED', **details)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', required=True)
    parser.add_argument('--usage', required=True)
    parser.add_argument('--owner-round', help='Current writer round; omit for heartbeat checks')
    parser.add_argument('--now', help='Timezone-aware replay time; omit in production')
    args = parser.parse_args()
    try:
        state = json.loads(Path(args.state).read_text(encoding='utf8'))
        usage_error = None
        try:
            snapshot = json.loads(Path(args.usage).read_text(encoding='utf8'))
        except (OSError, ValueError) as error:
            snapshot, usage_error = {}, str(error)
        response = decide(state, snapshot, timestamp(args.now) if args.now else None, args.owner_round)
        if usage_error and response['action'] == 'retry_usage':
            response['reason'] = usage_error
    except (OSError, KeyError, TypeError, ValueError, AttributeError) as error:
        print(json.dumps(result('retry_state', str(error), 'KEEP'), ensure_ascii=False))
        return 2
    print(json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
