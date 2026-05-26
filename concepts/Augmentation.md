---
type: concept
title: "Data Augmentation (데이터 증강)"
tags: [concept, data, training]
related:
  - "[[concepts/TTA]]"
  - "[[concepts/Transfer Learning]]"
  - "[[concepts/YOLOv8]]"
  - "[[tasks/issue-53]]"
---

# Data Augmentation — 데이터 증강

학습 이미지를 다양하게 변형해 데이터를 늘리는 기법. 과적합 방지 + 일반화 성능 향상.

## 학습 augmentation vs TTA

| | 학습 augmentation | [[concepts/TTA]] |
|---|---|---|
| 적용 시점 | 학습 시 | 추론(예측) 시 |
| 목적 | 일반화 성능 향상 | 예측 정확도 향상 |
| 모델 재학습 | 필요 | 불필요 |

## Albumentations 주요 변환

이 프로젝트에서 사용 (또는 예정):

```python
import albumentations as A

transform = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.3),
    A.HueSaturationValue(p=0.3),
    A.Rotate(limit=15, p=0.3),
    A.GaussianBlur(p=0.2),
], bbox_params=A.BboxParams(format="pascal_voc", label_fields=["labels"]))
```

## bbox_params 주의사항

Albumentations에서 bbox는 이미지 범위 내에 있어야 함.
이 프로젝트에서 `bbox_x=6567` 오기입 데이터가 있어 사전 필터링 필요.
→ `src/data/dataset.py`의 `load_annotations()`에서 범위 밖 bbox 스킵 처리됨.

## Ultralytics 내장 augmentation

`model.train()` 시 Ultralytics가 자동으로 기본 augmentation 적용.
추가 augmentation은 `augment=True` 파라미터 또는 커스텀 설정으로 조절.

## Mosaic 증강

이미지 4장을 2×2 그리드로 합쳐 하나의 학습 샘플로 만드는 기법. Ultralytics가 기본 적용하는 핵심 증강.

```
[이미지A][이미지B]
[이미지C][이미지D]  →  640×640 1장으로 리사이즈 → 학습
```

**기존 증강과의 차이**
- 기존: 이미지 1장의 모양을 바꿈 (같은 클래스 조합 유지)
- Mosaic: 4장의 다른 이미지를 합침 → 1 스텝당 4배 많은 클래스 정보

**알약 데이터에서 특히 유효한 이유**
이미지 1장에 알약 3~4개 → Mosaic 시 12~16개를 한 스텝에 학습.
56클래스 중 한 스텝에 보는 클래스 수가 늘어 클래스 구분 학습 효율 향상.

**설정 (configs/default.yaml)**
```yaml
augmentation:
  mosaic_p: 0.5             # 0=끄기, 1=항상, 0.5=절반 확률
  mosaic_min_bbox_size: 2   # 리사이즈 후 이 픽셀 이하 박스 제거
```

구현: `src/data/mosaic.py` — MosaicDataset이 train_ds를 래핑.

## 관련 이슈

- #53 [[tasks/issue-53]] — Albumentations 파이프라인 강화 (황원재)
