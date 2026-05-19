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

> GitHub Issues 링크: https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues
> 이슈 시작 시 Project 보드에서 **In Progress**로 이동. 막히면 이슈에 코멘트 + **Blocked** 상태로 변경 (이유 필수).

---

## 황원재 (Data/Dataset) — zipdid

### 지금 바로 시작
1. **[PILL-5](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/8)** — 원본 데이터 구조 확인
   - `data/raw/` 폴더 열어서 파일 구조, annotation 컬럼, bbox 형식, 클래스 수 파악
   - 이슈 코멘트에 결과 남기기 → 팀 전체가 확인함
   - ⚠️ **이게 끝나야 PILL-8 시작 가능**

2. **[PILL-6](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/9)** — EDA 노트북 (`notebooks/01_eda.ipynb`)
   - 클래스 분포, 이미지 크기, bbox 크기 분포 시각화

3. **[PILL-7](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/10)** — bbox 시각화 (`notebooks/02_visualize_bbox.ipynb`)

### PILL-5 완료 후
4. **PILL-8~10** — Dataset 클래스, transforms, split 구현
   - 참고: [[architecture/interfaces]] — Dataset 출력 형식 고정

---

## 유재열 (Model/Train) — YuJY9897

### 데이터 기다리는 동안 지금 시작
1. **[PILL-19](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/22)** — YOLOv8 설치 및 예제 실행
   - `pip install ultralytics` → 예제 실행 → GPU 여부 이슈 코멘트로 남기고 close
   - 30분 안에 끝낼 수 있음

2. **[PILL-20](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/23)** — `build_model()` 스켈레톤 구현
   - `src/models/baseline.py` 생성
   - 아래 코드가 에러 없이 돌면 완료:
     ```python
     model = build_model(num_classes=97)
     dummy = torch.randn(2, 3, 640, 640)
     print(model)
     ```
   - 참고: [[architecture/interfaces]] 섹션 3

### PILL-5 (데이터 구조 파악) 완료 후 순서대로
3. PILL-11 → PILL-12 → PILL-13 → PILL-14
   - 참고: [[architecture/interfaces]], [[architecture/module-design]]

---

## 박창준 (후처리/Inference) — cjkj1234

### 데이터 기다리는 동안 지금 시작
1. **[PILL-21](https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/24)** — `predict.py` 스켈레톤 구현
   - `src/engine/predict.py` 생성
   - 더미 반환값이라도 아래 형식을 맞추면 완료:
     ```python
     {"image_id": int, "boxes": Tensor[N,4], "labels": Tensor[N], "scores": Tensor[N]}
     ```
   - ⚠️ bbox는 반드시 **xyxy 형식** — `src/utils/bbox.py` 변환 함수 사용
   - 참고: [[architecture/interfaces]] 섹션 4

### PILL-8 (Dataset) 완료 후
2. PILL-15 — 실제 모델과 연결해서 predict 완성

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
