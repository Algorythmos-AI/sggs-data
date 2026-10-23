# -*- coding: utf-8 -*-
"""Voices-of-the-Granth read models (additive NEW tables; scripture is read, never altered).

    python3 pipeline/build_voices.py --db DB

  author_raag      (author, raag, is_raag, n_lines, n_shabads)   where each voice sings. After
                   Ang 1353 the Granth leaves the raag framework: those rows carry the section
                   name with is_raag = 0, so a client never shows "0 raags" for the Swaiyye.
  author_ang_hist  (author, bucket, n_lines)                      143 buckets of 10 Angs
                   (bucket b covers Angs 10b+1 .. 10b+10) -- the Granth ribbon.
  author_entry     (author, comp_id, ang, line_id)               the first verse line of each
                   voice in Granth order -- "begin with", never a heading.

Every count is over verse lines (is_header = 0), the same population as author_analytics,
and each table is checked against `lines` before commit: a mismatch aborts the build.
"""
import argparse, sqlite3, sys

BUCKET = 10
N_BUCKETS = 143            # 1,430 Angs / 10


def build(con):
    con.executescript("""
      DROP TABLE IF EXISTS author_raag;
      DROP TABLE IF EXISTS author_ang_hist;
      DROP TABLE IF EXISTS author_entry;
      CREATE TABLE author_raag (author TEXT NOT NULL, raag TEXT NOT NULL, is_raag INTEGER NOT NULL,
        n_lines INTEGER NOT NULL, n_shabads INTEGER NOT NULL, PRIMARY KEY (author, raag));
      CREATE TABLE author_ang_hist (author TEXT NOT NULL, bucket INTEGER NOT NULL,
        n_lines INTEGER NOT NULL, PRIMARY KEY (author, bucket));
      CREATE TABLE author_entry (author TEXT PRIMARY KEY, comp_id INTEGER NOT NULL,
        ang INTEGER NOT NULL, line_id INTEGER NOT NULL);
    """)
    con.execute("""
      INSERT INTO author_raag
      SELECT author, COALESCE(raag, section), CASE WHEN raag IS NULL THEN 0 ELSE 1 END,
             count(*), count(DISTINCT comp_id)
      FROM lines WHERE is_header = 0 AND author IS NOT NULL AND COALESCE(raag, section) IS NOT NULL
      GROUP BY author, COALESCE(raag, section)""")
    con.execute(f"""
      INSERT INTO author_ang_hist
      SELECT author, (ang - 1) / {BUCKET}, count(*)
      FROM lines WHERE is_header = 0 AND author IS NOT NULL
      GROUP BY author, (ang - 1) / {BUCKET}""")
    con.execute("""
      INSERT INTO author_entry
      SELECT l.author, l.comp_id, l.ang, l.id FROM lines l
      JOIN (SELECT author, min(id) AS id FROM lines WHERE is_header = 0 AND author IS NOT NULL
            GROUP BY author) f ON f.id = l.id""")


def check(con):
    fails = []
    verse = dict(con.execute("SELECT author, count(*) FROM lines WHERE is_header=0 AND author IS NOT NULL "
                             "GROUP BY author"))
    hist = dict(con.execute("SELECT author, sum(n_lines) FROM author_ang_hist GROUP BY author"))
    if hist != verse: fails.append('author_ang_hist sums != verse lines per author')
    mx = con.execute("SELECT max(bucket), min(bucket) FROM author_ang_hist").fetchone()
    if mx[0] is not None and not (0 <= mx[1] and mx[0] < N_BUCKETS): fails.append(f'bucket range {mx}')
    unplaced = con.execute("SELECT count(*) FROM lines WHERE is_header=0 AND author IS NOT NULL "
                           "AND raag IS NULL AND section IS NULL").fetchone()[0]
    raag = dict(con.execute("SELECT author, sum(n_lines) FROM author_raag GROUP BY author"))
    if sum(raag.values()) + unplaced != sum(verse.values()):
        fails.append(f'author_raag covers {sum(raag.values())} + {unplaced} unplaced != {sum(verse.values())}')
    entries = con.execute("SELECT count(*) FROM author_entry").fetchone()[0]
    if entries != len(verse): fails.append(f'author_entry {entries} rows != {len(verse)} authors')
    bad = con.execute("SELECT count(*) FROM author_entry e JOIN lines l ON l.id=e.line_id "
                      "WHERE l.is_header=1 OR l.author != e.author").fetchone()[0]
    if bad: fails.append(f'{bad} author_entry rows point at a heading or another author')
    return fails


def main():
    a = argparse.ArgumentParser(); a.add_argument('--db', required=True)
    db = a.parse_args().db
    con = sqlite3.connect(db)
    build(con)
    fails = check(con)
    if fails:
        con.rollback(); con.close()
        sys.exit('build_voices: FAIL — ' + '; '.join(fails))
    con.commit()
    n = [con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]
         for t in ('author_raag', 'author_ang_hist', 'author_entry')]
    con.close()
    print(f'voices: author_raag={n[0]} author_ang_hist={n[1]} author_entry={n[2]} (checked against lines)')


if __name__ == '__main__':
    main()
