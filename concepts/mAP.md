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

| 기준 | 설명 | 특징 |
|---|---|---|
| mAP@0.5 | IoU threshold 0.5 기준 | 관대함. 박스가 절반만 겹쳐도 정답 |
| mAP@0.5:0.95 | IoU 0.5~0.95 구간 평균 (COCO 기준) | 엄격함. 박스 위치 정밀도까지 요구 |

학습 초반에 mAP@0.5:0.95가 0에 가까워도 mAP@0.5가 나오면 → 박스는 찾는데 위치 정밀도가 낮은 것.
둘 다 0이면 → 아예 못 찾는 것.

## val mAP / 캐글 mAP / train mAP

| 종류 | 정답 필요 | 계산 위치 | 설명 |
|---|---|---|---|
| val mAP | O | `train.py` 내부 | 학습 데이터 20% split으로 매 에폭 계산. 터미널에 출력 |
| 캐글 mAP | X (우리가 모름) | 캐글 서버 | submission.csv 제출 후 채점. test 이미지 정답은 캐글만 보유 |
| train mAP | O | 계산 가능하나 무의미 | 학습에 쓴 데이터라 높게 나와도 실제 성능 반영 안 됨 |

## split 전 mAP가 높았던 이유

split.py 도입 전, `PillDataset(split="val")`이 val 폴더가 없어 train_images 전체를 로드했음.
→ train과 val이 완전히 같은 데이터 → 학습 데이터로 mAP 측정 → 0.1823 (과적합 수치)
→ split 도입 후 진짜 val 기준 → 0.0700 (정직한 수치)

## 관련 개념

- [[concepts/NMS]] — 중복 박스 제거 후 mAP 계산
- [[concepts/Bounding Box]] — 박스 형식과 좌표계
- [[concepts/Confidence Score]] — mAP 계산에 쓰이는 score
