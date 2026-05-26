---
type: concept
title: "LR Scheduling (학습률 스케줄링)"
tags: [concept, training, optimizer]
related:
  - "[[concepts/Transfer Learning]]"
---

# LR Scheduling — 학습률 스케줄링

학습이 진행되면서 lr(learning rate)을 점점 줄이는 전략. 처음엔 빠르게 수렴, 나중엔 세밀하게 조정.

## Cosine Annealing

```
lr
 │▔╲
 │  ╲
 │   ╲___
 └────────→ epoch
  시작lr     lr_min
```

에폭이 진행되면서 코사인 곡선을 따라 `lr_min`까지 감소.

```python
CosineAnnealingLR(optimizer, T_max=phase_epochs, eta_min=lr_min)
```

- `T_max`: 감소 구간 에폭 수
- `eta_min`: 최솟값 (0에 가깝게)

## 이 프로젝트의 Phase별 lr

Phase가 시작될 때마다 lr이 리셋되고 새 코사인 스케줄 시작.

```
Phase 1 (1~10에폭):  0.001 → 0.00001  (cv3 마지막 학습)
Phase 2 (11~30에폭): 0.001 → 0.00001  (head 전체 학습, lr 리셋)
Phase 3 (31~50에폭): 0.001 → 0.00001  (전체 학습, lr 리셋)
                     ↑ head lr
                  backbone = head × backbone_lr_ratio (더 낮음)
```

Phase 3에서 backbone/neck과 head가 서로 다른 lr을 가짐 → [[concepts/Transfer Learning]] 참고.

## lr이 너무 크면

gradient가 폭발 → loss가 NaN/inf → 학습 붕괴.
→ [[concepts/학습 안정화 기법]]의 Gradient Clipping으로 보완.

## 관련 개념

- [[concepts/Transfer Learning]] — Phase별 freeze + lr 전략
- [[concepts/학습 안정화 기법]] — lr과 함께 쓰는 안정화 기법
