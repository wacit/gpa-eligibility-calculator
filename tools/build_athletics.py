#!/usr/bin/env python3
"""Rebuild athletics.json NCAA entries from the NCAA Member Directory (2026-27 sponsored sports),
keeping NAIA entries and all curated sections from the existing file.

Usage: build_athletics.py <existing athletics.json> <ncaa_members.json> <ncaa_sports.json> <scorecard.json> <out.json> <report.txt>

Inputs (gather in a browser — these hosts block plain scripted access):
  ncaa_members.json : {"members":[...]} from https://web3.ncaa.org/directory/api/directory/memberList?type=12&division=I|II|III
                      (orgId, nameOfficial, division, subdivision, conferenceName, memberOrgAddress.state, reclass* fields)
  ncaa_sports.json  : {orgId: {"division": "I", "sports": [[label, divisionOfSport], ...]}} parsed from the
                      "Sponsored Sports" table on https://web3.ncaa.org/directory/orgDetail?id=<orgId>
                      (fetch sequentially, ~0.5 s apart; concurrent fetches get a 403 from Akamai)
  scorecard.json    : [[id, name, city, state, alias], ...] from the College Scorecard API (school.operating=1)
NAIA schools and the curated sections (partnerships, abet, naia_conferences, programs_new, sports_new) are
carried over from the existing athletics.json unchanged.
"""
import json, re, sys, unicodedata, collections, datetime

old_path, mem_path, sp_path, sc_path, out_path, rep_path = sys.argv[1:7]
old = json.load(open(old_path))
members = json.load(open(mem_path))['members']
sports = json.load(open(sp_path))
sc = json.load(open(sc_path))  # [id, name, city, state, alias]

SPORTS = old['meta']['sports']  # bit order must be preserved
BIT = {s: i for i, s in enumerate(SPORTS)}

# NCAA directory sport label -> (gender, canonical sport)
def map_sport(label):
    l = label.strip()
    if l in ('Baseball',): return ('m', 'Baseball')
    if l in ('Softball',): return ('w', 'Softball')
    if l == 'Field Hockey': return ('w', 'Field Hockey')
    if l in ('Football', "Men's Lightweight Football"): return ('m', 'Football')
    m = re.match(r"^(Men's|Women's)\s+(.*)$", l)
    if not m: return None
    g = 'm' if m.group(1) == "Men's" else 'w'
    s = m.group(2)
    if s == 'Basketball': return (g, 'Basketball')
    if s == 'Soccer': return (g, 'Soccer')
    if s in ('Volleyball',): return (g, 'Volleyball')
    if s == 'Golf': return (g, 'Golf')
    if s == 'Tennis': return (g, 'Tennis')
    if s in ('Cross Country', 'Track, Indoor', 'Track, Outdoor'): return (g, 'Cross Country / Track')
    if s == 'Swimming and Diving': return (g, 'Swimming & Diving')
    if s == 'Wrestling': return (g, 'Wrestling')
    if s == 'Lacrosse': return (g, 'Lacrosse')
    if s == 'Ice Hockey': return (g, 'Ice Hockey')
    return None

# ---------- name normalisation for NCAA <-> Scorecard matching ----------
def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    s = s.lower()
    s = s.replace('&', ' and ')
    s = re.sub(r"[^a-z0-9 ]", ' ', s)
    s = re.sub(r"\b(the|of|at|in|a|an)\b", ' ', s)
    s = re.sub(r"\s+", ' ', s).strip()
    return s

def variants(name):
    n = norm(name)
    out = {n}
    out.add(re.sub(r"\bst\b", 'saint', n)); out.add(re.sub(r"\bsaint\b", 'st', n))
    out.add(re.sub(r"\bmount\b", 'mt', n)); out.add(re.sub(r"\bmt\b", 'mount', n))
    # "University of X, Y" / "X University-Y" -> handle campus forms
    out.add(n.replace(' main campus', ''))
    # strip "(State)" / "(City)" disambiguators the NCAA appends, e.g. "Regis University (Colorado)"
    base = re.sub(r"\s*\([^)]*\)\s*$", '', name or '')
    if base != name:
        out |= {norm(base)}
    # "U.S." academies
    out.add(norm(re.sub(r"^U\.S\. ", 'United States ', name or '')))
    # "X University-Y" <-> "X University, Y" <-> "X University at Y"
    out.add(re.sub(r"\s+", ' ', norm(name).replace(' campus', '')))
    return {v for v in out if v}

sc_by_norm = collections.defaultdict(list)
sc_by_id = {}
for sid, name, city, state, alias in sc:
    sc_by_id[str(sid)] = (name, city, state, alias)
    for v in variants(name): sc_by_norm[(v, state)].append(str(sid))
    if alias:
        for a in re.split(r"[|,;/]", alias):
            a = a.strip()
            if len(a) >= 4:
                sc_by_norm[(norm(a), state)].append(str(sid))

