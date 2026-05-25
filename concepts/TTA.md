---
type: concept
title: "TTA (Test-Time Augmentation)"
tags: [concept, inference, augmentation]
related:
  - "[[concepts/Augmentation]]"
  - "[[concepts/앙상블]]"
  - "[[concepts/mAP]]"
  - "[[workflow/실험 전략]]"
  - "[[tasks/issue-58]]"
---

# TTA — Test-Time Augmentation

예측(추론) 단계에서 같은 이미지를 여러 방식으로 변형해 각각 예측한 뒤 결과를 합치는 기법.
재학습 없이 정확도를 높일 수 있음.

## 동작 방식

```
원본 이미지 → 예측 → 박스 A
좌우 반전    → 예측 → 박스 B (다시 반전)
스케일 업    → 예측 → 박스 C (스케일 보정)
       ↓
   결과 합산 (NMS 또는 WBF)
       ↓
   최종 박스
```

## Ultralytics 사용법

```python
results = model.predict(source="test_images/", augment=True)
# augment=True 한 줄로 flip + multi-scale TTA 적용
```

## 장단점

| 장점 | 단점 |
|---|---|
| 재학습 불필요 | 추론 시간 증가 (약 3~5배) |
| mAP 2~5% 향상 기대 | Colab 추론 시간 고려 필요 |

## 관련 개념

- [[concepts/Augmentation]] — 학습 시 augmentation과 유사하나, 추론 시점에 적용
- [[concepts/앙상블]] — TTA도 일종의 앙상블 (같은 모델, 다른 변형)
