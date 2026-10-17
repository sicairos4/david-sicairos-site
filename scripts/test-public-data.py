import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
AUDITOR = Path(__file__).with_name('audit-public-data.py').read_text()
BASE = {'name': 'YouTube', 'channelId': 'UCDMa9oEWj4i6KFOkjF79qLg', 'url': 'https://www.youtube.com/channel/UCDMa9oEWj4i6KFOkjF79qLg', 'followers': 44, 'followers28dAgo': None, 'source': 'YouTube Data API', 'status': 'API_SNAPSHOT', 'verified_on': '2026-10-17'}
HISTORY = {'followers28dAgo': 0, 'baseline_verified': True, 'baseline_source': 'Historical API snapshot', 'baseline_measured_at': '2026-09-19T00:00:00Z'}
CASES = [
    ('verified_count', {}, True),
    ('blank_source', {'source': '   '}, False),
    ('object_source', {'source': {}}, False),
    ('negative_count', {'followers': -1}, False),
    ('boolean_count', {'followers': True}, False),
    ('nonfinite_count', {'followers': float('nan')}, False),
    ('invalid_measurement_date', {'verified_on': 'invalid'}, False),
    ('verified_zero', {'followers': 0}, True),
    ('missing_baseline_evidence', {'followers28dAgo': 0}, False),
    ('valid_baseline', HISTORY, True),
    ('blank_baseline_source', {**HISTORY, 'baseline_source': '  '}, False),
    ('invalid_baseline_date', {**HISTORY, 'baseline_measured_at': 'invalid'}, False),
    ('future_baseline', {**HISTORY, 'baseline_measured_at': '2026-10-18T00:00:00Z'}, False),
    ('wrong_period', {**HISTORY, 'baseline_measured_at': '2026-10-01T00:00:00Z'}, False),
    ('negative_baseline', {**HISTORY, 'followers28dAgo': -1}, False),
    ('nonfinite_baseline', {**HISTORY, 'followers28dAgo': float('inf')}, False),
    ('verified_zero_growth', {**HISTORY, 'followers': 0}, True)
]
class PublicDataTests(unittest.TestCase):
    def check_case(self, overrides, expected):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'scripts').mkdir()
            (root / 'data').mkdir()
            script = root / 'scripts/audit-public-data.py'
            script.write_text(AUDITOR)
            (root / 'data/site-config.json').write_text(json.dumps({'socialPulse': [{**BASE, **overrides}]}))
            result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=10)
            self.assertIn(result.returncode, (0, 1), result.stderr)
            self.assertEqual(result.returncode == 0, expected, result.stdout + result.stderr)
            report = json.loads((root / 'qa-artifacts/public-data-audit.json').read_text())
            self.assertEqual(not report['errors'], expected)
def make_test(overrides, expected):
    def test(self):
        self.check_case(overrides, expected)
    return test
for name, overrides, expected in CASES:
    setattr(PublicDataTests, 'test_' + name, make_test(overrides, expected))
if __name__ == '__main__':
    unittest.main(verbosity=2)
