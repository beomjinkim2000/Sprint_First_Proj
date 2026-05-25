---
type: concept
title: "mAP (Mean Average Precision)"
tags: [concept, evaluation, metric]
related:
  - "[[concepts/Bounding Box]]"
  - "[[concepts/NMS]]"
  - "[[experiment/실험 로그]]"
  - "[[workflow/실험 전략]]"
---

# mAP — Mean Average Precision

객체 탐지 모델의 표준 성능 평가 지표.

## 계산 흐름

```
예측 박스 + 정답 박스
      ↓
  IoU 계산 (겹침 비율)
      ↓
 IoU ≥ threshold → TP / FP 판별
      ↓
 Precision-Recall 곡선
      ↓
  AP (클래스별 넓이)
      ↓
 mAP = 전체 클래스 AP 평균
```

## IoU (Intersection over Union)

$$IoU = \frac{예측 박스 \cap 정답 박스}{예측 박스 \cup 정답 박스}$$

- IoU ≥ 0.5 이면 TP (맞춘 것)
- IoU < 0.5 이면 FP (틀린 것)

## mAP@0.5 vs mAP@0.5:0.95

| 기준 | 설명 |
|---|---|
| mAP@0.5 | IoU threshold 0.5 기준 |
| mAP@0.5:0.95 | IoU 0.5~0.95 구간 평균 (COCO 기준) |

이 프로젝트는 Kaggle 점수 기반 평가. 내부 검증은 mAP@0.5 사용.

## 관련 개념

- [[concepts/NMS]] — 중복 박스 제거 후 mAP 계산
- [[concepts/Bounding Box]] — 박스 형식과 좌표계
