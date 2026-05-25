---
type: concept
title: "NMS (Non-Maximum Suppression)"
tags: [concept, postprocess, detection]
related:
  - "[[concepts/WBF]]"
  - "[[concepts/mAP]]"
  - "[[concepts/Bounding Box]]"
  - "[[architecture/실행 파이프라인]]"
---

# NMS — Non-Maximum Suppression

객체 탐지 후처리 단계. 같은 객체에 대해 여러 박스가 예측될 때 하나만 남기는 방법.

## 동작 방식

```
1. confidence score 높은 순으로 박스 정렬
2. 가장 높은 박스를 선택 (keep)
3. 나머지 박스 중 IoU ≥ threshold인 것 제거
4. 남은 박스 중 다음으로 높은 것 선택
5. 반복
```

## 파라미터

| 파라미터 | 역할 | 이 프로젝트 기본값 |
|---|---|---|
| `conf_threshold` | 이 점수 미만 박스 먼저 제거 | 0.5 |
| `iou_threshold` | 겹침이 이 이상이면 같은 객체로 판단 | 0.7 |
| `max_detections` | 최대 탐지 수 | 4 (알약 최대 4개) |

## NMS의 단점

여러 모델 앙상블 시 NMS는 점수 높은 박스 하나만 살리고 나머지를 버린다. 박스 위치 정보 손실.
→ 앙상블에는 [[concepts/WBF]]가 더 적합.

## Ultralytics에서의 NMS

`model.predict(conf=0.5, iou=0.7, max_det=4)` 형태로 내부 처리됨.
v0.1에서는 `src/engine/postprocess.py`에서 직접 구현했으나, v0.2 Ultralytics 전환 후 내장 NMS 사용.
