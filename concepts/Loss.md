---
type: concept
title: "Loss (손실 함수)"
tags: [concept, training, loss]
related:
  - "[[concepts/YOLOv8]]"
  - "[[concepts/Transfer Learning]]"
---

# Loss — YOLOv8 학습 손실

`train.py`가 매 에폭 출력하는 loss 3종.

```
loss: 9.18  box: 1.94  cls: 4.73  dfl: 2.51
```

## box_loss

예측 박스 위치(cx, cy, w, h)와 정답의 차이.
- backbone/neck이 frozen이면 줄어들지 않음 (가중치가 안 바뀌니까)
- Phase 2(head 전체 학습)부터 줄어들기 시작해야 정상

## cls_loss

클래스 분류 정확도. 예측한 클래스와 정답 클래스의 차이.
- Phase 1(cv3 마지막 학습)부터 빠르게 감소
- total loss의 대부분을 차지함 (특히 학습 초반)
- cls_loss만 줄고 box_loss가 안 줄면 → 위치는 못 찾고 클래스만 배우는 중

## dfl_loss (Distribution Focal Loss)

박스 좌표를 분포로 예측할 때의 불확실성 손실.
- box_loss와 비슷하게 움직임
- 보통 2~3 수준에서 서서히 감소

## 학습 상태 진단

| 상황 | 의미 |
|---|---|
| cls_loss만 빠르게 감소 | Phase 1 정상 동작 |
| box_loss가 2.0 수준에서 안 변함 | backbone/neck frozen (Phase 1~2 cv3_last 모드) |
| box_loss도 감소 시작 | Phase 2(head 전체) 정상 동작 |
| loss가 NaN/inf | gradient 폭발 → [[concepts/학습 안정화 기법]] Gradient Clipping 필요 |

## 관련 개념

- [[concepts/YOLOv8]] — 사용 모델
- [[concepts/Transfer Learning]] — Phase별 freeze와 loss 변화
- [[concepts/학습 안정화 기법]] — loss 안정화 기법
