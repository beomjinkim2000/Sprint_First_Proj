---
issue: 55
title: "[train] 하이퍼파라미터 튜닝"
assignee:
  - 박창준 (후처리)
label: train
st: todo
milestone: v0.2
priority: p2
target: 2026-05-28
github: https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/55
---

# #55 하이퍼파라미터 튜닝

## 2026-05-28 v2.7.3 checkpoint fine-tuning 실험

### 목적

- 기존 `best_model(V2.7.3).pt` 체크포인트를 기준으로 30 epoch 추가 fine-tuning을 진행했다.
- 큰 구조 변경 없이 learning rate와 weight decay만 조정해서 validation mAP가 개선되는지 확인했다.
- Kaggle 제출은 하지 않고, validation metric과 산출 파일 기준으로 비교했다.

### 기준 체크포인트

| 항목 | 값 |
| --- | --- |
| 기준 모델 | YOLOv8l |
| 체크포인트 | `best_model(V2.7.3).pt` |
| checkpoint epoch | 100 |
| 기준 val mAP | 0.9507185220718384 |
| 사용 state | `ema_state` |

### 실험 조건

| 실험명 | 모델 | epoch | batch | phase1_lr | phase2_lr | phase3_head_lr | phase3_backbone_lr | weight_decay |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ft_lowlr_e30` | YOLOv8l | 30 | 8 | 0.0001 | 0.0001 | 0.00001 | 0.000001 | 0.0005 |
| `ft_verylowlr_e30` | YOLOv8l | 30 | 8 | 0.00005 | 0.00005 | 0.000005 | 0.0000005 | 0.0005 |
| `ft_wd0001_e30` | YOLOv8l | 30 | 8 | 0.0001 | 0.0001 | 0.00001 | 0.000001 | 0.0001 |

### 결과

| 순위 | 실험명 | best raw epoch | best raw mAP | best raw mAP50 | best EMA epoch | best EMA mAP | best EMA mAP50 | 판단 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `ft_wd0001_e30` | 8 | 0.958421 | 0.990983 | 28 | 0.955340 | 0.990983 | 가장 좋음 |
| 2 | `ft_lowlr_e30` | 23 | 0.956633 | 0.990983 | 16 | 0.951947 | 0.990983 | 개선 확인 |
| 3 | `ft_verylowlr_e30` | 24 | 0.955445 | 0.989480 | 19 | 0.953763 | 0.990983 | 안정적이나 raw 기준 낮음 |

### 결론

- 3개 실험 모두 기준 체크포인트의 val mAP `0.950718`보다 개선됐다.
- 가장 좋은 조건은 `ft_wd0001_e30`이다.
- `ft_wd0001_e30`은 기준 대비 raw mAP 기준 약 `+0.0077`, EMA mAP 기준 약 `+0.0046` 상승했다.
- 같은 low lr 조건에서 `weight_decay`를 `0.0005`에서 `0.0001`로 낮춘 것이 가장 좋은 결과를 냈다.
- 다음 공유/후속 실험 기준 파일은 `ft_wd0001_e30/best_model.pt`, `ft_wd0001_e30/submission.csv`, `ft_wd0001_e30/metrics.csv`, `ft_wd0001_e30/summary.csv`를 우선으로 본다.

### 산출 파일

- `finetune_experiments_v273/ft_lowlr_e30/best_model.pt`
- `finetune_experiments_v273/ft_lowlr_e30/submission.csv`
- `finetune_experiments_v273/ft_verylowlr_e30/best_model.pt`
- `finetune_experiments_v273/ft_verylowlr_e30/submission.csv`
- `finetune_experiments_v273/ft_wd0001_e30/best_model.pt`
- `finetune_experiments_v273/ft_wd0001_e30/submission.csv`

## 2026-05-29 v2.7.3 checkpoint fine-tuning 후속 실험

### 목적

- 직전 실험 1등이었던 `ft_wd0001_e30` 주변 조건을 더 좁게 탐색했다.
- `weight_decay=0.0001` 조건을 유지하면서 epoch를 늘리는 실험과, weight decay 주변값 및 LR 절반 조건을 비교했다.
- Kaggle 제출은 하지 않고 validation metric 기준으로 비교했다.

### 실험 조건

| 실험명 | 모델 | epoch | batch | phase1_lr | phase2_lr | phase3_head_lr | phase3_backbone_lr | weight_decay | 변경점 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `ft_wd0001_e50` | YOLOv8l | 50 | 8 | 0.0001 | 0.0001 | 0.00001 | 0.000001 | 0.0001 | 이전 1등 조건에서 epoch만 50으로 증가 |
| `ft_wd00005_e30` | YOLOv8l | 30 | 8 | 0.0001 | 0.0001 | 0.00001 | 0.000001 | 0.00005 | weight decay 더 낮춤 |
| `ft_wd0002_e30` | YOLOv8l | 30 | 8 | 0.0001 | 0.0001 | 0.00001 | 0.000001 | 0.0002 | weight decay 약간 높임 |
| `ft_wd0001_lrhalf_e30` | YOLOv8l | 30 | 8 | 0.00005 | 0.00005 | 0.000005 | 0.0000005 | 0.0001 | LR 전체를 절반으로 낮춤 |
| `ft_wd0001_e30_repeat` | YOLOv8l | 30 | 8 | 0.0001 | 0.0001 | 0.00001 | 0.000001 | 0.0001 | 이전 1등 조건 반복 |

### 결과

| 순위 | 실험명 | best raw epoch | best raw mAP | best raw mAP50 | best EMA epoch | best EMA mAP | best EMA mAP50 | 판단 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `ft_wd0001_e50` | 20 | 0.961320 | 0.990983 | 36 | 0.956287 | 0.990983 | 이번 최고 |
| 2 | `ft_wd0002_e30` | 27 | 0.956821 | 0.990983 | 26 | 0.956225 | 0.990983 | EMA 기준 1등에 근접 |
| 3 | `ft_wd0001_e30_repeat` | 30 | 0.957913 | 0.990983 | 29 | 0.955679 | 0.990983 | 이전 1등 조건 재현성 확인 |
| 4 | `ft_wd00005_e30` | 12 | 0.955644 | 0.990983 | 24 | 0.955368 | 0.990983 | 나쁘지 않지만 0.0001보다 낮음 |
| 5 | `ft_wd0001_lrhalf_e30` | 11 | 0.956517 | 0.990983 | 13 | 0.951441 | 0.990983 | LR 절반은 효과 낮음 |

### 결론

- 현재까지 가장 좋은 validation 결과는 `ft_wd0001_e50`이다.
- 이전 최고였던 `ft_wd0001_e30`의 best raw mAP `0.958421`에서 `0.961320`으로 상승했다.
- `weight_decay=0.0001` 조건은 반복 실험에서도 안정적으로 좋은 편이었다.
- LR을 절반으로 낮추는 실험은 EMA 기준 성능이 낮아 우선순위를 낮춘다.
- `ft_wd0001_e50`은 best raw epoch가 20, best EMA epoch가 36이었고 마지막 epoch 50에서는 성능이 조금 내려갔다. 따라서 50 epoch까지 학습하되 best checkpoint를 선택하는 방식이 중요하다.

### 산출 파일

- `finetune_experiments_v273_next/summary_all.csv`
- `finetune_experiments_v273_next/ft_wd0001_e50/best_model.pt`
- `finetune_experiments_v273_next/ft_wd0001_e50/submission.csv`
- `finetune_experiments_v273_next/ft_wd0002_e30/best_model.pt`
- `finetune_experiments_v273_next/ft_wd0002_e30/submission.csv`
- `finetune_experiments_v273_next/ft_wd0001_e30_repeat/best_model.pt`
- `finetune_experiments_v273_next/ft_wd0001_e30_repeat/submission.csv`
