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


def load_folder_files(folder):
    """폴더 내 .md 파일을 file.name / file.mtime 형태로 로드"""
    import datetime
    rows = []
    folder_path = Path(folder)
    if not folder_path.exists():
        return rows
    for md_file in folder_path.rglob("*.md"):
        mtime = md_file.stat().st_mtime
        dt = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        rows.append({"file.name": md_file.stem, "file.mtime": dt, "_mtime_raw": mtime})
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

    # SORT 파싱
    sort_m = re.search(r'SORT\s+(\w+)(?:\s+(ASC|DESC))?', query, re.IGNORECASE)
    if sort_m:
        sort_key = sort_m.group(1)
        sort_desc = (sort_m.group(2) or "ASC").upper() == "DESC"
        rows = sorted(rows,
                      key=lambda r: (r.get(sort_key) is None, r.get(sort_key, "")),
                      reverse=sort_desc)

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
        elif from_folder:
            folder_rows = load_folder_files(from_folder)
            # WHERE file.name != "_index" 처리
            where_m = re.search(r'WHERE\s+file\.name\s*!=\s*"([^"]+)"', query, re.IGNORECASE)
            if where_m:
                exclude = where_m.group(1)
                folder_rows = [r for r in folder_rows if r["file.name"] != exclude]
            # SORT
            sort_m = re.search(r'SORT\s+([\w.]+)(?:\s+(ASC|DESC))?', query, re.IGNORECASE)
            if sort_m:
                sk = sort_m.group(1)
                desc = (sort_m.group(2) or "ASC").upper() == "DESC"
                raw_key = "_mtime_raw" if sk == "file.mtime" else sk
                folder_rows = sorted(folder_rows,
                                     key=lambda r: (r.get(raw_key) is None, r.get(raw_key, "")),
                                     reverse=desc)
            # LIMIT
            limit_m = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
            if limit_m:
                folder_rows = folder_rows[:int(limit_m.group(1))]
            rendered = render_table(query, folder_rows)
        else:
            return ""  # FROM 없는 쿼리는 제거

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
