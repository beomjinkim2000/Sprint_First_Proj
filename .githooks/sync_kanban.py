#!/usr/bin/env python3
"""Sync Q&A files ↔ Kanban board. Run from repo root.

Usage: sync_kanban.py [kanban_staged=yes|no]
  kanban_staged=yes  → Kanban column wins (user dragged cards)
  kanban_staged=no   → Q&A frontmatter wins (user changed status field)
"""
import os, re, sys, unicodedata

def nfc(s):
    return unicodedata.normalize('NFC', s)

KANBAN    = nfc('Q&A 칸반.md')
QNA_DIR   = nfc('게시판')
QNA_PAT   = re.compile(r'^\[Q&A\].*\.md$')
COLS      = ['미해결', '해결됨']
kanban_staged = (sys.argv[1] == 'yes') if len(sys.argv) > 1 else False


def read_status(path):
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
        m = re.search(r'^상태:\s*(.+)$', text, re.MULTILINE)
        return m.group(1).strip() if m else '미해결'
    except Exception:
        return '미해결'


def set_status(path, status):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    new = re.sub(r'^상태:.*$', f'상태: {status}', text, flags=re.MULTILINE)
    if new == text:
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new)
    return True


def parse_kanban():
    """{stem: column}"""
    if not os.path.exists(KANBAN):
        return {}
    col, result = None, {}
    with open(KANBAN, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            h = re.match(r'^## (.+)$', line)
            if h:
                col = h.group(1).strip()
                continue
            c = re.match(r'^- \[.\] \[\[(.+?)(?:\|.+?)?\]\]', line)
            if c and col:
                result[nfc(c.group(1))] = col
    return result


def stem(fname):
    return nfc(os.path.splitext(fname)[0])

def display_title(s):
    return re.sub(r'^\[Q&A\]-', '', s)

def read_question_excerpt(path, max_len=60):
    """질문 섹션의 첫 번째 내용 줄을 반환 (최대 max_len자)"""
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
        in_q = False
        for line in text.splitlines():
            if 'white-space:nowrap">질문<' in line:
                in_q = True
                continue
            if in_q and 'white-space:nowrap">' in line:
                break
            if in_q:
                # callout 줄이면 내용 추출
                m = re.match(r'^> (.+)$', line)
                clean = m.group(1) if m else line
                # [!note] 헤더 줄은 건너뜀
                if re.match(r'^\[!', clean):
                    continue
                clean = clean.strip().lstrip('>')
                if clean:
                    return clean[:max_len] + ('…' if len(clean) > max_len else '')
    except Exception:
        pass
    return ''

def build_kanban(by_col, excerpts):
    lines = [
        '---', '', 'kanban-plugin: board', '', '---', '',
        '> [!tip] [[게시판|→ Q&A 게시판 바로가기]]',
        '',
    ]
    for col in COLS:
        lines += [f'## {col}', '']
        for s in by_col.get(col, []):
            lines.append(f'- [ ] [[{s}|{display_title(s)}]]')
            exc = excerpts.get(s, '')
            if exc:
                lines.append(f'  {exc}')
        lines.append('')
    lines += [
        '%% kanban:settings',
        '```',
        '{"kanban-plugin":"board","list-collapse":[false,false]}',
        '```',
        '%%',
        '',
    ]
    return '\n'.join(lines)


# --- main ---

if not os.path.isdir(QNA_DIR):
    sys.exit(0)

# Collect all Q&A files
qna = {}
for fname in os.listdir(QNA_DIR):
    if QNA_PAT.match(nfc(fname)):
        s = stem(fname)
        qna[s] = os.path.join(QNA_DIR, fname)

# Parse current Kanban
kanban = parse_kanban()  # {stem: col}

# Build new column mapping
by_col = {c: [] for c in COLS}

excerpts = {}
for s, path in sorted(qna.items()):
    if kanban_staged and s in kanban:
        # Kanban wins — card was dragged
        col = kanban[s] if kanban[s] in COLS else '미해결'
        set_status(path, col)
    else:
        # Q&A frontmatter wins (or file not yet in Kanban)
        col = read_status(path)
        if col not in COLS:
            col = '미해결'
    by_col[col].append(s)
    excerpts[s] = read_question_excerpt(path)

# Rewrite Kanban if changed
new_text = build_kanban(by_col, excerpts)
old_text = open(KANBAN, encoding='utf-8').read() if os.path.exists(KANBAN) else ''
if new_text != old_text:
    with open(KANBAN, 'w', encoding='utf-8') as f:
        f.write(new_text)