# reverse map from the OLD file: unitid -> we don't have names, but we can use Scorecard names for old ids
old_ncaa_ids = {k for k, v in old['schools'].items() if v[0] != 'NAIA'}
old_naia = {k: v for k, v in old['schools'].items() if v[0] == 'NAIA'}

def match(m):
    name, state = m['name'].strip(), (m['state'] or '').strip()
    vs = variants(name)
    # 1) name variants that hit an id already classified NCAA in the old file -> trust it
    cands_old = set()
    for v in vs:
        cands_old.update(c for c in sc_by_norm.get((v, state), []) if c in old_ncaa_ids)
    if len(cands_old) == 1: return next(iter(cands_old)), 'old'
    # 2) strict unique match among all Scorecard schools in that state
    cands = set()
    for v in vs: cands.update(sc_by_norm.get((v, state), []))
    if len(cands) == 1: return next(iter(cands)), 'exact'
    if len(cands) > 1:
        # pick the one whose Scorecard name normalises identically to the NCAA name (not just an alias hit)
        exact = [c for c in cands if norm(sc_by_id[c][0]) in vs]
        if len(exact) == 1: return exact[0], 'exact-name'
        return None, f'ambiguous:{[sc_by_id[c][0] for c in cands]}'
    return None, 'none'


# Explicit NCAA orgId -> IPEDS unitid overrides (Scorecard campus naming / renames / system merges).
# Several NCAA orgs may share one unitid (merged IPEDS entity): masks are OR-ed.
OVERRIDES = {
 28:'104151', 31:'106397', 86:'196088', 90:'110422', 156:'126818', 158:'190150', 331:'203517', 99:'110583',
 414:'204024', 418:'170976', 669:'179566', 440:'180461', 474:'159939', 490:'199193', 545:'215293', 587:'186380',
 606:'215770', 756:'236948', 65:'498562', 360:'498562', 384:'498562', 106:'498571', 143:'498571', 209:'498571',
 133:'141486', 9680:'133553', 350:'220604', 2682:'243133', 30127:'800001', 745:'234173', 78:'196121', 85:'196130',
 1305:'215114', 30165:'196015', 124:'131283', 142:'112260', 30083:'196033', 30225:'196024', 242:'196158',
 247:'196167', 282:'191630', 478:'196291', 30067:'196051', 526:'196185', 25719:'214689', 538:'214591',
 30081:'214713', 30044:'214704', 30114:'214801', 30189:'214731', 547:'196246', 9500:'196112', 549:'121345',
 552:'196200', 30029:'196219', 564:'186201', 588:'186371', 589:'186399', 602:'174792', 30072:'195544',
 1340:'195544', 524:'196237', 123:'231165', 30065:'231165', 324:'231165', 803:'240417',
}
# Extra unitids that should mirror another org's entry (combined athletic programs listed once by the NCAA)
MIRROR = {'121345': ['121257']}   # Pomona-Pitzer -> also Pitzer College
EXCLUDE_ORG = {30270}             # "EC University" — NCAA test/placeholder record (no sports, no conference)

# ---------- build ----------
def div_label(m, sp):
    d, sub = m['div'], m['sub']
    if d == 1:
        has_fb = any(s[0] == 'Football' for s in sp)
        fb_sub = next((s[1] for s in sp if s[0] == 'Football'), None)
        if fb_sub == 'FBS' or (not sp and sub == 1): return 'DI-FBS'
        if fb_sub == 'FCS' or (not sp and sub == 2): return 'DI-FCS'
        if has_fb and fb_sub in ('I',): return 'DI-FCS'
        return 'DI-NoFB'
    if d == 2: return 'DII'
    if d == 3: return 'DIII'
    return None

by_org = {}
for m in members:
    by_org.setdefault(m['orgId'], []).append(m)

