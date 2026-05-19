#!/usr/bin/env python3
"""Q&A 파일 커밋 시 칸반 카드 자동 추가 및 내용 갱신. Run from repo root."""
import os, re, unicodedata

def nfc(s):
    return unicodedata.normalize('NFC', s)

KANBAN  = nfc('Q&A 칸반.md')
QNA_DIR = nfc('게시판')
QNA_PAT = re.compile(r'^\[Q&A\].*\.md$')
COLS    = ['미해결', '해결됨']


def read_excerpt(path, section):
    """해당 섹션의 첫 번째 내용 줄 반환 (callout 포함 처리)"""
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
        in_sec = False
        for line in text.splitlines():
            if f'white-space:nowrap">{section}<' in line:
                in_sec = True; continue
            if in_sec and 'white-space:nowrap">' in line:
                break
            if in_sec:
                m = re.match(r'^> (.+)$', line)
                clean = m.group(1) if m else line
                if re.match(r'^\[!', clean): continue
                clean = clean.strip().lstrip('>')
                if clean:
                    return clean[:55] + ('…' if len(clean) > 55 else '')
    except Exception:
        pass
    return ''


def parse_columns():
    """{stem: column} — 현재 칸반에서 읽음"""
    if not os.path.exists(KANBAN):
        return {}
    col, result = None, {}
    with open(KANBAN, encoding='utf-8') as f:
        for line in f:
            h = re.match(r'^## (.+)$', line)
            if h: col = h.group(1).strip(); continue
            m = re.search(r'\[\[(.+?)(?:\|.+?)?\]\]', line)
            if m and col:
                result[nfc(m.group(1))] = col
    return result


def build_kanban(by_col, q_exc, a_exc):
    lines = ['---', '', 'kanban-plugin: board', '', '---', '']
    for col in COLS:
        lines += [f'## {col}', '']
        for s in by_col.get(col, []):
            title = re.sub(r'^\[Q&A\]-', '', s)
            lines.append(f'- [ ] [[{s}|{title}]]')
            q = q_exc.get(s, '')
            a = a_exc.get(s, '')
            if q: lines.append(f'  Q. {q}')
            if a: lines.append(f'  A. {a}')
            lines.append('')
    lines += ['%% kanban:settings', '```',
              '{"kanban-plugin":"board","list-collapse":[false,false]}',
              '```', '%%', '']
    return '\n'.join(lines)


# --- main ---
if not os.path.isdir(QNA_DIR):
    import sys; sys.exit(0)

# 현재 칸반에서 컬럼 위치 읽기
col_map = parse_columns()  # {stem: col}

# Q&A 파일 수집
q_exc, a_exc = {}, {}
by_col = {c: [] for c in COLS}

for fname in sorted(os.listdir(QNA_DIR)):
    if not QNA_PAT.match(nfc(fname)): continue
    s    = nfc(os.path.splitext(fname)[0])
    path = os.path.join(QNA_DIR, fname)
    col  = col_map.get(s, '미해결')
    if col not in COLS: col = '미해결'
    by_col[col].append(s)
    q_exc[s] = read_excerpt(path, '질문')
    a_exc[s] = read_excerpt(path, '답변')

# 칸반 재빌드
new_text = build_kanban(by_col, q_exc, a_exc)
old_text = open(KANBAN, encoding='utf-8').read() if os.path.exists(KANBAN) else ''
if new_text != old_text:
    with open(KANBAN, 'w', encoding='utf-8') as f:
        f.write(new_text)
