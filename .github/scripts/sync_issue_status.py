#!/usr/bin/env python3
"""GitHub Projects v2 이슈 상태 → tasks/issue-*.md st 필드 동기화
- Projects Status → st 필드 업데이트
- GitHub issue CLOSED → st: done
- milestone 필드 동기화
- tasks/에 없는 이슈는 파일 자동 생성
"""
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


def get_all_issues():
    """모든 이슈의 번호, 상태(open/closed), 제목, assignees, labels, milestone 반환"""
    out = gh("issue", "list",
             "--repo", f"{OWNER}/Code_IT_Team_1_FirstProject",
             "--state", "all",
             "--json", "number,state,title,assignees,labels,milestone",
             "--limit", "200")
    if not out:
        return {}
    issues = {}
    for issue in json.loads(out):
        num = issue["number"]
        assignees = ",".join(a["login"] for a in issue.get("assignees", []))
        labels = ",".join(l["name"] for l in issue.get("labels", []))
        milestone = issue.get("milestone") or {}
        milestone_title = milestone.get("title", "")
        # v0.1 — 파이프라인 완성 → v0.1
        milestone_short = milestone_title.split(" ")[0] if milestone_title else ""
        issues[num] = {
            "state": issue["state"],
            "title": issue["title"],
            "assignee": assignees,
            "label": labels,
            "milestone": milestone_short,
        }
    return issues


def get_project_statuses(project_num):
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


def create_task_file(issue_num, issue_info, st):
    path = TASKS_DIR / f"issue-{issue_num}.md"
    milestone = issue_info.get("milestone", "")
    content = f"""---
issue: {issue_num}
title: "{issue_info['title']}"
assignee: {issue_info['assignee']}
label: {issue_info['label']}
st: {st}
milestone: {milestone}
target: ""
github: https://github.com/{OWNER}/Code_IT_Team_1_FirstProject/issues/{issue_num}
---
"""
    path.write_text(content, encoding="utf-8")
    print(f"  created: issue-{issue_num}.md")


def update_files(issues, project_statuses):
    existing = {
        int(re.search(r'issue-(\d+)', f.stem).group(1)): f
        for f in TASKS_DIR.glob("issue-*.md")
    }

    changed = 0

    # 새 이슈 파일 생성
    for num, info in issues.items():
        if num not in existing:
            st = "done" if info["state"] == "CLOSED" else project_statuses.get(num, "todo")
            create_task_file(num, info, st)
            changed += 1

    # 기존 파일 업데이트
    for md_file in sorted(TASKS_DIR.glob("issue-*.md")):
        content = md_file.read_text(encoding="utf-8")
        m = re.search(r'^issue:\s*(\d+)', content, re.MULTILINE)
        if not m:
            continue
        num = int(m.group(1))
        info = issues.get(num, {})

        # st 결정: CLOSED면 done, 아니면 Projects Status
        if info.get("state") == "CLOSED":
            new_st = "done"
        else:
            new_st = project_statuses.get(num)
        if not new_st:
            continue

        # milestone
        new_milestone = info.get("milestone", "")

        new_content = content
        st_m = re.search(r'^st:\s*(.+)$', content, re.MULTILINE)
        current_st = st_m.group(1).strip() if st_m else None
        if new_st != current_st:
            new_content = re.sub(r'^st:\s*.+$', f'st: {new_st}', new_content, flags=re.MULTILINE)
            print(f"  issue-{num}: st {current_st} → {new_st}")
            changed += 1

        mil_m = re.search(r'^milestone:\s*(.*)$', new_content, re.MULTILINE)
        current_mil = mil_m.group(1).strip() if mil_m else None
        if new_milestone and new_milestone != current_mil:
            if mil_m:
                new_content = re.sub(r'^milestone:\s*.*$', f'milestone: {new_milestone}', new_content, flags=re.MULTILINE)
            else:
                new_content = re.sub(r'^(st:\s*.+)$', rf'\1\nmilestone: {new_milestone}', new_content, flags=re.MULTILINE)
            if new_content != content:
                print(f"  issue-{num}: milestone → {new_milestone}")
            changed += 1

        if new_content != content:
            md_file.write_text(new_content, encoding="utf-8")

    print(f"{changed}개 변경")


if __name__ == "__main__":
    proj_num = get_project_number()
    if not proj_num:
        sys.exit(1)
    print(f"Project #{proj_num}")

    issues = get_all_issues()
    print(f"{len(issues)}개 이슈 로드")

    project_statuses = get_project_statuses(proj_num)
    print(f"{len(project_statuses)}개 Projects 상태 읽음")

    update_files(issues, project_statuses)