new_schools = {}
reclass = {}
split_di = {}
report = []
unmatched = []
matched_ids = {}
for org, ms in by_org.items():
    # a reclassifying school appears in both lists; take the entry for its current (lowest-listed) division:
    # directory lists them under current division AND destination; current = the one with reclass fields set and div==original.
    m = ms[0]
    if len(ms) > 1:
        # choose the entry whose div matches the orgDetail page division if available
        sp = sports.get(str(org)) or {}
        want = {'I': 1, 'II': 2, 'III': 3}.get(sp.get('division'))
        m = next((x for x in ms if x['div'] == want), ms[0])
    if org in EXCLUDE_ORG: continue
    if org in OVERRIDES: uid, how = OVERRIDES[org], 'override'
    else: uid, how = match(m)
    if not uid:
        unmatched.append((org, m['name'], m['state'], m['div'], how))
        continue
    merging = uid in matched_ids
    if merging and how != 'override':
        report.append(f"DUP unitid {uid}: {matched_ids[uid]} and {m['name']}")
        continue
    if not merging: matched_ids[uid] = m['name']
    sp = sports.get(str(org), {})
    rows = sp.get('sports', [])
    mm = wm = 0
    sm = sw = 0
    for label, sdiv in rows:
        r = map_sport(label)
        if not r: continue
        g, s = r
        b = 1 << BIT[s]
        if g == 'm': mm |= b
        else: wm |= b
        if m['div'] in (2, 3) and sdiv in ('I', 'FBS', 'FCS'):
            if g == 'm': sm |= b
            else: sw |= b
    label = div_label(m, rows)
    # Reclassifying schools: the directory still lists the ORIGINAL division until the transition
    # completes, but they compete in the destination division now. Keep the site's convention
    # (label = destination, `reclass` records from/to/year) so a DI search still finds e.g. Mercyhurst.
    if m.get('reclassDiv'):
        rd, rs, ry = m['reclassDiv'], m.get('reclassSub'), m.get('reclassYear')
        to = {1: {1: 'DI-FBS', 2: 'DI-FCS', 3: 'DI-NoFB', None: 'DI-NoFB'}.get(rs, 'DI-NoFB'), 2: 'DII', 3: 'DIII'}[rd]
        if to != label:
            reclass[uid] = {'from': label, 'to': to, 'year': ry}
            label = to
    if not rows:
        # no sponsorship table parsed: fall back to old file's masks if present
        o = old['schools'].get(uid)
        if sp.get('division'):
            report.append(f"NOSPORTS {m['name']} ({uid}): directory lists no sponsored sports — masks 0")
        elif o:
            mm, wm = o[1], o[2]
            report.append(f"NOSPORTS {m['name']} ({uid}): page not parsed, kept old masks")
        else:
            report.append(f"NOSPORTS {m['name']} ({uid}): no old data, masks 0")
    if merging:
        o = new_schools[uid]; new_schools[uid] = [o[0], o[1] | mm, o[2] | wm]
        report.append(f"MERGED {m['name']} into {uid}")
    else:
        new_schools[uid] = [label, mm, wm]
    if sm or sw:
        d0 = split_di.get(uid, {'m': 0, 'w': 0}); split_di[uid] = {'m': d0['m'] | sm, 'w': d0['w'] | sw}
for src, dsts in MIRROR.items():
    if src in new_schools:
        for d in dsts: new_schools[d] = list(new_schools[src])
# merge: NCAA from directory, NAIA from old file (unless now NCAA)
schools = dict(new_schools)
for uid, v in old_naia.items():
    if uid not in schools: schools[uid] = v
    else: report.append(f"NAIA->NCAA {sc_by_id.get(uid,('?',))[0]} ({uid}) now {schools[uid][0]}")

# schools in the old file that vanished from the directory
gone = [uid for uid in old_ncaa_ids if uid not in schools]
for uid in gone:
    report.append(f"GONE from NCAA directory: {sc_by_id.get(uid,('?',))[0]} ({uid}) was {old['schools'][uid][0]}")

# diff summary
changes = collections.Counter()
div_changes = []
for uid, v in schools.items():
    o = old['schools'].get(uid)
    if not o: changes['added'] += 1; report.append(f"ADDED {sc_by_id.get(uid,('?',))[0]} ({uid}) {v[0]}"); continue
    if o[0] != v[0]: changes['division'] += 1; div_changes.append(f"DIV {sc_by_id.get(uid,('?',))[0]} ({uid}): {o[0]} -> {v[0]}")
    if o[1] != v[1] or o[2] != v[2]: changes['sports'] += 1
changes['removed'] = len(gone)

out = dict(old)
out['schools'] = dict(sorted(schools.items(), key=lambda kv: int(kv[0])))
out['split_di'] = split_di
out['reclass'] = reclass
meta = dict(old['meta'])
meta['source'] = 'NCAA Member Directory 2026-27 (sponsored sports as listed per institution) + EADA 2024-25 (NAIA + sport fallback)'
meta['sport_sponsorship_source'] = 'NCAA Member Directory 2026-27 sponsored-sports tables for NCAA members; EADA 2024-25 for NAIA'
meta['updated'] = datetime.date.today().isoformat()
out['meta'] = meta
json.dump(out, open(out_path, 'w'), separators=(',', ':'))

with open(rep_path, 'w') as f:
    f.write(f"NCAA orgs: {len(by_org)}  matched: {len(matched_ids)}  unmatched: {len(unmatched)}\n")
    f.write(f"schools total: {len(schools)}  by div: {collections.Counter(v[0] for v in schools.values())}\n")
    f.write(f"changes: {dict(changes)}\nreclass: {len(reclass)}  split_di: {len(split_di)}\n\n")
    f.write("UNMATCHED:\n" + "\n".join(f"  {u}" for u in unmatched) + "\n\n")
    f.write("DIVISION CHANGES:\n" + "\n".join(div_changes) + "\n\n")
    f.write("\n".join(report) + "\n")
print(open(rep_path).read()[:3000])
