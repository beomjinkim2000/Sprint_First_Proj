---
type: concept
title: "Annotation 정제 (Annotation Correction)"
tags: [concept, data, annotation, eda]
related:
  - "[[concepts/Bounding Box]]"
  - "[[concepts/YOLOv8]]"
  - "[[architecture/인터페이스 계약서]]"
---

# Annotation 정제 — Annotation Correction

원본 COCO JSON annotation에 오류가 있을 경우 학습 전 정제가 필요하다.  
이 프로젝트는 `configs/bbox_corrections.json`에 오류 목록을 기록하고,  
`dataset.py`의 `load_annotations()`가 로드 시점에 자동 적용한다.

---

## 오류 유형 3가지

### 케이스 1 — bbox 좌표 오기입

annotation JSON에 좌표값이 잘못 입력된 경우.  
이미지 width를 초과하는 x값이 대표 사례.

```
K-003351-016262-018357_...png
  원본: bbox_x = 6567  ← 이미지 width=976 초과 → 명백한 오기입
  보정: bbox_x = 656
```

**발견 방법**: `x + w > img_w` or `y + h > img_h` 조건으로 범위 초과 bbox 탐지.  
`load_annotations()`는 범위 초과 bbox를 기본적으로 스킵하므로, 보정 없이는 해당 class annotation 자체가 사라진다.

---

### 케이스 2 — 중복 bbox

하나의 이미지에서 서로 다른 category_id 2개가 동일한 bbox 좌표를 공유하는 경우.  
한 bbox가 다른 class에 복사·붙여넣기된 것으로 추정.

```
이미지: K-001900-016548-019607-033009_...png
중복 bbox: [88, 255, 366, 209]
  annotation_id=4683 → category_id=A
  annotation_id=4691 → category_id=B  ← 실제로는 다른 위치에 있어야 함
```

**처리 방법**: 중복 bbox를 두 개 모두 제거하고, 모델 추론 예측으로 올바른 bbox를 각 class마다 새로 추가.

---

### 케이스 3 — annotation 누락

이미지에 annotation이 없거나 일부 class annotation만 있는 경우.

**케이스 3a — annotation 전체 없음**  
해당 이미지 파일이 `train_annotations/` JSON에 아예 등록되지 않은 경우.

**케이스 3b — 부분 누락**  
이미지에는 annotation이 존재하지만, 파일명에 명시된 class ID 중 일부가 빠진 경우.

```
파일명: K-003351-013900-021325_...png
기대 class IDs: [3351, 13900, 21325]   ← 파일명에서 파싱
실제 annotated: [13900, 21325]
누락:           [3351]                  ← 케이스 3b
```

---

## 파일명 기반 Class ID 파싱

이 프로젝트 이미지 파일명에는 해당 이미지에 포함된 알약 class ID가 인코딩되어 있다.

```
K-003351-013900-021325_0_2_0_2_70_000_200.png
  └─────────────────┘
  K-{id1}-{id2}-{id3}-...  → class IDs: [3351, 13900, 21325]
```

```python
def parse_category_ids_from_filename(filename):
    stem = Path(filename).stem
    prefix = stem.split("_")[0]        # "K-003351-013900-021325"
    return [int(x) for x in prefix.split("-")[1:]]   # [3351, 13900, 21325]
```

이 파싱 결과와 실제 annotation의 category_id를 비교해 부분 누락을 탐지한다.

---

## bbox_corrections.json 구조

```json
{
  "bbox_x6567_fix": {
    "image_file_name": "K-...png",
    "original_bbox": [6567, 625, 311, 315],
    "corrected_bbox": [656, 625, 311, 315],
    "category_id": 18357
  },

  "duplicate_bbox_fixes": [
    {
      "image_file_name": "K-...png",
      "duplicate_bbox_xywh": [88, 255, 366, 209],
      "duplicate_annotation_ids": [4683, 4691],
      "model_predictions": [
        { "category_id": 19607, "bbox_xywh": [...], "score": 0.988 },
        ...
      ]
    }
  ],

  "missing_annotation_additions": [
    {
      "image_file_name": "K-...png",
      "expected_category_ids": [3351, 13900, 21325],
      "missing_category_ids": [3351],
      "model_predictions": [
        { "category_id": 3351, "bbox_xywh": [...], "score": 0.862 }
      ]
    }
  ]
}
```

- 생성: `notebooks/01_data_EDA.ipynb` 섹션 8~9에서 EDA + 모델 추론 후 저장
- 소비: `src/data/dataset.py`의 `load_annotations(configs/bbox_corrections.json)`

---

## dataset.py 적용 파이프라인

```
load_annotations() 실행 흐름
│
├─ bbox_x6567_fix
│   └─ coord_fixes 테이블 구성 → annotation 로드 시 좌표 치환
│
├─ duplicate_bbox_fixes
│   └─ dup_fix_map 구성
│       → 중복 bbox와 일치하는 항목 제거 (두 annotation 모두)
│       → model_predictions로 대체 추가
│
└─ missing_annotation_additions
    ├─ 케이스 3a (파일 자체 없음)
    │   └─ annotations_by_file에 신규 생성
    └─ 케이스 3b (일부 누락)
        └─ 기존 항목에 model_predictions append
```

`configs/bbox_corrections.json`이 없으면 보정 없이 기존 동작 유지 (graceful fallback).

---

## 모델 추론 신뢰 기준

누락·중복 보정에 사용한 모델 예측은 모두 score ≥ 0.70 이상 선별.  
예외적으로 케이스 3 부분 누락 중 K-003544-004543-012247-016548 의 category_id=4543 예측은 score=0.998로 높은 신뢰도.

---

## 이 프로젝트 보정 결과 요약 (2026-05-28 기준)

| 유형 | 건수 | 파일 |
|---|---|---|
| bbox 오기입 수정 | 1건 | K-003351-016262-018357 |
| 중복 bbox 제거 + 대체 | 3건 | K-001900-..., K-003351-020238-..., K-003351-029667-... |
| annotation 누락 추가 | 8건 | K-003351-013900-021325 외 7건 |
