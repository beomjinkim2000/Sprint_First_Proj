---
type: concept
title: "인터페이스 계약서"
created: 2026-05-19
updated: 2026-05-19
tags:
  - architecture
  - interfaces
  - contract
status: mature
related:
  - "[[index]]"
  - "[[architecture/module-design]]"
  - "[[architecture/folder-structure]]"
---

# 인터페이스 계약서

> **이 파일이 바뀌면 팀장 승인 필요.**
> 병렬 개발 중 형식이 달라지면 merge 시 코드가 깨진다.
> 변경이 필요하면 팀장에게 먼저 얘기하고 PR에 반영한다.

---

## 1. Dataset 출력 형식

```python
# src/data/dataset.py
image, target = dataset[idx]

# image: torch.Tensor [C, H, W], float32, 0~1 정규화
# target: dict
target = {
    "boxes":    torch.Tensor,   # shape [N, 4], dtype float32
                                # 형식: [x1, y1, x2, y2] 절대 픽셀 좌표
    "labels":   torch.Tensor,   # shape [N], dtype int64, category_id
    "image_id": int
}
```

---

## 2. bbox 내부 형식 규칙

| 용도 | 형식 | 비고 |
|---|---|---|
| 학습 / 예측 내부 | `[x1, y1, x2, y2]` | 절대 픽셀 좌표 |
| Kaggle 제출 CSV | `[x, y, w, h]` | 좌상단 기준 |
| 변환 함수 위치 | `src/utils/bbox.py` | `xyxy_to_xywh()` / `xywh_to_xyxy()` |

```python
# src/utils/bbox.py
def xyxy_to_xywh(boxes: Tensor) -> Tensor: ...  # 제출용 변환
def xywh_to_xyxy(boxes: Tensor) -> Tensor: ...  # 로딩 시 변환
```

---

## 3. 모델 생성 함수

```python
# src/models/baseline.py
def build_model(num_classes: int) -> torch.nn.Module:
    ...
    return model
```

- `num_classes`: 배경 클래스 포함 여부는 모델별로 다름 → baseline.py 내부 주석으로 명시
- 반환 타입은 반드시 `nn.Module`

---

## 4. predict 결과 형식

```python
# src/engine/predict.py 반환값
List[Dict]  # 이미지 1장당 dict 1개

pred = {
    "image_id":   int,
    "boxes":      torch.Tensor,   # [N, 4], [x1, y1, x2, y2]
    "labels":     torch.Tensor,   # [N], int64
    "scores":     torch.Tensor,   # [N], float32, confidence
}
```

---

## 5. submission.csv 컬럼

```
annotation_id, image_id, category_id, bbox_x, bbox_y, bbox_w, bbox_h, score
```

- `bbox_x, bbox_y, bbox_w, bbox_h`: xywh 형식 (절대 픽셀)
- `score`: 모델 confidence (0~1)
- `annotation_id`: 예측 결과 순번 (1부터 시작, 전체 unique)
- 탐지 결과 없는 이미지도 행 포함 필요 여부 → Kaggle 가이드 확인 후 여기에 업데이트

---

## 6. 변경 이력

| 날짜 | 변경 내용 | 승인자 |
|---|---|---|
| 2026-05-19 | 초안 작성 | 김범진 |

---

## Connections

- [[architecture/module-design]] — 모듈별 입출력 전체 표
- [[architecture/folder-structure]] — 파일 위치
