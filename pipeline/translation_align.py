# -*- coding: utf-8 -*-
"""Order-aware alignment of translation records to corpus lines (pure; no DB writes).

Both streams are in Granth order: corpus lines by id, source records in file order
(shabados_ingest.py writes them ORDER BY order_id). Alignment is monotonic, so a
repeated line (a refrain, a heading) can only take the record of its own occurrence,
and one record may cover 2-4 consecutive printed lines of one composition (a "span").

1. Anchors: records whose normalised text occurs exactly once in the source AND once in
   the corpus, at an Ang within 1, kept only where they are mutually in order (LIS).
2. Between consecutive anchors, a small DP aligns the gap with these steps:
   skip a record, skip a line, 1:1 (exact / skeleton / fuzzy >= 0.92), 1:k exact span.
3. The DP runs twice, preferring the earliest and then the latest of equal-cost paths.
   A placement that the two runs disagree on is ambiguous and is NOT placed: no English
   is better than English under the wrong line.
"""
import re, unicodedata, difflib, bisect

MATRAS = 'ਾਿੀੁੂੇੈੋੌ੍ੰਂਃ਼ੱੑੵ'
SPAN_MAX = 4
FUZZY_MIN = 0.92
COST = {'exact': 0.0, 'skeleton': 0.2, 'fuzzy': 0.6, 'span': 0.1}   # 1:1 wins over a span on a tie
SKIP = 1.0


def norm(s):
    """Unchanged from load_translations v1: punctuation, digits, trailing refrain label."""
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'[॥।|੦-੯\s]+', ' ', s).strip()
    s = re.sub(r'( ਰਹਾਉ( ਦੂਜਾ)?)+$', '', s)
    return s


def norm_span(s):
    """For span comparison only: refrain labels removed wherever they fall."""
    return ' '.join(re.sub(r'(^| )ਰਹਾਉ( ਦੂਜਾ)?(?= |$)', ' ', norm(s)).split())


def skel(s):
    return re.sub('[' + MATRAS + ' ]', '', norm(s))


class Line:
    __slots__ = ('id', 'ang', 'comp', 'header', 'n', 'ns', 'sk')

    def __init__(self, lid, ang, comp, header, text):
        self.id, self.ang, self.comp, self.header = lid, ang, comp, bool(header)
        self.n, self.ns, self.sk = norm(text), norm_span(text), skel(text)


class Rec:
    __slots__ = ('k', 'ang', 'g', 'en', 'n', 'ns', 'sk')

    def __init__(self, k, ang, g, en):
        self.k, self.ang, self.g, self.en = k, ang, g, en
        self.n, self.ns, self.sk = norm(g), norm_span(g), skel(g)


def _one(r, l):
    if abs(r.ang - l.ang) > 1:
        return None
    if r.n == l.n and r.n:
        return 'exact'
    if r.sk and r.sk == l.sk:
        return 'skeleton'
    if r.n and l.n and difflib.SequenceMatcher(None, r.n, l.n).ratio() >= FUZZY_MIN:
        return 'fuzzy'
    return None


def _span(r, lines, j, k):
    """Record r == lines[j:j+k] joined, all one composition, no headings."""
    run = lines[j:j + k]
    if len(run) < k or any(x.header for x in run) or len({x.comp for x in run}) != 1:
        return False
    if abs(r.ang - run[0].ang) > 1 and abs(r.ang - run[-1].ang) > 1:
        return False
    return bool(r.ns) and ' '.join(x.ns for x in run) == r.ns


