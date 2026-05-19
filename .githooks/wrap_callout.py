#!/usr/bin/env python3
# Usage: python3 wrap_callout.py AUTHOR SIGN_BODY INPUT_FILE OUTPUT_FILE
import sys, re

author = sys.argv[1]
sign_body = int(sys.argv[2])
in_path = sys.argv[3]
out_path = sys.argv[4]

with open(in_path, 'r', encoding='utf-8') as f:
    text = f.read()

ends_newline = text.endswith('\n')
lines = text.rstrip('\n').split('\n')

SECTION_PAT = {
    'body':    re.compile(r'white-space:nowrap">(?:본문|질문|내용)<'),
    'answer':  re.compile(r'white-space:nowrap">답변<'),
    'comment': re.compile(r'white-space:nowrap">댓글<'),
    'target':  re.compile(r'white-space:nowrap">대상<'),
}

def should_sign(section):
    return (sign_body and section == 'body') or section in ('answer', 'comment')

def flush(buf, output):
    # strip leading/trailing blank lines from buf
    while buf and not buf[0].strip():
        buf.pop(0)
    while buf and not buf[-1].strip():
        buf.pop()
    if not buf:
        return
    output.append(f'> [!note] {author}')
    for ln in buf:
        output.append(f'> {ln}' if ln.strip() else '>')
    output.append('')

section = None
output = []
buf = []

for line in lines:
    new_sec = None
    for sec, pat in SECTION_PAT.items():
        if pat.search(line):
            new_sec = sec
            break

    if new_sec is not None:
        if buf:
            if section and should_sign(section):
                # pull trailing blank lines out — they go after the callout
                trailing = []
                while buf and not buf[-1].strip():
                    trailing.insert(0, buf.pop())
                flush(buf, output)
                # flush always appends one blank line; replace it with the
                # original trailing blanks to avoid double-blank-line
                if trailing:
                    if output and output[-1] == '':
                        output.pop()
                    output.extend(trailing)
            else:
                output.extend(buf)
            buf = []
        section = new_sec
        output.append(line)
        continue

    if section and should_sign(section):
        if line.startswith('>'):
            # already a callout/quote line — flush pending plain text first
            if buf:
                flush(buf, output)
                buf = []
            output.append(line)
        else:
            buf.append(line)
    else:
        if buf:
            output.extend(buf)
            buf = []
        output.append(line)

if buf:
    if section and should_sign(section):
        flush(buf, output)
    else:
        output.extend(buf)

result = '\n'.join(output)
if ends_newline:
    result += '\n'

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(result)
