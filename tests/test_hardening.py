"""Tests for the verification layers added after reviewing the remote-proposal.

Each test covers a safeguard that could otherwise read as stronger than it is:
a baseline receipt that vouches for itself, an equal-length rewrite that only
happens to hold arithmetically, and a report that records state it never reads.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import portal_auto as a
import portal_active_probe as p
from test_probe import fixture


class LengthInvariantTests(unittest.TestCase):
    """Equal length is the whole premise. It must be enforced, not incidental."""

    def test_every_mask_width_preserves_frame_length(self):
        data, plain, stream, pos = fixture()
        masks = list(a.PROFILES.values()) + [b'\x01', b'\x09' * 9, b'\x7f' * 40, b'\x04' * 200]
        for delta in masks:
            with patch.object(p, 'PATCH_DELTA', delta):
                out, changed = p.mutate(data)
                if changed:
                    self.assertEqual(len(out), len(data),
                                     'a %d-byte mask resized the startup frame' % len(delta))
                else:
                    self.assertEqual(out, data, 'a refusal must return bytes untouched')

    def test_oversized_mask_never_truncates(self):
        data, *_ = fixture()
        for width in (500, 900):
            with patch.object(p, 'PATCH_DELTA', b'\x04' * width):
                out, changed = p.mutate(data)
                self.assertEqual(len(out), len(data))
                self.assertIsInstance(changed, bool)


class GuardianHandbackTests(unittest.TestCase):
    """The guardian's own receipt, not the parent's assumption, is the evidence."""

    def handback(self, root, payload):
        if payload is not None:
            a.atomic_json(root / 'recovery.json', payload)
        return root

    def test_clean_relay_closure_is_a_handback(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertTrue(a.handed_back(self.handback(Path(td), {'reason': 'relay_closed', 'errors': []})))

    def test_every_other_outcome_is_refused(self):
        cases = ({'reason': 'heartbeat_timeout', 'errors': []},
                 {'reason': 'relay_closed', 'errors': ['adapter down']},
                 {'reason': 'relay_closed'},
                 {},
                 None)
        with tempfile.TemporaryDirectory() as td:
            for case in cases:
                self.assertFalse(a.handed_back(self.handback(Path(td), case)), case)


class BaselineGateTests(unittest.TestCase):
    """Three things must agree before any Profile may rewrite Portal bytes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.c = {'network': {'interface': 'en0', 'ps5_ip': '192.0.2.10', 'portal_ip': '192.0.2.20'},
                  'profile': '65', 'ps5_mac': '02:00:00:00:00:02', 'portal_mac': '02:00:00:00:00:03'}

    def tearDown(self):
        self.tmp.cleanup()

    def receipt(self, **over):
        payload = {'time': a.utc(), 'fingerprint': a.fingerprint(self.c),
                   'forwarded_out': 9, 'restored': True}
        payload.update(over)
        a.atomic_json(self.root / 'auto-baseline.json', payload)

    def confirm(self, **over):
        payload = {'time': a.utc(), 'fingerprint': a.fingerprint(self.c)}
        payload.update(over)
        a.atomic_json(self.root / 'auto-baseline-confirmed.json', payload)

    def test_gate_needs_transport_handback_and_eyes(self):
        self.assertFalse(a.baseline_valid(self.c, self.root), 'an empty runtime must not pass')
        self.receipt()
        self.assertFalse(a.baseline_valid(self.c, self.root),
                         'relayed bytes alone must not license a mutation')
        self.confirm()
        self.assertTrue(a.baseline_valid(self.c, self.root))

    def test_unverified_restoration_vetoes_the_receipt(self):
        self.receipt(restored=False)
        self.confirm()
        self.assertFalse(a.baseline_valid(self.c, self.root))

    def test_zero_forwarded_traffic_vetoes_the_receipt(self):
        self.receipt(forwarded_out=0)
        self.confirm()
        self.assertFalse(a.baseline_valid(self.c, self.root))

    def test_stale_confirmation_does_not_outlive_a_new_baseline(self):
        self.receipt()
        self.confirm()
        self.assertTrue(a.baseline_valid(self.c, self.root))
        # Re-running baseline tomorrow must invalidate today's eyeball check.
        self.receipt(time='2099-01-01T00:00:00+00:00')
        self.assertFalse(a.baseline_valid(self.c, self.root))

    def test_confirmation_does_not_carry_to_another_configuration(self):
        self.receipt()
        self.confirm()
        self.assertTrue(a.baseline_valid(self.c, self.root))
        self.c['profile'] = '200'
        self.assertFalse(a.baseline_valid(self.c, self.root), 'each profile needs its own baseline')

    def test_receipt_restored_flag_follows_the_guardian_verdict(self):
        counts = {'forwarded_out': 9}
        # A missing guardian receipt is a veto, never a pass.
        self.assertFalse(a.baseline_receipt(self.c, counts, [], self.root)['restored'])
        a.atomic_json(self.root / 'recovery.json', {'reason': 'relay_closed', 'errors': []})
        self.assertTrue(a.baseline_receipt(self.c, counts, [], self.root)['restored'])
        # A restoration error vetoes even a finish that reached the last line.
        self.assertFalse(a.baseline_receipt(self.c, counts, ['adapter down'], self.root)['restored'])

    def test_receipt_records_why_it_refused(self):
        receipt = a.baseline_receipt(self.c, {'forwarded_out': 9}, ['adapter down'], self.root)
        self.assertEqual(receipt['restoration_errors'], ['adapter down'])
        self.assertFalse(receipt['guardian_handback_verified'])
        self.assertFalse(receipt['restored'])


if __name__ == '__main__':
    unittest.main()
