#!/usr/bin/env python3
"""
Usage: python3 discord_notify.py question|answer <file_path>
Obsidian 버튼 템플릿에서 호출. commit/push 없이 Discord 알림 전송.
"""
import sys, json, subprocess, re, os, unicodedata

WEBHOOK = "https://discord.com/api/webhooks/1493432111548465244/33ebLhZEHh6FX3PRJBcP8T1MvkuxUoSTJtzruBTpSBeWYc8LCgXfTmHtznAuqmsarrOv"

mode = sys.argv[1]
file_path = unicodedata.normalize("NFC", sys.argv[2])

with open(file_path, encoding="utf-8") as f:
    lines = f.read().splitlines()

basename = os.path.basename(file_path)
title = re.sub(r"^(\[Q&A\]|\[공지\])-?", "", basename)
title = re.sub(r"\.md$", "", title)

SECTION_RE = {
    "question": re.compile(r'white-space:nowrap">질문<'),
    "answer":   re.compile(r'white-space:nowrap">답변<'),
    "comment":  re.compile(r'white-space:nowrap">댓글<'),
}

def parse_sections():
    sections = {k: [] for k in SECTION_RE}
    cur = None
    for line in lines:
        for sec, pat in SECTION_RE.items():
            if pat.search(line):
                cur = sec
                break
        else:
            if cur:
                sections[cur].append(line)
    return sections

def plain_text(sec_lines):
    parts = []
    for line in sec_lines:
        s = line.strip()
        if not s or s.startswith("> [!") or s == ">":
            continue
        clean = s[2:] if s.startswith("> ") else s
        if clean:
            parts.append(clean)
    return " ".join(parts)

def last_callout(sec_lines):
    """[!note] 블록 중 가장 마지막 것의 (author, content) 반환."""
    callouts = []
    cur_author, cur_lines = None, []
    for line in sec_lines:
        m = re.match(r"^>\s*\[!note\]\s*(.+)", line)
        if m:
            if cur_author is not None:
                callouts.append((cur_author, " ".join(cur_lines)))
            cur_author = m.group(1).strip()
            cur_lines = []
        elif cur_author is not None and line.startswith(">"):
            text = line[1:].strip()
            if text:
                cur_lines.append(text)
    if cur_author is not None:
        callouts.append((cur_author, " ".join(cur_lines)))
    return callouts[-1] if callouts else None

sections = parse_sections()

def send(msg):
    body = json.dumps({"content": msg})
    subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-X", "POST", WEBHOOK,
         "-H", "Content-Type: application/json", "-d", body],
        check=True,
    )
    print(f"전송 완료: {title} ({mode})")

if mode == "question":
    text = plain_text(sections["question"])
    preview = text[:300] + ("..." if len(text) > 300 else "")
    msg = f"❓ **새 질문이 등록됐어요!** 아는 분 답변 부탁드립니다 🙏\n> **제목:** {title}"
    if preview:
        msg += f"\n> **질문:** {preview}"
    send(msg)

elif mode == "answer":
    # 답변 → 댓글 순으로 마지막 [!note] 탐색
    result = last_callout(sections["answer"] + sections["comment"])
    if not result:
        print("답변/댓글 [!note] 블록을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)
    author, content = result
    preview = content[:300] + ("..." if len(content) > 300 else "")
    msg = f"💬 **{author}님이 답변을 등록했습니다!**\n> **제목:** {title}"
    if preview:
        msg += f"\n> **내용:** {preview}"
    send(msg)

else:
    print(f"알 수 없는 mode: {mode}", file=sys.stderr)
    sys.exit(1)
