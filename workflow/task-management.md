---
type: concept
title: "태스크 관리 — GitHub Issues & Projects"
created: 2026-05-19
updated: 2026-05-19
tags:
  - workflow
  - github
  - project-management
status: mature
related:
  - "[[index]]"
  - "[[workflow/roles]]"
  - "[[workflow/git-strategy]]"
---

# 태스크 관리 — GitHub Issues & Projects

## 기본 설정

- **GitHub Issues** 사용 (Linear 사용 안 함)
- **이슈 번호**: GitHub 자동 부여 번호 사용 (#4, #5, ...)
- **Milestone 2개**:
  - `v0.1 — 파이프라인 완성` (1차 목표)
  - `v0.2 — 성능 개선` (2차 목표)
- **GitHub Projects 권한**: 팀장 Admin / 팀원 Read

---

## Status 흐름

```
Backlog → Todo → In Progress → In Review → Done
                                    ↓
                                 Blocked
```

- **Backlog**: 전체 할 일 목록
- **Todo**: 이번 주 할 일 (당겨온 것)
- **In Progress**: 지금 작업 중
- **In Review**: PR 올림, 리뷰 대기 중 (자동화로 이동)
- **Blocked**: 다른 이슈에 의존해서 못 시작 (이유 코멘트 필수)
- **Done**: PR 머지 완료 (자동화로 이동)

---

## GitHub Projects 자동화 설정

> Settings → Projects → 해당 프로젝트 → Workflows

| 트리거 | 동작 |
|---|---|
| Pull request opened | 연결된 이슈 → **In Review** |
| Pull request merged | 연결된 이슈 → **Done** |
| Issue closed | 이슈 → **Done** |

**연결 방법**: PR 본문에 `closes #8` 또는 `fixes #8` 명시 → 자동으로 이슈와 연결됨

---

## Label 목록

| Label | 용도 |
|---|---|
| `setup` | 환경, 폴더, Git 세팅 |
| `data` | 원본 데이터 확인, EDA |
| `dataset` | Dataset 클래스, DataLoader |
| `model` | 모델 설계, build_model |
| `train` | 학습 루프, checkpoint |
| `inference` | predict, 결과 확인 |
| `submission` | submission.csv 생성, Kaggle 제출 |
| `experiment` | 하이퍼파라미터 튜닝, 성능 비교 |
| `docs` | 보고서, README, 협업일지 |
| `bug` | 버그 수정 |
| `priority:high` | 마감 직전 긴급 또는 블로킹 이슈 |

---

## 스토리포인트

| 포인트 | 기준 |
|---|---|
| 1 | 30분~1시간 |
| 2 | 반나절 |
| 3 | 하루 안에 가능 |
| 5 | 하루 이상 → 쪼갤 것 |
| 8 | 무조건 쪼갬 |

이슈 제목 앞에 `[3] Dataset 클래스 구현` 형식으로 표기. (GitHub 이슈 번호와 별개)

---

## 이슈 전체 목록 (v0.1)

```dataview
TABLE issue as "#", title as "작업", st as "상태", label as "라벨", assignee as "담당", priority as "우선순위", target as "마감", milestone as "마일스톤"
FROM "tasks"
SORT target ASC, priority ASC, issue ASC
```

---

## 일일 운영 루틴

```
아침:  오늘 할 이슈 In Progress로 이동
작업:  PR 올리면 이슈 자동으로 In Review 이동
머지:  이슈 자동으로 Done 이동
```

우선순위 순서: data → dataset → model → train → predict → submission

---

## Connections

- [[workflow/roles]] — 담당자 매핑
- [[workflow/git-strategy]] — branch 이름 규칙 (PILL-번호 연동)
