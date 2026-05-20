import os, subprocess, json, unicodedata

webhook = os.environ["DISCORD_WEBHOOK"]
before = os.environ.get("BEFORE_SHA", "").strip()

if not before or before == "0" * 40:
    before = "HEAD~1"

result = subprocess.run(
    ["git", "-c", "core.quotepath=false", "log", "--diff-filter=A", "--name-only", "--format=", f"{before}..HEAD"],
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
    body = json.dumps({"content": f"❓ **새 질문이 등록됐어요!** 아는 분 답변 부탁드립니다 🙏\n> **제목:** {title}"})
    subprocess.run(
        ["curl", "-s", "-X", "POST", webhook, "-H", "Content-Type: application/json", "-d", body],
        check=True
    )
    print(f"알림 전송: {title}")
