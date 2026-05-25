---
type: concept
title: "WBF (Weighted Box Fusion)"
tags: [concept, ensemble, postprocess]
related:
  - "[[concepts/NMS]]"
  - "[[concepts/앙상블]]"
  - "[[concepts/mAP]]"
  - "[[workflow/실험 전략]]"
  - "[[tasks/issue-59]]"
---

# WBF — Weighted Box Fusion

여러 모델의 예측 박스를 버리지 않고 가중평균으로 합치는 앙상블 후처리 방법.
[[concepts/NMS]]의 업그레이드 버전.

## NMS vs WBF 비교

| | NMS | WBF |
|---|---|---|
| 겹치는 박스 처리 | 점수 낮은 것 제거 | 가중평균으로 합침 |
| 박스 위치 | 가장 높은 점수의 박스 위치 | 여러 박스의 평균 위치 |
| 앙상블 적합성 | 낮음 (정보 손실) | 높음 |

## 동작 방식

```
모델 A 예측: 박스[x1,y1,x2,y2, score=0.9]
모델 B 예측: 박스[x1',y1',x2',y2', score=0.8]

IoU ≥ iou_thr → 같은 객체로 판단
→ 가중평균: 위치 = (0.9*박스A + 0.8*박스B) / (0.9+0.8)
→ 최종 score = (0.9+0.8) / 2
```

## 파이프라인

```python
from ensemble_boxes import weighted_boxes_fusion

boxes_list = [boxes_model_a, boxes_model_b]   # 정규화된 [x1,y1,x2,y2]
scores_list = [scores_a, scores_b]
labels_list = [labels_a, labels_b]
weights = [1, 1]   # 두 모델 동등 비중

boxes, scores, labels = weighted_boxes_fusion(
    boxes_list, scores_list, labels_list,
    weights=weights, iou_thr=0.5, skip_box_thr=0.4
)
```

## 이 프로젝트 적용 계획

- #54 유재열님 모델 실험 완료 후 (yolov8n + yolov8s/m)
- 담당: 박창준 (#59)
- 자세한 내용 → [[workflow/실험 전략]]
