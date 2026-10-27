# -*- coding: utf-8 -*-
"""Structural editorial decisions: which section a line belongs to and where a composition
begins. Post-pass 5 of build_corpus.py, read from pipeline/structure_ledger.json.

The print-derived structure is right almost everywhere; a few printed headings and labels are not
read by the detectors (a salok collection whose heading carries no Mahalla, a bare Bhagat label
set inside the previous Bhagat's composition). Fixing those by changing a detector would renumber
every later composition, so each one is a reviewed ledger entry instead.

This pass changes `section`, `is_header`, `comp_id` and `line_no` ONLY -- never text, markers or
author -- and only for entries g3_gate.py lets through: a complete G3 ruling (`approved`), or `held` in
a draft that the release check keeps from shipping. Every entry states what it expects to
find (`from`); if the corpus no longer matches, the build fails rather than apply an entry to lines
it was not written for.

Kinds:
  section  lines start_id..end_id move from section `from` to section `to`.
  opens    line start_id is a printed label that opens a composition (is_header 0 -> 1), and
           lines start_id..end_id leave composition `from` for the new composition `to`. A new id
           is issued above every id the build has ever issued (`issued`), so no existing comp_id
           moves and no vacated (burned) id is reused.
"""
import g3_gate


class LedgerMismatch(Exception):
    pass


def load_ledger(path):
    return g3_gate.load('structure', path)


def apply(records, ledger, issued):
    """Mutates records in place; returns the change log. `issued` is the highest comp_id the
    build issued (build_corpus's comp_seq), burned ids included."""
    log = []
    by_id = {r['id']: r for r in records}
    approved = g3_gate.check(ledger, 'structure')

    def rows(e):
        out = [by_id.get(i) for i in range(e['start_id'], e['end_id'] + 1)]
        if None in out or not out:
            raise LedgerMismatch(f"{e['entry']}: ids {e['start_id']}-{e['end_id']} not all in the corpus")
        return out

    def change(r, field, new, e):
        if r[field] != new:
            log.append({'id': r['id'], 'ang': r['ang'], 'field': field, 'from': r[field], 'to': new,
                        'entry': e['entry']})
            r[field] = new

    # ---- section ---------------------------------------------------------------
    for e in (e for e in approved if e['kind'] == 'section'):
        rs = rows(e)
        bad = [r['id'] for r in rs if r['section'] != e['from']]
        if bad:
            raise LedgerMismatch(f"{e['entry']}: expected section {e['from']!r} on every line, "
                                 f"not on ids {bad[:5]}")
        for r in rs:
            change(r, 'section', e['to'], e)

    # ---- opens -----------------------------------------------------------------
    opens = [e for e in approved if e['kind'] == 'opens']
    starts = {e['start_id'] for e in opens}
    used = {r['comp_id'] for r in records}
    new_ids = [e['to'] for e in opens]
    if len(set(new_ids)) != len(new_ids):
        raise LedgerMismatch(f'opens: a new comp_id is issued twice: {sorted(new_ids)}')
    touched = set()
    for e in opens:
        rs = rows(e)
        if e['to'] <= issued or e['to'] in used:
            raise LedgerMismatch(f"{e['entry']}: new comp_id {e['to']} must be above every issued id "
                                 f"({issued}) and unused")
        bad = [r['id'] for r in rs if r['comp_id'] != e['from']]
        if bad:
            raise LedgerMismatch(f"{e['entry']}: expected comp_id {e['from']} on every line, not on ids {bad[:5]}")
        if rs[0]['is_header']:
            raise LedgerMismatch(f"{e['entry']}: id {rs[0]['id']} is already a header")
        nxt = by_id.get(e['end_id'] + 1)
        if nxt is not None and nxt['comp_id'] == e['from'] and nxt['id'] not in starts:
            raise LedgerMismatch(f"{e['entry']}: id {nxt['id']} would be left behind in comp {e['from']} "
                                 f"after the new composition")
        change(rs[0], 'is_header', 1, e)
        for r in rs:
            change(r, 'comp_id', e['to'], e)
        touched |= {e['from'], e['to']}

    # line_no runs 1..N within every composition this pass touched (id order)
    seen = {}
    for r in records:
        c = r['comp_id']
        if c in touched:
            seen[c] = seen.get(c, 0) + 1
            if r['line_no'] != seen[c]:
                log.append({'id': r['id'], 'ang': r['ang'], 'field': 'line_no', 'from': r['line_no'],
                            'to': seen[c], 'entry': 'renumber'})
                r['line_no'] = seen[c]
    return log
