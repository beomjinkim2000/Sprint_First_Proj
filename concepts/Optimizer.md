---
type: concept
title: "Optimizer (옵티마이저)"
tags: [concept, training, optimizer]
related:
  - "[[concepts/LR Scheduling]]"
  - "[[concepts/Transfer Learning]]"
  - "[[concepts/학습 안정화 기법]]"
---

# Optimizer — 옵티마이저

학습 중 gradient를 이용해 가중치를 업데이트하는 알고리즘.

## SGD (Stochastic Gradient Descent)

```
θ = θ - lr × g_t
```

가장 단순한 형태. **YOLOv8(Ultralytics) 기본 옵티마이저** (momentum=0.937, weight_decay=0.0005).  
충분히 학습하면 Adam 계열보다 최종 mAP가 높은 경우 많음. 단, lr 튜닝에 민감.

## Momentum

관성. 이전에 가던 방향을 기억해서 유지.

```
v_t = β × v_{t-1} + g_t    ← 이전 속도 β(=0.9)만큼 유지 + 현재 gradient
θ   = θ - lr × v_t
```

평탄한 구간도 이전 속도로 통과하고, 노이즈에 덜 흔들림.  
공이 언덕을 굴러내려가는 것과 같음.

## Adam

Momentum(1차 모멘트) + RMSprop(2차 모멘트) 결합.

```
m_t = β1 × m_{t-1} + (1-β1) × g_t      ← 1차 모멘트 (momentum, β1=0.9)
v_t = β2 × v_{t-1} + (1-β2) × g_t²     ← 2차 모멘트 (β2=0.999)

m̂_t = m_t / (1 - β1^t)                  ← bias correction
v̂_t = v_t / (1 - β2^t)

θ = θ - lr × m̂_t / (√v̂_t + ε)
```

- **β1 (momentum)**: gradient 방향의 지수이동평균
- **β2 (2차 모멘트)**: gradient 크기(제곱)의 지수이동평균 — β1과 구조가 동일하지만 g² 추적 (β1의 "cousin")
- 파라미터마다 adaptive lr 자동 조정 → lr 튜닝 쉬움, 수렴 빠름

## AdamW

Adam + **decoupled weight decay**.

```
θ = θ - lr × m̂_t / (√v̂_t + ε) - λ × θ
                                    ↑ weight decay: 매 스텝 가중치를 λ 비율로 0 쪽으로 당김
```

Adam의 weight decay는 gradient에 섞이면 adaptive lr과 상호작용해 효과가 줄어듦.  
AdamW는 weight decay를 gradient 계산과 독립적으로 적용 → 정규화 효과 제대로 발휘.

**이 프로젝트 `train.py`의 기본 옵티마이저.**

## 비교

| | SGD | Adam | AdamW |
|---|---|---|---|
| 수렴 속도 | 느림 | 빠름 | 빠름 |
| 최종 성능 | 높음 (충분히 학습 시) | 보통 | 보통~높음 |
| lr 튜닝 민감도 | 높음 | 낮음 | 낮음 |
| YOLOv8 기본값 | ✓ | | |
| 이 프로젝트 | | | ✓ |

## 관련 개념

- [[concepts/LR Scheduling]] — lr 스케줄러와 함께 사용
- [[concepts/학습 안정화 기법]] — weight decay 외 추가 정규화 기법
- [[concepts/Transfer Learning]] — Phase 3 차등 lr (Discriminative LR)
