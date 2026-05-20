---
type: concept
title: "킥오프 가이드 — 역할별 지금 당장 할 일"
created: 2026-05-20
updated: 2026-05-20
tags:
  - workflow
  - onboarding
status: mature
related:
  - "[[workflow/task-management]]"
  - "[[workflow/roles]]"
  - "[[architecture/interfaces]]"
---

# 킥오프 가이드 — 역할별 지금 당장 할 일

> GitHub Issues: https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues
> 이슈 시작 시 Project 보드 → **In Progress** / 막히면 이슈 코멘트 + **Blocked** (이유 필수)

---

## 황원재 (Data/Dataset) — zipdid

```dataview
TABLE issue as "#", title as "작업", milestone as "마일스톤", priority as "우선순위", target as "마감", st as "상태"
FROM "tasks"
WHERE contains(assignee, "zipdid") AND milestone = "v0.1"
SORT target ASC, priority ASC, issue ASC
```

**순서**
1. **[#8](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/8)** — 원본 데이터 구조 확인 ← **여기서 시작**
   - `data/raw/` 파일 구조·annotation 컬럼·bbox 형식·클래스 수 파악
   - 이슈 코멘트에 결과 남기기 → **이게 끝나야 #11 시작 가능**
2. **[#9](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/9)** — EDA 노트북 (`notebooks/01_eda.ipynb`)
3. **[#10](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/10)** — bbox 시각화 (`notebooks/02_visualize_bbox.ipynb`)
4. **#8 완료 후** → #11 → #12 → #13 (Dataset / transforms / split)
   - 참고: [[architecture/interfaces]] — Dataset 출력 형식 고정

---

## 유재열 (Model/Train) — YuJY9897

```dataview
TABLE issue as "#", title as "작업", milestone as "마일스톤", priority as "우선순위", target as "마감", st as "상태"
FROM "tasks"
WHERE contains(assignee, "YuJY9897") AND milestone = "v0.1"
SORT target ASC, priority ASC, issue ASC
```

**순서**
1. **[#22](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/22)** — YOLOv8 설치 및 예제 실행 (30분, 데이터 없이 가능)
   - `pip install ultralytics` → 예제 실행 → GPU 여부 이슈 코멘트 남기고 close
2. **[#23](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/23)** — `build_model()` 스켈레톤 (데이터 없이 가능)
   - `src/models/baseline.py` 생성, 더미 텐서로 forward 통과 확인
   - 참고: [[architecture/interfaces]] 섹션 3
3. **#8 완료 후** → #14 → #15 → #16 → #17 (model → train → evaluate → checkpoint)
   - 참고: [[architecture/interfaces]], [[architecture/module-design]]

---

## 박창준 (Inference) — cjkj1234

```dataview
TABLE issue as "#", title as "작업", milestone as "마일스톤", priority as "우선순위", target as "마감", st as "상태"
FROM "tasks"
WHERE contains(assignee, "cjkj1234") AND milestone = "v0.1"
SORT target ASC, priority ASC, issue ASC
```

**순서**
1. **[#24](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/24)** — `predict.py` 스켈레톤 (데이터 없이 가능)
   - `src/engine/predict.py` 생성, 더미 반환값으로 형식만 맞추기
   - bbox는 반드시 **xyxy 형식** — `src/utils/bbox.py` 변환 함수 사용
   - 참고: [[architecture/interfaces]] 섹션 4
2. **#11 완료 후** → #18 (실제 모델과 연결해서 predict 완성)

---

## 김범진 (PM) — beomjinkim2000

```dataview
TABLE issue as "#", title as "작업", milestone as "마일스톤", priority as "우선순위", target as "마감", st as "상태"
FROM "tasks"
WHERE contains(assignee, "beomjinkim2000") AND milestone = "v0.1"
SORT target ASC, priority ASC, issue ASC
```

---

## 공통 규칙

| 상황 | 행동 |
|------|------|
| 이슈 시작할 때 | Project 보드 → **In Progress** |
| PR 올릴 때 | 본문에 `closes #번호` 명시 |
| 막혔을 때 | 이슈 코멘트에 이유 + Project 보드 → **Blocked** |
| interfaces.md 변경 필요 시 | 팀장에게 카톡 먼저, PR에서 변경 |

---

## Connections

- [[workflow/task-management]] — 전체 이슈 목록 및 Status 흐름
- [[workflow/roles]] — 역할별 담당 모듈 상세
- [[architecture/interfaces]] — 모듈 간 입출력 계약서 (필수 숙지)
