#!/usr/bin/env python3
"""dataview TABLE 쿼리를 정적 마크다운 표로 변환 (Quartz 빌드 전 실행)"""
import re, sys, datetime, subprocess
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


def load_folder_files(folder):
    rows = []
    folder_path = Path(folder)
    if not folder_path.exists():
        return rows
    for md_file in folder_path.rglob("*.md"):
        git_out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(md_file)],
            capture_output=True, text=True
        ).stdout.strip()
        mtime_ts = float(git_out) if git_out else md_file.stat().st_mtime
        mtime_str = datetime.datetime.fromtimestamp(mtime_ts).strftime("%Y-%m-%d %H:%M")
        rows.append({
            "file.name": md_file.stem,
            "file.link": f"[[{md_file.stem}]]",
            "file.folder": md_file.parent.name,
            "file.mtime": mtime_str,
            "_mtime_raw": mtime_ts,
        })
    return rows


def load_tasks():
    rows = []
    for md_file in sorted(TASKS_DIR.glob("issue-*.md")):
        fm, _ = parse_frontmatter(md_file.read_text(encoding="utf-8"))
        fm["_file"] = md_file.stem
        rows.append(fm)
    return rows


def render_table(query, rows, auto_file_col=False):
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

    # WHERE 파싱 (contains(field, "val") AND field = "val" 지원)
    where_m = re.search(r'WHERE\s+(.+?)(?:\n|SORT|LIMIT|$)', query, re.IGNORECASE | re.DOTALL)
    if where_m:
        conditions = re.split(r'\bAND\b', where_m.group(1), flags=re.IGNORECASE)
        for cond in conditions:
            cond = cond.strip()
            contains_m = re.match(r'contains\(([\w.]+),\s*"([^"]+)"\)', cond, re.IGNORECASE)
            neq_m = re.match(r'([\w.]+)\s*!=\s*"([^"]+)"', cond)
            eq_m = re.match(r'([\w.]+)\s*=\s*"([^"]+)"', cond)
            if contains_m:
                field, val = contains_m.group(1), contains_m.group(2)
                rows = [r for r in rows if val in str(r.get(field, ""))]
            elif neq_m:
                field, val = neq_m.group(1), neq_m.group(2)
                rows = [r for r in rows if str(r.get(field, "")) != val]
            elif eq_m and "!=" not in cond:
                field, val = eq_m.group(1), eq_m.group(2)
                rows = [r for r in rows if str(r.get(field, "")) == val]

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
            raw_key = "_mtime_raw" if key == "mtime" else key
            rows = sorted(rows,
                          key=lambda r, k=raw_key: (r.get(k) is None or r.get(k) == "", r.get(k, "")),
                          reverse=desc)

    def cell(row, key):
        val = row.get(key, row.get(key.split(".")[-1], ""))
        if isinstance(val, list):
            return ", ".join(str(v) for v in val)
        return str(val) if val is not None else ""

    if auto_file_col:
        columns = [("file.link", "파일")] + columns

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
            rendered = render_table(query, folder_rows, auto_file_col=True)
        else:
            return m.group(0)

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
