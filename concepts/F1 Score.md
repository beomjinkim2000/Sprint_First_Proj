---
type: concept
title: "F1 Score"
tags: [concept, evaluation, metric]
related:
  - "[[concepts/mAP]]"
  - "[[concepts/Confidence Score]]"
  - "[[experiment/실험 로그]]"
---

# F1 Score

## Precision / Recall

| 용어 | 의미 | 낮으면 |
|---|---|---|
| Precision | "알약이다"라고 한 것 중 진짜 알약 비율 | 없는 박스를 그리는 오탐이 많음 |
| Recall | 실제 알약 중 모델이 잡아낸 비율 | 알약을 못 찾고 놓치는 게 많음 |

```
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 × Precision × Recall / (Precision + Recall)
```

- TP: 예측 박스가 GT 박스와 IoU ≥ threshold이고 클래스도 맞는 경우
- FP: 예측했지만 GT와 매칭 안 된 박스 (위치 틀림 or 클래스 틀림)
- FN: GT 박스인데 모델이 못 잡은 경우

## mAP와 차이

| 지표 | 박스 위치 반영 | threshold | 용도 |
|---|---|---|---|
| F1 | X (클래스 분류만) | 하나 고정 | 클래스별 약점 파악, threshold 최적화 |
| mAP | O (IoU 포함) | 전 구간 평균 | 종합 성능 평가, Kaggle 제출 점수 |

F1은 threshold 하나에서의 스냅샷. mAP는 전 threshold 구간의 PR 곡선 넓이.  
Kaggle 메트릭이 mAP@50:95이므로 **종합 성능은 mAP, 약점 분석은 F1**으로 역할을 나눈다.

## 클래스별 F1 — 약점 클래스 파악

학습 후 val set에서 클래스마다 F1을 뽑으면 어떤 알약 종류가 bottleneck인지 보인다.

```
클래스 A: F1 = 0.97  → 문제 없음
클래스 B: F1 = 0.41  → bottleneck
  ├─ Precision 낮음 → 다른 알약으로 오탐 (외형 유사 클래스 문제)
  └─ Recall 낮음   → 아예 못 잡음 (데이터 부족 or 해상도 부족)
```

**구현 위치:** `train.py` → 매 에폭 `f1_{run_name}.csv`에 저장  
**활용 시점:** 실험 끝난 뒤 결과 분석

### 실험별 활용

| 실험 | 클래스별 F1 활용법 |
|---|---|
| Q4 (YOLO11x vs YOLOv8x) | 두 모델의 클래스별 F1 비교 → 어떤 아키텍처가 어떤 유형에서 강한지 |
| Q6 (해상도 1024) | 640에서 F1 낮은 클래스가 1024에서 개선되는지 → 각인/텍스트 클래스 집중 확인 |
| Q7 (AI Hub 데이터) | F1 낮은 클래스 = 데이터 부족 가능성 → 해당 클래스 데이터 우선 확보 |

## F1 곡선 — 최적 confidence threshold 찾기

confidence threshold를 낮춰가며 F1을 그리면 F1이 최대인 지점이 최적 threshold다.

```
conf = 0.05 → F1 계산 (IoU=0.5 고정)
conf = 0.10 → F1 계산
...
conf = 0.90 → F1 계산
→ F1 최대 지점 = 최적 conf → postprocess.conf_threshold에 반영 후 제출
```

**현재 conf=0.25는 관행적 값** — 이 모델에서 실제 최적이 0.4일 수도 있음.  
**활용 시점:** 학습 완료 후 best 모델에서 1회 실행, 제출 직전.  
**IoU 고정값:** 0.5 (mAP@50 기준과 동일, 해석 일관성)

WBF의 `skip_box_thr`도 같은 방식으로 최적화 가능.

## train F1 / train mAP는 의미 없는가

**의미 없다.** 모델이 학습 데이터를 직접 보고 가중치를 업데이트했으므로 같은 데이터에서 재측정하면 당연히 높게 나온다. 과적합 진단은 **train loss vs val loss**로 봐야 한다.

## 관련 개념

- [[concepts/mAP]] — 종합 성능 지표 (박스 위치 + 클래스, 전 threshold 평균)
- [[concepts/Confidence Score]] — threshold 기준값, F1 곡선의 x축
- [[concepts/NMS]] — F1 계산 전 중복 박스 제거
