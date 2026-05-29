---
type: concept
title: "WBF (Weighted Box Fusion)"
tags: [concept, ensemble, postprocess]
related:
  - "[[concepts/NMS]]"
  - "[[concepts/앙상블]]"
  - "[[concepts/mAP]]"
  - "[[tasks/issue-59]]"
---

# WBF — Weighted Box Fusion

여러 모델의 예측 박스를 버리지 않고 **가중평균으로 합치는** 앙상블 후처리 방법.  
[[concepts/NMS]]와 달리 점수 낮은 박스를 버리지 않고 위치 정보를 보존함.

## NMS vs WBF 비교

| | NMS | WBF |
|---|---|---|
| 겹치는 박스 처리 | 점수 낮은 것 제거 | 가중평균으로 합침 |
| 박스 위치 | 최고 점수 박스 위치 그대로 | 여러 박스의 가중평균 위치 |
| 정보 보존 | 낮음 (나머지 버림) | 높음 |
| 앙상블 적합성 | 낮음 | 높음 |

## 동작 방식

```
모델 A: 박스[x1,y1,x2,y2], score=0.9, label=3351
모델 B: 박스[x1',y1',x2',y2'], score=0.8, label=3351

IoU ≥ iou_thr → 같은 객체로 판단
→ 위치 = (0.9×박스A + 0.8×박스B) / (0.9+0.8)
→ score = (0.9+0.8) / 2
→ label = 두 박스의 label이 같으면 그대로 유지
```

**중요**: 박스 좌표는 반드시 0~1로 정규화된 값이어야 함.  
→ `ensemble_wbf.py`에서 이미지 크기로 나눠서 정규화 처리.

## 이 프로젝트 실제 구현

**스크립트**: `ensemble_wbf.py`  
**라이브러리**: `ensemble-boxes` (`weighted_boxes_fusion`)

```python
from ensemble_boxes import weighted_boxes_fusion

boxes, scores, labels = weighted_boxes_fusion(
    boxes_list,   # [[박스들_모델A], [박스들_모델B], ...], 정규화 좌표
    scores_list,
    labels_list,
    weights=WBF_WEIGHTS,    # 기본: [1, 1, ...]
    iou_thr=0.5,            # 같은 객체로 묶는 IoU 임계값
    skip_box_thr=0.25,      # 이 점수 미만 박스는 WBF 전에 제거
)
```

**실제 기본 파라미터**:
- `iou_thr = 0.5` — IoU 0.5 이상이면 같은 객체로 묶음
- `skip_box_thr = 0.25` — score 0.25 미만 박스 무시
- `WBF_WEIGHTS = [1]` — 모델이 하나면 weight 1, 여러 개면 성능 좋은 쪽에 높게

## 앙상블 노트북에서 사용하는 방법

`notebooks/04_ensemble_submit.ipynb` cell 1 상단에서 설정:

```python
WBF_CHECKPOINTS = [
    "/content/drive/MyDrive/HealthEat/checkpoints/best_model_A.pt",
    "/content/drive/MyDrive/HealthEat/checkpoints/best_model_B.pt",
]
WBF_WEIGHTS   = [2, 1]    # A가 성능 더 좋으면 높게
WBF_IOU_THR   = 0.5
WBF_SKIP_BOX_THR = 0.25
```

체크포인트 1개이면 WBF 생략 → `submission_v1.csv` 그대로 사용 ([[concepts/앙상블]] 참고).

## 클래스 소프트 보팅

`ensemble_wbf.py`에는 WBF 외에 **클래스 소프트 보팅**도 구현돼 있음.  
같은 박스 위치에서 여러 모델이 다른 클래스를 예측할 때 score 가중합으로 최종 클래스 결정.  
→ WBF와 함께 사용해 위치와 클래스 모두 앙상블 효과.
