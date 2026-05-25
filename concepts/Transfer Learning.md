---
type: concept
title: "Transfer Learning (전이학습)"
tags: [concept, training, model]
related:
  - "[[concepts/YOLOv8]]"
  - "[[concepts/Augmentation]]"
  - "[[workflow/실험 전략]]"
  - "[[tasks/issue-61]]"
---

# Transfer Learning — 전이학습

이미 대규모 데이터로 학습된 모델의 가중치를 가져와 새 태스크에 맞게 재학습하는 방법.

## 왜 필요한가

YOLOv8은 COCO(자연 이미지 80 클래스, 33만 장)로 학습됨.
이 프로젝트의 알약 이미지는 COCO와 도메인이 크게 다름:
- 배경이 단순 (흰 배경 등)
- 객체가 작고 유사한 형태
- 클래스 수 56개, 이미지 수 적음

→ scratch 학습보다 pretrained 가중치 활용이 훨씬 효과적.

## Freeze 전략

학습 시 일부 레이어를 고정(freeze)하면 그 레이어의 가중치는 바뀌지 않음.

| 전략 | freeze 레이어 수 | 설명 |
|---|---|---|
| 전체 fine-tune | 0 | 모든 레이어 학습, 알약 도메인에 완전 적응 |
| 부분 freeze | 10 | backbone 초반 고정, 고수준 특징만 재학습 |
| backbone freeze | 22 | backbone 전체 고정, detection head만 학습 |

```python
# Ultralytics에서 freeze 설정
model.train(data="configs/pill.yaml", freeze=10, ...)
```

## 판단 기준

- freeze 많을수록 → 학습 빠름, 과적합 적음, COCO 특징 보존
- freeze 적을수록 → 알약 도메인에 더 잘 적응, 학습 시간 증가

→ [[workflow/실험 전략]] #61에서 비교 실험 예정.

## 관련 개념

- [[concepts/YOLOv8]] — 사용 모델
- [[concepts/Augmentation]] — freeze와 함께 overfitting 방지에 기여
