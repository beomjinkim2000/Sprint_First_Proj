import os, subprocess, json, urllib.request, unicodedata

webhook = os.environ["DISCORD_WEBHOOK"]

result = subprocess.run(
    ["git", "-c", "core.quotepath=false", "diff", "--name-only", "--diff-filter=A", "HEAD~1", "HEAD"],
    capture_output=True, text=True
)

for path in result.stdout.splitlines():
    path = unicodedata.normalize("NFC", path.strip())
    if not path.startswith("게시판/[Q&A]") or not path.endswith(".md"):
        continue
    try:
        content = open(path, encoding="utf-8").read()
    except Exception:
        continue

    in_q = has_question = False
    for line in content.splitlines():
        if "nowrap" in line and "질문" in line:
            in_q = True; continue
        if in_q and "nowrap" in line:
            break
        s = line.strip()
        if in_q and s and not s.startswith("> [!") and s != ">":
            has_question = True; break

    if not has_question:
        continue

    title = os.path.basename(path)[len("[Q&A]-"):-len(".md")]
    body = json.dumps({"content": f"❓ **새 질문이 등록됐어요!** 아는 분 답변 부탁드립니다 🙏\n> **제목:** {title}"}).encode()
    req = urllib.request.Request(webhook, data=body, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)
    print(f"알림 전송: {title}")
