#!/usr/bin/env python3
"""
CI 안전망: 로컬 pre-commit hook이 실행되지 않아 wrap이 안 된 Q&A 파일을 자동 처리.
push된 파일에서 답변/댓글 섹션에 [!note]가 아닌 plain/blockquote 텍스트가 있으면 wrap.
"""
import subprocess, os, re, unicodedata, sys, tempfile, shutil

AUTHOR_MAP = {
    "김범진": "김범진(PM)",
    "beomjinkim2000": "김범진(PM)",
    "박창준": "박창준(Exp)",
    "cjkj1234": "박창준(Exp)",
    "유재열": "유재열(Model)",
    "YuY9897": "유재열(Model)",
    "YuJY9897": "유재열(Model)",
    "황원재": "황원재(Data)",
    "zipdid": "황원재(Data)",
}

SECTION_RE = {
    "answer":  re.compile(r'white-space:nowrap">답변<'),
    "comment": re.compile(r'white-space:nowrap">댓글<'),
}

def needs_wrap(path):
    """답변/댓글 섹션에 [!note]가 아닌 텍스트 줄이 있으면 True."""
    in_sec = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            for pat in SECTION_RE.values():
                if pat.search(line):
                    in_sec = True
                    break
            if not in_sec:
                continue
            s = line.strip()
            if s and not s.startswith("> [!") and s != ">" and not s.startswith("<"):
                # [!note] 아닌 내용이 있음
                if not re.match(r'^>\s*\[!', s):
                    return True
    return False

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

# push에서 변경된 Q&A 파일 목록
result = run(["git", "-c", "core.quotepath=false", "diff", "--name-only", "HEAD~1", "HEAD"])
files = []
for line in result.stdout.splitlines():
    path = unicodedata.normalize("NFC", line.strip())
    if re.search(r'게시판/\[Q&A\].*\.md$', path) and os.path.isfile(path):
        files.append(path)

for path in files:
    if not needs_wrap(path):
        continue

    # 파일 마지막 커밋 작성자 → display name 매핑
    r = run(["git", "log", "-1", "--format=%an", "--", path])
    git_author = unicodedata.normalize("NFC", r.stdout.strip())
    author = AUTHOR_MAP.get(git_author, git_author if git_author else "Unknown")

    tmpfile = tempfile.mktemp(suffix=".md")
    r = run(["python3", ".githooks/wrap_callout.py", author, "0", path, tmpfile])
    if r.returncode != 0:
        print(f"wrap 실패: {path}\n{r.stderr}", file=sys.stderr)
        if os.path.exists(tmpfile):
            os.unlink(tmpfile)
        continue

    diff = run(["diff", "-q", path, tmpfile])
    if diff.returncode != 0:
        shutil.copy(tmpfile, path)
        print(f"자동 wrap 완료: {path} (작성자: {author})")
    os.unlink(tmpfile)
