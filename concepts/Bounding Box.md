---
type: concept
title: "Bounding Box (바운딩 박스)"
tags: [concept, detection, data]
related:
  - "[[concepts/YOLOv8]]"
  - "[[concepts/mAP]]"
  - "[[concepts/NMS]]"
  - "[[architecture/인터페이스 계약서]]"
---

# Bounding Box — 바운딩 박스

객체의 위치를 나타내는 직사각형 영역. 형식이 여러 가지라 변환에 주의가 필요.

## 형식 종류

| 형식 | 구성요소 | 사용처 |
|---|---|---|
| `xyxy` | x1, y1, x2, y2 (절대 픽셀) | 내부 학습/예측 표준 |
| `xywh` | x, y, w, h (절대 픽셀) | COCO 어노테이션, Kaggle 제출 |
| `cxcywh` | cx, cy, w, h (정규화 0~1) | YOLO txt 라벨 형식 |

## 이 프로젝트 변환 흐름

```
COCO JSON 어노테이션 (xywh 절대)
        ↓ xywh_to_xyxy()
내부 학습/예측 (xyxy 절대)
        ↓ xyxy_to_xywh()
Kaggle 제출 CSV (xywh 절대)

COCO JSON (xywh 절대)
        ↓ YOLO 변환 스크립트 (#52)
YOLO txt 라벨 (cxcywh 정규화)
```

변환 함수 위치: `src/utils/bbox.py`

## 정규화 (normalize)

YOLO 포맷은 이미지 크기로 나눈 0~1 값 사용:
```
cx_norm = (x + w/2) / image_width
cy_norm = (y + h/2) / image_height
w_norm  = w / image_width
h_norm  = h / image_height
```

## bbox 오기입 사례

이 프로젝트 원본 데이터에 `bbox_x=6567` (이미지 width=976 초과) 오기입 존재.
→ `src/data/dataset.py`의 `load_annotations()`에서 이미지 범위 밖 bbox 필터링.

## 인터페이스 계약

팀 전체 표준 → [[architecture/인터페이스 계약서]]
- Dataset 출력: `xyxy` 절대 픽셀
- Kaggle 제출: `xywh` 절대 픽셀
