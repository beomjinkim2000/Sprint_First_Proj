---
type: concept
title: "Confidence Score"
tags: [concept, evaluation, prediction]
related:
  - "[[concepts/mAP]]"
  - "[[concepts/NMS]]"
---

# Confidence Score — 신뢰도 점수

모델이 각 예측 박스에 대해 "이 박스 안에 이 클래스의 물체가 있을 확률"을 0~1로 표현한 값.

## 어떻게 계산되나

YOLOv8 eval 모드 출력: `[B, 4 + num_classes, num_anchors]`

```python
class_scores = raw_output[4:, :]          # 56개 클래스 확률 (sigmoid 적용됨)
scores, labels = torch.max(class_scores)  # 56개 중 가장 높은 확률 → score
```

정답(ground truth)과 비교하는 게 아니라 **모델이 자체적으로 출력하는 확신도**.

## mAP와의 관계

- **score** — 박스 1개의 신뢰도 (0~1)
- **mAP** — score를 threshold 0~1로 바꿔가며 precision-recall 곡선을 그리고 그 면적을 계산한 최종 성능 지표

score가 높다고 mAP가 높은 게 아님. score 분포가 적절하게 퍼져있어야 PR 곡선이 잘 나옴.

## conf_threshold

```yaml
postprocess:
  conf_threshold: 0.25   # predict/submission 용 — 이 이하 박스 제거
eval:
  conf_threshold: 0.001  # mAP 계산 전용 — 낮게 설정해야 recall 최대 확보
```

mAP 계산 시 conf_threshold를 낮게 설정하는 이유: PR 곡선 전체를 그려야 면적이 정확하게 나옴. 0.25로 자르면 낮은 score의 박스가 사라져 recall이 낮아 보임.

## submission.csv에서의 score

```
annotation_id, image_id, category_id, bbox_x, bbox_y, bbox_w, bbox_h, score
```

각 행의 score = 해당 박스의 confidence score. 캐글 평가 시 이 값으로 예측의 우선순위를 정함.

## 관련 개념

- [[concepts/mAP]] — score 기반으로 계산되는 성능 지표
- [[concepts/NMS]] — score 기준으로 중복 박스 제거
