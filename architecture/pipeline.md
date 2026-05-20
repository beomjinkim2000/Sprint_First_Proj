---
type: concept
title: "실행 파이프라인"
created: 2026-05-20
updated: 2026-05-20
tags:
  - architecture
  - pipeline
status: draft
related:
  - "[[architecture/folder-structure]]"
  - "[[architecture/module-design]]"
  - "[[architecture/interfaces]]"
  - "[[workflow/roles]]"
---

# 실행 파이프라인

## 전체 흐름

| Step | 환경 | 진입점 | 주요 출력 |
|---|---|---|---|
| 0 | — | — | 공통 유틸리티 (config, seed, validate, collate, bbox) |
| 1 | Colab CLI | `train.py` | `outputs/checkpoints/best.pt` |
| 2a | Colab CLI | `predict.py` | `reports/experiment_log.md` (mAP) |
| 2b | Colab CLI | `predict.py` | `outputs/submissions/submission_vX.csv`, `outputs/predictions/predictions.json` |
| 3 | Colab 노트북 | `notebooks/02_visualize_bbox.ipynb` | `reports/figures/` |

---

## Step 0 — 공통 유틸리티

모든 Step에서 공통으로 사용하는 유틸리티 모음.

| 파일 | 역할 | 사용 Step | 정 | 부 |
|---|---|---|---|---|
| `src/utils/config.py` | config 로드 + null 검증 | 1, 2 | 김범진(PM) | 유재열(Model) |
| `src/utils/seed.py` | 재현성 시드 고정 | 1 | 김범진(PM) | 유재열(Model) |
| `src/utils/validate.py` | 데이터셋 / 배치 형식 검증 | 1 | 김범진(PM) | 황원재(Data) |
| `src/utils/collate.py` | DataLoader collate 함수 | 1 | 김범진(PM) | 황원재(Data) |
| `src/utils/bbox.py` | xyxy↔xywh 변환 | 1, 2b | 김범진(PM) | 황원재(Data) |

---

## Step 1 — 학습 (Colab CLI)

실행: `python train.py --config configs/default.yaml`

| 파일 | 역할 | 정 | 부 |
|---|---|---|---|
| `train.py` | 진입점. config 로드, seed 고정, 루프 총괄 | 김범진(PM) | 유재열(Model) |
| `configs/default.yaml` | 하이퍼파라미터 / 경로 / 클래스 설정 | 김범진(PM) | 유재열(Model) |
| `data/processed/` | 전처리된 학습 데이터 | 황원재(Data) | — |
| `src/data/dataset.py` | data/processed/ → (image_tensor, target_dict) | 황원재(Data) | 김범진(PM) |
| `src/data/transforms.py` | 이미지 + bbox 동시 augmentation | 황원재(Data) | 김범진(PM) |
| `src/data/split.py` | train/val image_id 분리 | 황원재(Data) | 김범진(PM) |
| `src/models/baseline.py` | build_model(cfg) → nn.Module | 유재열(Model) | 박창준(Exp) |
| `src/engine/train.py` | 1 epoch 학습 루프 → avg_loss | 유재열(Model) | 박창준(Exp) |
| `src/engine/evaluate.py` | val mAP 계산 (학습 중) | 유재열(Model) | 박창준(Exp) |
| `outputs/checkpoints/best.pt` | 최고 val mAP 기준 가중치 저장 | 유재열(Model) | — |

---

## Step 2a — 검증 평가 (Colab CLI)

실행: `python predict.py --config configs/default.yaml --weights outputs/checkpoints/best.pt`

| 파일 | 역할 | 정 | 부 |
|---|---|---|---|
| `predict.py` | 진입점. 가중치 로드, 전체 이미지 순회 | 김범진(PM) | 박창준(Exp) |
| `src/engine/predict.py` | 1 batch 예측 → raw predictions | 박창준(Exp) | 유재열(Model) |
| `src/engine/postprocess.py` | NMS / confidence 필터링 → List[pred_dict] | 박창준(Exp) | 유재열(Model) |
| `src/data/dataset.py` | val → target_dict (정답 레이블) | 황원재(Data) | 김범진(PM) |
| `src/engine/evaluate.py` | pred_dict + target_dict → mAP | 박창준(Exp) | 유재열(Model) |
| `reports/experiment_log.md` | 버전별 실험 결과 기록 | 박창준(Exp) | 김범진(PM) |

---

## Step 2b — Kaggle 제출 (Colab CLI)

make_submission.py 가 pred_dict 를 Kaggle CSV 형식으로 변환.

| 파일 | 역할 | 정 | 부 |
|---|---|---|---|
| `src/submission/make_submission.py` | pred_dict → Kaggle CSV | 김범진(PM) | 박창준(Exp) |
| `outputs/predictions/predictions.json` | 시각화용 예측 결과 저장 | 황원재(Data) | 박창준(Exp) |
| `outputs/submissions/submission_vX.csv` | Kaggle 제출 파일 | 유재열(Model) · 박창준(Exp) | 김범진(PM) |

pred_dict 형식은 architecture/interfaces 참고.

---

## Step 3 — 시각화 (Colab 노트북)

predictions.json 을 로드해 bbox 오버레이 시각화.

| 파일 | 역할 | 정 | 부 |
|---|---|---|---|
| `outputs/predictions/predictions.json` | Step 2b 출력 로드 | — | — |
| `notebooks/02_visualize_bbox.ipynb` | bbox + label + score 시각화 인라인 | 황원재(Data) | 김범진(PM) |
| `reports/figures/` | 시각화 결과 이미지 저장 | 박창준(Exp) | 황원재(Data) |

notebooks/01_data_structure.ipynb (EDA용) 과 별개 파일.

---

## Connections

- [[architecture/folder-structure]] — 파일 경로 기준
- [[architecture/module-design]] — 각 모듈 입출력 상세
- [[architecture/interfaces]] — pred_dict 형식 계약
- [[workflow/roles]] — 전체 역할 분담
