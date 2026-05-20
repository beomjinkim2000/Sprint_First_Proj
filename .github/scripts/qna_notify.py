import os, subprocess, json, unicodedata

webhook = os.environ["DISCORD_WEBHOOK"]
before = os.environ.get("BEFORE_SHA", "").strip()

if not before or before == "0" * 40:
    before = "HEAD~1"

result = subprocess.run(
    ["git", "-c", "core.quotepath=false", "log", "--diff-filter=AR", "--name-status", "--format=", f"{before}..HEAD"],
    capture_output=True, text=True
)

seen = set()
paths = []
for line in result.stdout.splitlines():
    line = line.strip()
    if not line:
        continue
    parts = line.split("\t")
    # A: [status, path], R: [status, old_path, new_path]
    path = unicodedata.normalize("NFC", parts[-1])
    if path not in seen:
        seen.add(path)
        paths.append(path)

for path in paths:
    if not path.startswith("게시판/[Q&A]") or not path.endswith(".md"):
        continue
    try:
        content = open(path, encoding="utf-8").read()
    except Exception:
        continue

    # 질문 섹션 추출
    question_lines = []
    in_q = False
    for line in content.splitlines():
        if "nowrap" in line and "질문" in line:
            in_q = True; continue
        if in_q and "nowrap" in line:
            break
        if in_q:
            s = line.strip()
            if s and not s.startswith("> [!") and s != ">":
                question_lines.append(s)

    if not question_lines:
        continue

    title = os.path.basename(path)[len("[Q&A]-"):-len(".md")]
    question_text = "\n".join(question_lines)
    if len(question_text) > 800:
        question_text = question_text[:800] + "…"

    msg = (
        f"❓ **새 질문이 등록됐어요!** 아는 분 답변 부탁드립니다 🙏\n"
        f"**제목:** {title}\n"
        f"─────────────────\n"
        f"{question_text}\n"
        f"─────────────────"
    )
    body = json.dumps({"content": msg})
    subprocess.run(
        ["curl", "-s", "-X", "POST", webhook, "-H", "Content-Type: application/json", "-d", body],
        check=True
    )
    print(f"알림 전송: {title}")
