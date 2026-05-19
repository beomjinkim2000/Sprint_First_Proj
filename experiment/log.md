---
type: log
title: "실험 로그"
created: 2026-05-19
updated: 2026-05-19
tags:
  - experiment
  - log
status: current
related:
  - "[[index]]"
  - "[[Overview]]"
---

# 실험 로그

> 버전별 실험 결과 트래킹. 제출할 때마다 한 줄 추가.
> 형식: 날짜 | 버전 | 변경사항 | mAP | Kaggle Score

---

## 실험 결과 테이블

| 날짜 | 버전 | 모델 | 변경사항 | val mAP@50 | Kaggle Score | 비고 |
|---|---|---|---|---|---|---|
| - | v0.1 | YOLOv8n | 파이프라인 첫 완성 | - | - | 제출 예정 |

---

## v0.1 — 파이프라인 완성

- **목표**: train → predict → submission.csv 까지 동작
- **모델**: YOLOv8n (가장 가벼운 것부터)
- **데이터**: 원본 그대로, 증강 없음
- **결과**: (제출 후 기록)
- **다음 시도**:

---

## v0.2 — 성능 개선 (예정)

- 데이터 증강 추가 (Albumentations)
- 모델 크기 업 (yolov8n → yolov8s → yolov8m)
- 하이퍼파라미터 튜닝
- 추가 데이터 수집 (AI Hub — 금지 데이터셋 제외)

---

## 실험 기록 방법

```bash
# Kaggle 제출 전 태그 남기기
git tag v0.1-submission
git push origin v0.1-submission

# outputs/submissions/ 에 버전 명시해서 저장
submission_v1_yolov8n_baseline.csv
submission_v2_yolov8s_augmented.csv
```

---

## Connections

- [[Overview]] — 프로젝트 전체 목표
- [[architecture/module-design]] — 각 모듈 구조
