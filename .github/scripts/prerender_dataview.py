#!/usr/bin/env python3
"""dataview TABLE 쿼리를 정적 마크다운 표로 변환 (Quartz 빌드 전 실행)"""
import re, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml 없음 — pip install pyyaml", file=sys.stderr)
    sys.exit(1)

TASKS_DIR = Path("tasks")
DATAVIEW_PAT = re.compile(r'```dataview\n(.*?)```', re.DOTALL)
FROM_PAT = re.compile(r'FROM\s+"([^"]+)"', re.IGNORECASE)



def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    try:
        fm = yaml.safe_load(text[3:end])
        return fm or {}, text[end + 3:]
    except Exception:
        return {}, text


def load_tasks():
    rows = []
    for md_file in sorted(TASKS_DIR.glob("issue-*.md")):
        fm, _ = parse_frontmatter(md_file.read_text(encoding="utf-8"))
        fm["_file"] = md_file.stem
        rows.append(fm)
    return rows


def render_table(query, rows):
    # TABLE field as "alias", ... FROM "tasks" SORT x ASC|DESC
    table_m = re.match(r'TABLE\s+(.+?)\s+FROM', query, re.DOTALL | re.IGNORECASE)
    if not table_m:
        return None

    # 컬럼 파싱
    columns = []
    for part in re.split(r',\s*', table_m.group(1).strip()):
        alias_m = re.match(r'(\S+)\s+as\s+"?([^"]+)"?', part.strip(), re.IGNORECASE)
        if alias_m:
            columns.append((alias_m.group(1), alias_m.group(2)))
        else:
            key = part.strip()
            columns.append((key, key))

    # SORT 파싱 (다중 키 지원: SORT a ASC, b ASC, c ASC)
    sort_m = re.search(r'SORT\s+(.+?)(?:\n|$)', query, re.IGNORECASE)
    if sort_m:
        sort_keys = []
        for part in re.split(r',\s*', sort_m.group(1).strip()):
            part = part.strip()
            km = re.match(r'(\w+)(?:\s+(ASC|DESC))?', part, re.IGNORECASE)
            if km:
                sort_keys.append((km.group(1), (km.group(2) or "ASC").upper() == "DESC"))
        for key, desc in reversed(sort_keys):
            rows = sorted(rows,
                          key=lambda r, k=key: (r.get(k) is None or r.get(k) == "", r.get(k, "")),
                          reverse=desc)

    def cell(row, key):
        val = row.get(key, row.get(key.split(".")[-1], ""))
        if isinstance(val, list):
            return ", ".join(str(v) for v in val)
        return str(val) if val is not None else ""

    headers = [alias for _, alias in columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(cell(row, k) for k, _ in columns) + " |")

    return "\n".join(lines)


def process_file(path, rows):
    content = path.read_text(encoding="utf-8")
    if "```dataview" not in content:
        return False

    def replace(m):
        query = m.group(1).strip()
        from_m = FROM_PAT.search(query)
        from_folder = from_m.group(1) if from_m else None

        if from_folder == "tasks":
            rendered = render_table(query, rows)
        else:
            return m.group(0)  # tasks 외 쿼리는 그대로 유지

        return rendered if rendered else ""

    new_content = DATAVIEW_PAT.sub(replace, content)
    if new_content == content:
        return False
    path.write_text(new_content, encoding="utf-8")
    print(f"  rendered: {path}")
    return True


if __name__ == "__main__":
    if not TASKS_DIR.exists():
        print("tasks/ 폴더 없음, 건너뜀")
        sys.exit(0)

    rows = load_tasks()
    print(f"{len(rows)}개 태스크 로드")

    changed = 0
    for md_file in Path(".").rglob("*.md"):
        if any(p.startswith(".") for p in md_file.parts):
            continue
        if process_file(md_file, rows):
            changed += 1

    print(f"{changed}개 파일 pre-render 완료")
