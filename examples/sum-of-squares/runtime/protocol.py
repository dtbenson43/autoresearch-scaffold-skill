#!/usr/bin/env python3
"""Portable v2 event replay oracle; Python standard library only. Not a controller."""
import argparse
import copy
import json
import sys


class ProtocolError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ProtocolError(message)


def fields(value, required, optional=()):
    require(isinstance(value, dict), 'expected object')
    require(set(required) <= set(value) <= set(required) | set(optional), 'invalid fields')


def ident(value):
    require(isinstance(value, str) and bool(value), 'expected nonempty identifier')


def integer(value):
    return type(value) is int and value >= 0


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def replay(data):
    """Reject every non-newline-terminated tail, including otherwise valid JSON."""
    require(isinstance(data, bytes), 'expected bytes')
    require(not data or data.endswith(b'\n'), 'torn tail')
    state = {'schemaVersion': 2, 'seq': 0, 'workflow': None, 'currentCandidate': None,
             'experiment': None, 'history': [], 'eventIds': [], 'attemptIds': [], 'experimentIds': []}
    try:
        decoded = data.decode('utf-8')
    except UnicodeError as exc:
        raise ProtocolError('invalid UTF-8') from exc
    for number, line in enumerate(decoded.split('\n')[:-1], 1):
        try:
            event = json.loads(line, object_pairs_hook=unique_object,
                               parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError('nonfinite JSON')))
            state = apply(state, event)
        except (ValueError, TypeError, KeyError, UnicodeError) as exc:
            raise ProtocolError('line %s: %s' % (number, exc)) from exc
    require(state['workflow'] is not None, 'missing initialization')
    return state


