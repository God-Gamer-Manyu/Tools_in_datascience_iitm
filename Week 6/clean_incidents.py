#!/usr/bin/env python3
"""One-shot cleaner for the incident export.

Usage: run the script from the workspace root (it uses the file paths below).
It will read `q-editor-incident-tags.txt` and write `q-editor-incident-tags.cleaned.txt`.

The script is intentionally small and editable — change `TEAM_EQUIV` or `CANONICAL_PATTERNS` to tweak mappings.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'q-editor-incident-tags.txt'
OUT = ROOT / 'q-editor-incident-tags.cleaned.txt'

# Which canonical team to keep. To include CommerceIT/Commerce Ops, change the set.
TARGET_CANONICAL_TEAM = 'commerce'
INCLUDE_ADJACENT = False  # change to True if you want CommerceIT/Commerce Ops considered Commerce

# Minimal canonicalization patterns (pattern -> canonical tag)
CANONICAL_PATTERNS = [
    (re.compile(r"\b(api|api[-_ ]?err|api[-_ ]?error|api[-_ ]?failure|api[-_ ]?fail)\b", re.I), 'api-error'),
    (re.compile(r"\b(auth|authentication|auth[-_ ]?failure|auth[-_ ]?err|auth[-_ ]?error)\b", re.I), 'auth'),
    (re.compile(r"\b(infra|infrastructure|infra-fault|infra)\b", re.I), 'infrastructure'),
    (re.compile(r"\b(data[-_ ]?quality|data quality|bad data|data-quality)\b", re.I), 'data-quality'),
    (re.compile(r"\b(billing|billing[-_ ]?error|billing[-_ ]?dispute|billing[-_ ]?err)\b", re.I), 'billing'),
    (re.compile(r"\b(time ?out|timeout|timed out|request timeout)\b", re.I), 'timeout'),
    (re.compile(r"\b(latency|slow[-_ ]?response|slow response|response lag)\b", re.I), 'latency'),
    (re.compile(r"\b(integration|intg|integration[-_ ]?failure|integration[-_ ]?issue|partner-integrations)\b", re.I), 'integration'),
    (re.compile(r"\b(deploy|deployment|release|release[-_ ]?task)\b", re.I), 'deployment'),
    (re.compile(r"\b(sign[-_ ]?in|signin)\b", re.I), 'sign-in'),
]

# Helper functions
split_tags_re = re.compile(r"[,|/;•\u2022]|\\|\band\b", re.I)
field_re = re.compile(r"(?P<key>\bteam\b|\bseverity\b|\bstatus\b|\btags\b)\s*=\s*(?P<val>\[[^\]]*\]|[^:]+)", re.I)
id_re = re.compile(r"^(INC-\d+)")
severity_words = re.compile(r"(critical|high|medium|low)", re.I)


def canonicalize_team(raw):
    s = raw.strip()
    # remove punctuation, collapse whitespace, lowercase
    s_norm = re.sub(r"[\W_]+", ' ', s).strip().lower()
    # pick canonical tokens
    if 'commerce' in s_norm:
        return 'commerce'
    if 'commerceit' in s_norm or 'commerce it' in s_norm or 'commerce-it' in s_norm:
        return 'commerceit'
    if 'commerce ops' in s_norm or 'commerceops' in s_norm:
        return 'commerce-ops'
    return s_norm.replace(' ', '-')


def canonicalize_severity(raw):
    m = severity_words.search(raw)
    if not m:
        return 'Low'
    return m.group(1).capitalize()


def extract_tags(raw_tags_text):
    # raw_tags_text may include the brackets or not
    t = raw_tags_text.strip()
    if t.startswith('[') and t.endswith(']'):
        t = t[1:-1]
    # split on many separators
    parts = [p.strip() for p in split_tags_re.split(t) if p and p.strip()]
    cleaned = []
    for p in parts:
        # normalize spaces
        x = re.sub(r"\s+", ' ', p)
        x = x.strip().lower()
        # Replace internal spaces with hyphens
        x = x.replace(' ', '-')
        # Remove characters except alphanum and hyphen
        x = re.sub(r"[^a-z0-9-]", '', x)
        if not x:
            continue
        # map to canonical using patterns
        mapped = None
        for pat, canon in CANONICAL_PATTERNS:
            if pat.search(p):
                mapped = canon
                break
        if not mapped:
            mapped = x
        cleaned.append(mapped)
    # de-duplicate preserving order
    seen = set()
    uniq = []
    for tag in cleaned:
        if tag not in seen:
            seen.add(tag)
            uniq.append(tag)
    return uniq


def parse_line(line):
    if not line.strip():
        return None
    entry = {
        'id': None,
        'team': None,
        'severity': None,
        'status': None,
        'tags_raw': None,
        'owner': None,
        'opened': None,
        'note': None,
        'raw': line.rstrip('\n')
    }
    m = id_re.match(line)
    if m:
        entry['id'] = m.group(1)
    # quick key scans
    for fm in field_re.finditer(line):
        k = fm.group('key').lower()
        v = fm.group('val').strip()
        if k == 'team':
            entry['team'] = v
        elif k == 'severity':
            entry['severity'] = v
        elif k == 'status':
            entry['status'] = v
        elif k == 'tags':
            entry['tags_raw'] = v
    # owner, opened, note simple heuristics
    owner_m = re.search(r'owner\s*=\s*([^:]+)::', line)
    if not owner_m:
        # fallback: owner=... (till :: or whitespace)
        owner_m = re.search(r'owner\s*=\s*([^:]+)\s', line)
    if owner_m:
        entry['owner'] = owner_m.group(1).strip()
    opened_m = re.search(r'opened\s*=\s*([0-9\-:\s]+)', line)
    if opened_m:
        entry['opened'] = opened_m.group(1).strip()
    note_m = re.search(r'note\s*:\s*([^\n]+)', line)
    if note_m:
        entry['note'] = note_m.group(1).strip()
    return entry


def keep_entry(entry, include_adjacent=INCLUDE_ADJACENT):
    # canonicalize team
    if not entry or not entry.get('team'):
        return False
    team_can = canonicalize_team(entry['team'])
    if include_adjacent:
        # accept commerce and commerceit and commerce-ops
        if team_can not in ('commerce', 'commerceit', 'commerce-ops', 'commerce-ops'):
            return False
    else:
        if team_can != TARGET_CANONICAL_TEAM:
            return False
    # status match REOPENED
    status = entry.get('status') or ''
    if 'reopen' not in status.lower():
        return False
    # severity check
    sev = canonicalize_severity(entry.get('severity') or '')
    if sev not in ('Critical', 'High', 'Medium'):
        return False
    return True


def process():
    if not RAW.exists():
        print('Raw file not found at', RAW)
        sys.exit(1)
    cleaned_lines = []
    total_tag_set = set()
    with RAW.open('r', encoding='utf-8') as fh:
        for ln in fh:
            entry = parse_line(ln)
            if not entry:
                continue
            if not keep_entry(entry):
                continue
            team_can = canonicalize_team(entry['team'])
            sev_can = canonicalize_severity(entry.get('severity') or '')
            tags_list = extract_tags(entry.get('tags_raw') or '')
            for t in tags_list:
                total_tag_set.add(t)
            # owner/opened
            owner = (entry.get('owner') or '').strip()
            opened = (entry.get('opened') or '').strip()
            note = (entry.get('note') or '').strip()
            # format output line
            out_tags = ', '.join(tags_list)
            out_line = f"{entry.get('id') or 'UNKNOWN'} :: team={team_can.capitalize()} :: severity={sev_can} :: status=REOPENED :: tags=[{out_tags}] :: owner={owner} :: opened={opened} :: note:{note}"
            cleaned_lines.append(out_line)
    # write output
    with OUT.open('w', encoding='utf-8') as fo:
        for l in cleaned_lines:
            fo.write(l + '\n\n')
        fo.write('# Summary\n')
        fo.write(f'# distinct_canonical_tags_count: {len(total_tag_set)}\n')
        fo.write('# distinct_canonical_tags: ' + ', '.join(sorted(total_tag_set)) + '\n')
    # print short summary
    print(f'Wrote {len(cleaned_lines)} cleaned incidents to {OUT}')
    print(f'distinct canonical tags count: {len(total_tag_set)}')
    print('distinct tags:', ', '.join(sorted(total_tag_set)))


if __name__ == '__main__':
    process()
