"""Boundary and recovery scenarios; no account or automation access."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import unittest

from quota_decision import decide


NOW = datetime(2026, 10, 4, 4, tzinfo=timezone.utc)


def state(status='running'):
    return {'state': status, 'completion_verified': False,
            'quota_policy': {'bucket_id': 'codex', 'pause_five_hour_remaining_pct': 6,
                             'resume_five_hour_remaining_pct': 95, 'weekly_reserve_pct': 1,
                             'snapshot_max_age_seconds': 300},
            'stop_policy': {'deadline': None, 'max_rounds': None,
                            'five_hour_remaining_floor_pct': None, 'weekly_remaining_floor_pct': None},
            'rounds_started': 1, 'writer': {'round_id': 'r1'} if status == 'running' else None,
            'next_unit_estimated_cost_pct': None}


def usage(five=50, week=25, allowed=True):
    return {'observed_at': NOW.isoformat(), 'data': {'ordinaryUsageAllowed': allowed,
            'rateLimitsByLimitId': {'codex': {
                'primary': {'usedPercent': 100 - five, 'windowDurationMins': 300},
                'secondary': {'usedPercent': 100 - week, 'windowDurationMins': 10080}}}}}


class Decisions(unittest.TestCase):
    def action(self, task=None, snapshot=None, owner='r1'):
        return decide(state() if task is None else task, usage() if snapshot is None else snapshot, NOW, owner)['action']

    def test_pause_strict_boundary(self):
        self.assertEqual(self.action(snapshot=usage(five=6)), 'continue')
        self.assertEqual(self.action(snapshot=usage(five=5.9)), 'save_and_wait')

    def test_resume_strict_boundary(self):
        for remaining, action in ((95, 'wait'), (95.1, 'prepare_resume')):
            self.assertEqual(self.action(state('waiting_for_quota'), usage(five=remaining)), action)

    def test_weekly_window_blocks_full_five_hour(self):
        self.assertEqual(self.action(state('waiting_for_quota'), usage(100, 0)), 'wait')
        self.assertEqual(self.action(state('waiting_for_quota'), usage(100, 1)), 'wait')
        self.assertEqual(self.action(state('waiting_for_quota'), usage(100, 1.1)), 'prepare_resume')

    def test_expensive_next_unit_does_not_start(self):
        task = state(); task['next_unit_estimated_cost_pct'] = 5
        self.assertEqual(self.action(task, usage(five=11)), 'save_and_wait')

    def test_unknown_stale_and_future_snapshots(self):
        self.assertEqual(self.action(snapshot={}), 'retry_usage')
        for changed in (None, -1, float('nan'), True):
            snapshot = usage(); snapshot['data']['rateLimitsByLimitId']['codex']['primary']['usedPercent'] = changed
            self.assertEqual(self.action(snapshot=snapshot), 'retry_usage')
        for delta in (-301, 1):
            snapshot = usage(); snapshot['observed_at'] = (NOW + timedelta(seconds=delta)).isoformat()
            self.assertEqual(self.action(snapshot=snapshot), 'retry_usage')
        self.assertEqual(self.action(snapshot=usage(allowed=None)), 'retry_usage')

    def test_wrong_window_and_wrong_legacy_bucket(self):
        snapshot = usage(); snapshot['data']['rateLimitsByLimitId']['codex']['primary']['windowDurationMins'] = 60
        self.assertEqual(self.action(snapshot=snapshot), 'retry_usage')
        snapshot = usage(); bucket = snapshot['data'].pop('rateLimitsByLimitId')['codex']
        bucket['limitId'] = 'other'; snapshot['data']['rateLimits'] = bucket
        self.assertEqual(self.action(snapshot=snapshot), 'retry_usage')

    def test_legacy_bucket_is_read_only(self):
        snapshot = usage(); snapshot['data']['rateLimits'] = snapshot['data'].pop('rateLimitsByLimitId')['codex']
        original = deepcopy(snapshot)
        self.assertEqual(self.action(snapshot=snapshot), 'continue')
        self.assertEqual(snapshot, original)

    def test_completion_has_priority_over_low_quota(self):
        task = state(); task['completion_verified'] = True
        self.assertEqual(self.action(task, usage(0, 0)), 'finish')

    def test_terminal_and_manual_pause_never_resume(self):
        for status in ('completed', 'stopped'):
            self.assertEqual(self.action(state(status), {}), 'remain_stopped')
        for status in ('paused_by_user', 'needs_input'):
            self.assertEqual(self.action(state(status), {}), 'remain_paused')

    def test_timezone_deadline_does_not_need_quota(self):
        task = state(); task['stop_policy']['deadline'] = '2026-10-04T12:00:00+08:00'
        self.assertEqual(self.action(task, {}), 'stop')

    def test_other_owner_is_not_overwritten_even_at_deadline(self):
        task = state(); task['stop_policy']['deadline'] = NOW.isoformat()
        original = deepcopy(task)
        response = decide(task, usage(), NOW)
        self.assertEqual(response['action'], 'busy')
        self.assertEqual(response['pending_stop_reason'], 'deadline_reached')
        self.assertEqual(task, original)

    def test_round_cap_only_blocks_next_round(self):
        task = state(); task['stop_policy']['max_rounds'] = 1
        self.assertEqual(self.action(task), 'continue')
        task['state'] = 'waiting_for_quota'; task['writer'] = None
        self.assertEqual(self.action(task, usage(100, 50)), 'stop')

    def test_permanent_reserve_is_not_a_wait(self):
        task = state(); task['stop_policy']['five_hour_remaining_floor_pct'] = 10
        self.assertEqual(self.action(task, usage(five=10)), 'stop')

    def test_usage_denied_does_not_use_credits(self):
        self.assertEqual(self.action(snapshot=usage(100, 100, False)), 'save_and_wait')

    def test_missing_writer_requires_inspection(self):
        task = state(); task['writer'] = None
        self.assertEqual(self.action(task), 'retry_state')

    def test_bad_policy_is_rejected(self):
        task = state(); task['quota_policy']['resume_five_hour_remaining_pct'] = 100
        with self.assertRaises(ValueError):
            decide(task, usage(), NOW, 'r1')

    def test_all_stop_conditions_are_not_silently_treated_as_any(self):
        task = state(); task['stop_policy']['operator'] = 'all'
        with self.assertRaises(ValueError):
            decide(task, usage(), NOW, 'r1')

    def test_preparing_does_not_require_full_reset(self):
        self.assertEqual(self.action(state('preparing'), usage(50, 25)), 'start_round')


if __name__ == '__main__':
    unittest.main()
