#!/usr/bin/env python3
"""Discord 답변을 Q&A 파일의 답변 섹션에 추가."""
import os, re, sys, unicodedata

def nfc(s):
    return unicodedata.normalize('NFC', s)

qna_stem    = nfc(os.environ['QNA_STEM'])    # e.g. [Q&A]-파이썬-에러
answer_text = os.environ['ANSWER']
author      = os.environ['AUTHOR']

qna_dir = nfc('게시판')
path    = os.path.join(qna_dir, qna_stem + '.md')

if not os.path.exists(path):
    print(f'파일 없음: {path}', file=sys.stderr)
    sys.exit(1)

with open(path, encoding='utf-8') as f:
    content = f.read()

# 멀티라인 답변 처리: 각 줄 앞에 "> " 추가
lines = answer_text.strip().splitlines()
body  = '\n'.join(f'> {l}' if l.strip() else '>' for l in lines)
callout = f'\n> [!note] {author}\n{body}\n'

# 댓글 섹션 div 바로 앞에 삽입
COMMENT_PAT = re.compile(
    r'(<div[^>]*><hr[^>]*/><span[^>]*>댓글</span><hr[^>]*/></div>)'
)

if COMMENT_PAT.search(content):
    new_content = COMMENT_PAT.sub(callout + r'\1', content, count=1)
else:
    # 댓글 섹션 없으면 파일 끝에 추가
    new_content = content.rstrip() + callout

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'답변 추가 완료: {path}')