def _dp(recs, lines, late):
    """Min-cost monotonic alignment of recs to lines. Returns [(rec, [line,...], quality)]."""
    R, L = len(recs), len(lines)
    INF = float('inf')
    cost = [[INF] * (L + 1) for _ in range(R + 1)]
    back = [[None] * (L + 1) for _ in range(R + 1)]
    cost[0][0] = 0.0
    better = (lambda a, b: a <= b) if late else (lambda a, b: a < b)
    one_cache = {}
    for i in range(R + 1):
        for j in range(L + 1):
            c = cost[i][j]
            if c == INF:
                continue
            steps = []
            if i < R: steps.append((i + 1, j, SKIP, None))
            if j < L: steps.append((i, j + 1, SKIP, None))
            if i < R and j < L:
                q = one_cache.get((i, j))
                if q is None:
                    q = one_cache[(i, j)] = _one(recs[i], lines[j]) or ''
                if q: steps.append((i + 1, j + 1, COST[q], (q, 1)))
                for k in range(2, SPAN_MAX + 1):
                    if j + k <= L and _span(recs[i], lines, j, k):
                        steps.append((i + 1, j + k, COST['span'], ('span', k)))
            for ni, nj, sc, m in steps:
                if better(c + sc, cost[ni][nj]):
                    cost[ni][nj] = c + sc
                    back[ni][nj] = (i, j, m)
    out, i, j = [], R, L
    while (i, j) != (0, 0):
        pi, pj, m = back[i][j]
        if m:
            out.append((recs[pi], lines[pj:j], m[0]))
        i, j = pi, pj
    out.reverse()
    return out


def _lis(pairs):
    """Longest chain increasing in both coordinates; pairs sorted by first coordinate."""
    tails, tails_i, prev = [], [], [None] * len(pairs)
    for idx, (_, b) in enumerate(pairs):
        p = bisect.bisect_left(tails, b)
        if p == len(tails): tails.append(b); tails_i.append(idx)
        else: tails[p] = b; tails_i[p] = idx
        prev[idx] = tails_i[p - 1] if p else None
    out, idx = [], tails_i[-1] if tails_i else None
    while idx is not None:
        out.append(pairs[idx]); idx = prev[idx]
    return out[::-1]


def align(recs, lines, gap_limit=250000):
    """Returns (placements, ambiguous_recs). placements: [(rec, [line,...], quality)]."""
    from collections import Counter
    rc = Counter(r.n for r in recs)
    lc = Counter(l.n for l in lines)
    lpos = {l.n: j for j, l in enumerate(lines) if lc[l.n] == 1}
    pairs = [(i, lpos[r.n]) for i, r in enumerate(recs)
             if r.n and rc[r.n] == 1 and r.n in lpos and abs(lines[lpos[r.n]].ang - r.ang) <= 1]
    anchors = _lis(pairs)
    placed, ambiguous = [], []
    bounds = [(-1, -1)] + anchors + [(len(recs), len(lines))]
    for (i0, j0), (i1, j1) in zip(bounds, bounds[1:]):
        if i1 < len(recs):
            placed.append((recs[i1], [lines[j1]], 'exact'))
        gr = recs[i0 + 1:i1]
        if not gr:
            continue
        lo, hi = min(r.ang for r in gr) - 1, max(r.ang for r in gr) + 1
        gl = [l for l in lines[j0 + 1:j1] if lo <= l.ang <= hi]
        if not gl:
            ambiguous += [(r, 'no-candidate') for r in gr]
            continue
        if len(gr) * len(gl) > gap_limit:
            raise RuntimeError(f'alignment gap too large: {len(gr)} records x {len(gl)} lines near Ang {lo + 1}')
        a, b = _dp(gr, gl, False), _dp(gr, gl, True)
        key = lambda t: (t[0].k, tuple(x.id for x in t[1]), t[2])
        sa, sb = {key(t): t for t in a}, {key(t) for t in b}
        took = set()
        for kk, t in sa.items():
            if kk in sb:
                placed.append(t); took.add(t[0].k)
        for t in a + b:
            if t[0].k not in took:
                took.add(t[0].k); ambiguous.append((t[0], 'tie'))
    placed.sort(key=lambda t: t[1][0].id)
    return placed, ambiguous
