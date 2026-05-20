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

| #   | 작업                                      | 상태   | 우선순위 | 마감         | 마일스톤 |
| --- | --------------------------------------- | ---- | ---- | ---------- | ---- |
| 8   | [data] 원본 데이터 구조 확인 및 annotation 컬럼 파악  | todo | p0   | 2026-05-21 | v0.1 |
| 9   | [data] EDA 노트북 작성 (01_eda.ipynb)        | todo | p1   | 2026-05-22 | v0.1 |
| 10  | [data] bbox 시각화 노트북 작성                  | todo | p1   | 2026-05-22 | v0.1 |
| 11  | [dataset] Dataset 클래스 구현 (dataset.py)   | todo | p1   | 2026-05-22 | v0.1 |
| 12  | [dataset] transforms 구현 (transforms.py) | todo | p1   | 2026-05-22 | v0.1 |
| 13  | [dataset] train/val split 구현 (split.py) | todo | p2   | 2026-05-22 | v0.1 |

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

| # | 작업 | 상태 | 우선순위 | 마감 | 마일스톤 |
| --- | --- | --- | --- | --- | --- |
| 22 | [setup] YOLOv8 설치 및 예제 실행 확인 | in-progress | p0 | 2026-05-21 | v0.1 |
| 23 | [model] build_model() 스켈레톤 구현 | todo | p1 | 2026-05-21 | v0.1 |
| 16 | [train] evaluate 구현 (engine/evaluate.py) | todo | p1 | 2026-05-23 | v0.1 |
| 17 | [train] checkpoint 저장/로드 구현 | todo | p1 | 2026-05-23 | v0.1 |
| 14 | [model] baseline 모델 구현 (build_model) | todo | p2 | 2026-05-23 | v0.1 |
| 15 | [train] train loop 구현 (engine/train.py) | todo | p2 | 2026-05-23 | v0.1 |

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

| # | 작업 | 상태 | 우선순위 | 마감 | 마일스톤 |
| --- | --- | --- | --- | --- | --- |
| 24 | [inference] predict.py 스켈레톤 구현 | todo | p1 | 2026-05-21 | v0.1 |
| 18 | [inference] predict 구현 (engine/predict.py) | todo | p2 | 2026-05-23 | v0.1 |

**순서**
1. **[#24](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/24)** — `predict.py` 스켈레톤 (데이터 없이 가능)
   - `src/engine/predict.py` 생성, 더미 반환값으로 형식만 맞추기
   - bbox는 반드시 **xyxy 형식** — `src/utils/bbox.py` 변환 함수 사용
   - 참고: [[architecture/interfaces]] 섹션 4
2. **#11 완료 후** → #18 (실제 모델과 연결해서 predict 완성)

---

## 김범진 (PM) — beomjinkim2000

| # | 작업 | 상태 | 우선순위 | 마감 | 마일스톤 |
| --- | --- | --- | --- | --- | --- |
| 4 | [setup] Github repo 생성 및 branch 전략 설정 | todo | p0 | 2026-05-21 | v0.1 |
| 8 | [data] 원본 데이터 구조 확인 및 annotation 컬럼 파악 | todo | p0 | 2026-05-21 | v0.1 |
| 5 | [setup] 폴더 구조 생성 및 빈 파일 커밋 | todo | p1 | 2026-05-21 | v0.1 |
| 6 | [setup] interfaces.md 작성 | todo | p1 | 2026-05-21 | v0.1 |
| 7 | [setup] pyproject.toml 및 .gitignore 작성 | todo | p1 | 2026-05-21 | v0.1 |
| 9 | [data] EDA 노트북 작성 (01_eda.ipynb) | todo | p1 | 2026-05-22 | v0.1 |
| 10 | [data] bbox 시각화 노트북 작성 | todo | p1 | 2026-05-22 | v0.1 |
| 19 | [submission] make_submission.py 구현 | todo | p1 | 2026-05-24 | v0.1 |
| 20 | [submission] 첫 번째 Kaggle 제출 | todo | p1 | 2026-05-25 | v0.1 |
| 21 | [docs] README 초안 작성 | todo | p1 | 2026-05-25 | v0.1 |

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