def apply(previous, e):
    s = copy.deepcopy(previous)
    require(isinstance(e, dict), 'expected event object')
    common = {'v', 'seq', 'id', 'type'}
    require(common <= set(e), 'missing envelope')
    require(type(e['v']) is int and e['v'] == 2, 'unsupported version')
    require(integer(e['seq']) and e['seq'] == s['seq'] + 1, 'nonmonotonic sequence')
    ident(e['id'])
    require(e['id'] not in s['eventIds'], 'duplicate event id')
    kind = e['type']
    w, x = s['workflow'], s['experiment']
    if kind == 'initialized':
        fields(e, common | {'workflow', 'baseline'})
        require(w is None and e['seq'] == 1, 'duplicate initialization')
        w = e['workflow']
        fields(w, {'initialStage', 'buildStage', 'edges', 'promotionOutcomes'})
        require(isinstance(w['edges'], dict) and bool(w['edges']), 'empty workflow')
        require(w['initialStage'] in w['edges'] and w['buildStage'] in w['edges'], 'unknown initial/build stage')
        require(isinstance(w['promotionOutcomes'], list), 'invalid promotion outcomes')
        for outcome in w['promotionOutcomes']:
            ident(outcome)
        for stage, edges in w['edges'].items():
            ident(stage)
            require(isinstance(edges, dict) and bool(edges), 'empty stage edges')
            for outcome, target in edges.items():
                ident(outcome)
                require(target is None or target in w['edges'], 'unknown edge target')
        fields(e['baseline'], {'id', 'mode'})
        ident(e['baseline']['id'])
        require(e['baseline']['mode'] in ('real', 'mock'), 'invalid baseline mode')
        s['workflow'], s['currentCandidate'] = w, e['baseline']
    else:
        require(w is not None, 'missing initialization')
        if kind == 'experiment_started':
            fields(e, common | {'experimentId', 'candidateId', 'parentId', 'mode'})
            require(x is None, 'experiment already open')
            for key in ('experimentId', 'candidateId', 'parentId'):
                ident(e[key])
            require(e['experimentId'] not in s['experimentIds'], 'duplicate experiment id')
            require(e['candidateId'] != s['currentCandidate']['id'] and all(e['candidateId'] not in (h['candidateId'], h['parentId']) for h in s['history']), 'duplicate candidate id')
            require(e['mode'] in ('real', 'mock'), 'invalid experiment mode')
            require(e['parentId'] == s['currentCandidate']['id'], 'stale candidate parent')
            s['experimentIds'].append(e['experimentId'])
            s['experiment'] = {k: e[k] for k in ('experimentId', 'candidateId', 'parentId', 'mode')}
            s['experiment'].update(stage=w['initialStage'], buildRevision=0, activeAttempt=None,
                                   lastOutcome=None, promoted=False, artifacts=[], builtRevision=None)
        elif kind in ('stage_started', 'stage_completed', 'stage_failed', 'stage_interrupted'):
            needed = common | {'experimentId', 'stage', 'attemptId', 'buildRevision'}
            if kind == 'stage_completed':
                needed |= {'outcome', 'nextStage', 'artifacts', 'promote'}
            elif kind in ('stage_failed', 'stage_interrupted'):
                needed |= {'reason'}
            fields(e, needed)
            require(x is not None and e['experimentId'] == x['experimentId'], 'wrong experiment')
            require(x['stage'] is not None and e['stage'] == x['stage'], 'wrong stage')
            require(integer(e['buildRevision']), 'invalid build revision')
            ident(e['attemptId'])
            if kind == 'stage_started':
                require(x['activeAttempt'] is None, 'attempt already active')
                require(e['attemptId'] not in s['attemptIds'], 'duplicate attempt id')
                revision = x['buildRevision'] + (x['stage'] == w['buildStage'])
                require(e['buildRevision'] == revision, 'wrong build revision')
                x['buildRevision'] = revision
                s['attemptIds'].append(e['attemptId'])
                x['activeAttempt'] = e['attemptId']
            else:
                require(x['activeAttempt'] == e['attemptId'], 'unmatched attempt')
                if kind == 'stage_completed':
                    require(e['outcome'] in w['edges'][x['stage']], 'unknown outcome')
                    require(e['nextStage'] == w['edges'][x['stage']][e['outcome']], 'illegal edge')
                    revision = x['buildRevision']
                    require(e['buildRevision'] == revision, 'wrong build revision')
                    require(isinstance(e['artifacts'], list), 'invalid artifacts')
                    paths = {a['path'] for record in [x, *s['history']] for a in record['artifacts']}
                    for a in e['artifacts']:
                        fields(a, {'path', 'sha256'})
                        ident(a['path'])
                        require(not a['path'].startswith('/') and '\\' not in a['path'] and all(p not in ('', '.', '..') for p in a['path'].split('/')), 'unsafe artifact path')
                        require(a['path'] not in paths, 'reused artifact path')
                        paths.add(a['path'])
                        require(isinstance(a['sha256'], str) and len(a['sha256']) == 64 and all(c in '0123456789abcdef' for c in a['sha256']), 'invalid artifact digest')
                    require(type(e['promote']) is bool, 'invalid promotion flag')
                    if e['promote']:
                        require(e['outcome'] in w['promotionOutcomes'] and e['nextStage'] is None, 'illegal promotion outcome')
                        require((x['builtRevision'] == revision or x['stage'] == w['buildStage']) and not x['promoted'], 'candidate not built or already promoted')
                        require(x['parentId'] == s['currentCandidate']['id'], 'stale candidate parent')
                        require(not (x['mode'] == 'mock' and s['currentCandidate']['mode'] == 'real'), 'mock cannot replace real')
                        s['currentCandidate'] = {'id': x['candidateId'], 'mode': x['mode']}
                        x['promoted'] = True
                    if x['stage'] == w['buildStage']:
                        x['builtRevision'] = revision
                    x.update(stage=e['nextStage'], buildRevision=revision, lastOutcome=e['outcome'])
                    x['artifacts'].extend(e['artifacts'])
                else:
                    ident(e['reason'])
                    require(e['buildRevision'] == x['buildRevision'], 'wrong build revision')
                x['activeAttempt'] = None
        elif kind == 'experiment_closed':
            fields(e, common | {'experimentId', 'outcome'})
            require(x is not None and x['experimentId'] == e['experimentId'], 'wrong experiment')
            require(x['activeAttempt'] is None and x['stage'] is None, 'experiment not terminal')
            require(e['outcome'] == x['lastOutcome'], 'wrong close outcome')
            s['history'].append(x)
            s['experiment'] = None
        else:
            raise ProtocolError('unknown event type')
    s['seq'] = e['seq']
    s['eventIds'].append(e['id'])
    return s


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', help='newline-terminated v2 JSONL log')
    args = parser.parse_args()
    try:
        with open(args.log, 'rb') as handle:
            state = replay(handle.read())
        print(json.dumps(state, sort_keys=True, indent=2))
    except (OSError, ProtocolError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
