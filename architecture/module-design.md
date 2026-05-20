---
type: concept
title: "모듈 설계"
created: 2026-05-19
updated: 2026-05-19
tags:
  - architecture
  - module
status: mature
related:
  - "[[index]]"
  - "[[architecture/interfaces]]"
  - "[[architecture/folder-structure]]"
  - "[[workflow/roles]]"
---

# 모듈 설계

## 전체 파이프라인

```
Data(raw) → Dataset → Model → Train → Predict → Postprocess → Submission(csv)
    ↓            ↓        ↓       ↓        ↓           ↓              ↓
src/data/   dataset  baseline engine/  engine/    engine/       submission/
            .py      .py     train.py  predict.py postprocess  make_submission.py
                                                  .py
```

---

## 모듈별 책임 & 입출력

### `src/data/dataset.py`
- **책임**: 파일 읽어서 Tensor + target_dict 반환
- **입력**: 이미지 경로 목록, annotation JSON/CSV
- **출력**: `(image_tensor [C,H,W], target_dict)`
- **주의**: bbox를 `xywh → xyxy`로 변환해서 반환 (`src/utils/bbox.py` 사용)

### `src/data/transforms.py`
- **책임**: 이미지와 bbox를 동시에 변환 (augmentation 포함)
- **입력**: PIL Image or Tensor, target_dict
- **출력**: 동일 타입 (bbox도 같이 변환됨)
- **주의**: bbox도 같이 transform 해야 함 — Albumentations 권장

### `src/data/split.py`
- **책임**: train/val image_id 분리
- **입력**: 전체 image_id 리스트, val_ratio
- **출력**: `(train_ids: List[int], val_ids: List[int])`

### `src/models/baseline.py`
- **책임**: 모델 객체 생성 1개 함수
- **입력**: `num_classes: int`
- **출력**: `nn.Module`
- **참고**: `build_model()` 시그니처 고정 → 모델 교체 시 이 함수만 바꾸면 됨

### `src/engine/train.py`
- **책임**: 1 epoch 학습 루프
- **입력**: model, dataloader, optimizer, device
- **출력**: `avg_loss: float`
- **주의**: Dataset 내부를 몰라도 됨 — target_dict 형식만 알면 됨

### `src/engine/evaluate.py`
- **책임**: val 성능 측정
- **입력**: model, dataloader, device
- **출력**: `{"mAP": float, "mAP_50": float, ...}`

### `src/engine/predict.py`
- **책임**: 1 batch 예측 → raw predictions (model forward 단일 책임)
- **입력**: model, batch tensor, device
- **출력**: raw model output (postprocess 전 단계)

### `src/engine/postprocess.py`
- **책임**: NMS / confidence 필터링 / max_detections
- **입력**: raw predictions, iou_threshold, score_threshold, max_detections
- **출력**: `List[pred_dict]` (형식은 [[architecture/interfaces]] 참고)

### `src/submission/make_submission.py`
- **책임**: 예측 결과 → Kaggle 제출 CSV
- **입력**: `List[pred_dict]`
- **출력**: `outputs/submissions/submission_vX.csv`
- **주의**: bbox를 `xyxy → xywh`로 변환 (`src/utils/bbox.py` 사용)

### `src/utils/bbox.py`
- **책임**: bbox 형식 변환 공통 함수
- **함수**: `xyxy_to_xywh()`, `xywh_to_xyxy()`
- **팀장이 직접 구현** — 모든 모듈에서 사용하므로

### `src/utils/seed.py`
- **책임**: 재현성 시드 고정
- **함수**: `set_seed(seed: int)`

### `src/utils/config.py`
- **책임**: config 로드 + null 검증
- **함수**: `load_config(path)` — num_classes, data.names 등 null 검증 포함
- **팀장이 직접 구현** — train.py, predict.py 모두 의존

### `src/utils/collate.py`
- **책임**: DataLoader collate 함수
- **함수**: `collate_fn(batch)` — target_dict 리스트를 배치로 묶음

### `src/utils/validate.py`
- **책임**: 데이터셋/배치 형식 검증
- **함수**: 인터페이스 계약 형식 준수 여부 검사

---

## 응집도 / 결합도 원칙

| 원칙 | 이 프로젝트에서 적용 |
|---|---|
| **응집도 높이기** | 각 `.py` 파일이 하나의 책임만 가짐 |
| **결합도 낮추기** | engine/train.py는 Dataset 내부를 모름. target_dict 형식만 알면 됨 |
| **인터페이스로 연결** | 모듈 간 연결은 [[architecture/interfaces]]의 형식만 따름 |

---

## Connections

- [[architecture/interfaces]] — 고정된 형식 계약
- [[workflow/roles]] — 누가 어떤 모듈 담당
