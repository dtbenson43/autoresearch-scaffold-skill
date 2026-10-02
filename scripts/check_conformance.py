#!/usr/bin/env python3
"""Check bundled golden vectors or a generated reducer's JSON-output command."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from reference_reducer import ProtocolError, replay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, default=Path(__file__).resolve().parents[1] / 'references' / 'fixtures')
    parser.add_argument('--command', nargs=argparse.REMAINDER, help='command argv; fixture log path is appended; output JSON state, nonzero on rejection')
    args = parser.parse_args()
    manifest = json.loads((args.fixtures / 'manifest.json').read_text())
    failures = []
    for test in manifest['cases']:
        path = args.fixtures / test['log']
        try:
            if args.command:
                result = subprocess.run([*args.command, str(path)], capture_output=True, text=True, timeout=10)
                accepted = result.returncode == 0
                actual = json.loads(result.stdout) if accepted else None
            else:
                try:
                    actual = replay(path.read_bytes())
                    accepted = True
                except ProtocolError:
                    accepted, actual = False, None
            assert accepted == test['accept'], 'accept/reject mismatch'
            if accepted:
                expected = json.loads((args.fixtures / test['expected']).read_text())
                assert actual == expected, 'state mismatch'
            print('PASS', test['name'])
        except (AssertionError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
            failures.append(test['name'])
            print('FAIL', test['name'], str(exc))
    print('%s/%s passed' % (len(manifest['cases']) - len(failures), len(manifest['cases'])))
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
