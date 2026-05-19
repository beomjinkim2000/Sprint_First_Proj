#!/usr/bin/env python3
"""새 Q&A 파일을 칸반 보드에 자동 추가. Run from repo root."""
import os, re, unicodedata

def nfc(s):
    return unicodedata.normalize('NFC', s)

KANBAN  = nfc('Q&A 칸반.md')
QNA_DIR = nfc('게시판')
QNA_PAT = re.compile(r'^\[Q&A\].*\.md$')


def existing_cards():
    """칸반에 이미 있는 카드 stem 목록"""
    if not os.path.exists(KANBAN):
        return set()
    result = set()
    with open(KANBAN, encoding='utf-8') as f:
        for line in f:
            m = re.search(r'\[\[(.+?)(?:\|.+?)?\]\]', line)
            if m:
                result.add(nfc(m.group(1)))
    return result


def insert_card(stem):
    """미해결 레인 맨 아래에 카드 추가"""
    title = re.sub(r'^\[Q&A\]-', '', stem)
    card  = f'- [ ] [[{stem}|{title}]]'

    with open(KANBAN, encoding='utf-8') as f:
        lines = f.readlines()

    # 미해결 레인 찾아서 그 다음 빈 줄 이후에 삽입
    insert_at = None
    in_unsolved = False
    for i, line in enumerate(lines):
        if re.match(r'^## 미해결', line):
            in_unsolved = True
            continue
        if in_unsolved and re.match(r'^## ', line):
            insert_at = i
            break

    if insert_at is None:
        # 미해결 레인이 없으면 %% kanban:settings 앞에 추가
        for i, line in enumerate(lines):
            if line.startswith('%% kanban:settings'):
                insert_at = i
                break

    if insert_at is not None:
        lines.insert(insert_at, card + '\n')
        with open(KANBAN, 'w', encoding='utf-8') as f:
            f.writelines(lines)


# --- main ---
if not os.path.isdir(QNA_DIR) or not os.path.exists(KANBAN):
    import sys; sys.exit(0)

cards = existing_cards()

for fname in sorted(os.listdir(QNA_DIR)):
    if not QNA_PAT.match(nfc(fname)):
        continue
    stem = nfc(os.path.splitext(fname)[0])
    if stem not in cards:
        insert_card(stem)
