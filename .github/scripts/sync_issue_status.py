#!/usr/bin/env python3
"""GitHub Projects v2 이슈 상태 → tasks/issue-*.md st 필드 동기화"""
import re, subprocess, json, sys
from pathlib import Path

TASKS_DIR = Path("tasks")
OWNER = "beomjinkim2000"

STATUS_MAP = {
    "Backlog": "backlog",
    "Todo": "todo",
    "In Progress": "in-progress",
    "In Review": "in-review",
    "Blocked": "blocked",
    "Done": "done",
}


def gh(*args):
    r = subprocess.run(["gh"] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        print(f"gh error: {r.stderr.strip()}", file=sys.stderr)
        return None
    return r.stdout


def get_project_number():
    out = gh("project", "list", "--owner", OWNER, "--format", "json", "--limit", "20")
    if not out:
        return None
    data = json.loads(out)
    projects = data.get("projects", [])
    if not projects:
        print("프로젝트 없음", file=sys.stderr)
        return None
    return projects[0]["number"]


def get_issue_statuses(project_num):
    query = """
    query($owner: String!, $num: Int!) {
      user(login: $owner) {
        projectV2(number: $num) {
          items(first: 100) {
            nodes {
              content { ... on Issue { number } }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    out = gh("api", "graphql",
             "-f", f"query={query}",
             "-f", f"owner={OWNER}",
             "-F", f"num={project_num}")
    if not out:
        return {}

    data = json.loads(out)
    statuses = {}
    items = (data.get("data", {})
                 .get("user", {})
                 .get("projectV2", {})
                 .get("items", {})
                 .get("nodes", []))

    for item in items:
        content = item.get("content") or {}
        issue_num = content.get("number")
        if not issue_num:
            continue
        for fv in item.get("fieldValues", {}).get("nodes", []):
            field = fv.get("field") or {}
            if field.get("name") == "Status":
                raw = fv.get("name", "")
                statuses[issue_num] = STATUS_MAP.get(raw, raw.lower().replace(" ", "-"))
                break

    return statuses


def update_files(statuses):
    changed = 0
    for md_file in sorted(TASKS_DIR.glob("issue-*.md")):
        content = md_file.read_text(encoding="utf-8")

        m = re.search(r'^issue:\s*(\d+)', content, re.MULTILINE)
        if not m:
            continue
        issue_num = int(m.group(1))

        new_st = statuses.get(issue_num)
        if not new_st:
            continue

        st_m = re.search(r'^st:\s*(.+)$', content, re.MULTILINE)
        current_st = st_m.group(1).strip() if st_m else None

        if new_st == current_st:
            continue

        new_content = re.sub(r'^st:\s*.+$', f'st: {new_st}', content, flags=re.MULTILINE)
        md_file.write_text(new_content, encoding="utf-8")
        print(f"  issue-{issue_num}: {current_st} → {new_st}")
        changed += 1

    print(f"{changed}개 파일 업데이트")


if __name__ == "__main__":
    proj_num = get_project_number()
    if not proj_num:
        sys.exit(1)
    print(f"Project #{proj_num}")

    statuses = get_issue_statuses(proj_num)
    print(f"{len(statuses)}개 이슈 상태 읽음")

    update_files(statuses)
