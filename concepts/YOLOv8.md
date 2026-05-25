---
type: concept
title: "YOLOv8"
tags: [concept, model, detection]
related:
  - "[[concepts/mAP]]"
  - "[[concepts/Bounding Box]]"
  - "[[concepts/Transfer Learning]]"
  - "[[concepts/NMS]]"
  - "[[architecture/실행 파이프라인]]"
  - "[[workflow/실험 전략]]"
---

# YOLOv8

Ultralytics가 만든 실시간 객체 탐지 모델. YOLO(You Only Look Once) 계열 8번째 버전.

## 모델 크기 종류

| 모델 | 파라미터 | mAP (COCO) | 특징 |
|---|---|---|---|
| yolov8n | 3.2M | 37.3 | nano, 가장 빠름 |
| yolov8s | 11.2M | 44.9 | small |
| yolov8m | 25.9M | 50.2 | medium |
| yolov8l | 43.7M | 52.9 | large |
| yolov8x | 68.2M | 53.9 | extra, 가장 정확 |

이 프로젝트 기준선: `yolov8n` → [[workflow/실험 전략]] #54에서 s/m 비교 예정.

## 구조

```
Backbone (CSPDarknet) → Neck (FPN+PAN) → Head (Detection)
```

- **Backbone**: 이미지에서 특징 추출. COCO pretrained 가중치 사용
- **Neck**: 다양한 크기의 객체 탐지를 위해 멀티스케일 특징 합성
- **Head**: 최종 bbox + class 예측

## Ultralytics 사용법

```python
from ultralytics import YOLO

# 학습
model = YOLO("yolov8n.pt")          # COCO pretrained 로드
model.train(data="configs/pill.yaml", epochs=50, imgsz=640)

# 예측
results = model.predict(source="test_images/", conf=0.5)
```

## 데이터 포맷 요구사항

학습 시 YOLO 포맷 txt 라벨 필요:
```
class_id  cx_norm  cy_norm  w_norm  h_norm
```
자세한 내용 → [[concepts/Bounding Box]]

## 관련 개념

- [[concepts/Transfer Learning]] — pretrained 가중치 활용, freeze 전략
- [[concepts/NMS]] — 중복 박스 제거 (Ultralytics 내장)
- [[concepts/mAP]] — 성능 평가 지표
