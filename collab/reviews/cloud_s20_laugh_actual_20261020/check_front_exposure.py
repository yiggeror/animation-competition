"""Check new production exposure against the adopted external 036–057 table."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parent
source = json.loads((P / 'integration_000_143/036_057_exposure.adopted.json').read_text())
production = json.loads((ROOT / 'assets/chars/g20/sequence.json').read_text())
for hold in source['holds']:
    for frame in range(hold['start_inclusive'], hold['end_exclusive']):
        rows = [s for s in production['states'] if s['start'] <= frame <= s['end']]
        assert len(rows) == 1, f'Adopted frame{frame} must have exactly one production exposure'
        assert rows[0]['key'] == hold['state'], f'Wrong adopted drawing at{frame}'
        assert rows[0].get('geometry'), f'Frame{frame} requires its actual T/finite-rod geometry'
for path, sha in [
    ('integration_000_143/first36_actual/S20_000_035_actual.mp4', 'bd3e3372342f340f58ef659e475eeac0a2699042766235728dd0cea1aab14c25'),
    ('laugh_four_states_20261020/actual/S20_laugh_144_215_actual.mp4', '2d4d3639f9f1369163fb04644ee747ef7295cc49ae3374662bda23bd0c1a7435'),
]:
    assert hashlib.sha256((P / path).read_bytes()).hexdigest() == sha, 'Accepted video changed'
print('PASS: all22 adopted exposures selected exactly, per-state geometry required, prior MP4 bytes retained.')
