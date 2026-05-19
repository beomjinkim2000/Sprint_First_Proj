---
type: concept
title: "팀원 역할 분담"
created: 2026-05-19
updated: 2026-05-19
tags:
  - workflow
  - team
status: mature
related:
  - "[[index]]"
  - "[[architecture/module-design]]"
  - "[[workflow/linear-setup]]"
---

# 팀원 역할 분담

## 역할 → 모듈 매핑

| 역할              | 정 (주담당)       | 부 (보조)              | 주담당 모듈                                                                                                                        | Label             |
| --------------- | ------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------- |
| 팀장/PM          | beomjinkim2000 | -                    | `interfaces.md`, `utils/bbox.py`, 루트 `train.py`, `configs/`, PR 리뷰, Kaggle 제출, 전체 관리 및 총괄                                     | setup, submission |
| Data·Dataset 담당 | zipdid        | YuY9897 · cjkj1234   | `data/raw` 확인, annotation 분석, `notebooks/01_eda.ipynb`, `notebooks/02_visualize_bbox.ipynb`, `src/data/dataset.py`, `transforms.py`, `split.py` | data, dataset     |
| Model·Train 담당  | YuY9897       | cjkj1234             | `src/models/baseline.py`, `src/engine/train.py`, `src/engine/evaluate.py`, checkpoint 관리                                      | model, train      |
| 후처리 담당         | cjkj1234      | YuY9897              | `src/engine/predict.py`, `submission/`                                                                                         | inference         |
| 보고서            | 전원            | -                    | `reports/experiment_log.md`, 발표자료/보고서                                                                                         | docs              |

---

## 팀장이 직접 하는 이유

- `interfaces.md`: 팀 전체 계약 → 팀장이 확정해야 권위 생김
- `utils/bbox.py`: 모든 모듈에서 공통으로 쓰는 코드 → 한 명이 책임져야 버그 추적 쉬움
- `submission/make_submission.py`: Kaggle 형식 오류 시 제출 불가 → 팀장이 직접 검증
- PR 리뷰: 팀장이 모든 모듈 코드를 직접 안 짜야 리뷰어 역할 가능

---

## 팀원이 맡는 이유

- 팀장이 모든 코드를 짜면 리뷰가 불가능
- 모듈별 책임을 나누면 인터페이스만 지키면 병렬 개발 가능
- 각자 맡은 모듈에서 주인의식 생김

---

## Connections

- [[workflow/task-management]] — GitHub Issues 이슈/담당자 배정
- [[architecture/module-design]] — 각 모듈 상세 책임
