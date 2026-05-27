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

## val mAP / 캐글 Score / train mAP — 세 가지 지표의 차이

같은 "mAP"라는 이름을 쓰지만 **계산하는 데이터가 다르고 목적이 다르다.**

| 지표 | 정답 보유 | 계산 위치 | 언제 보는가 | 목적 |
|---|---|---|---|---|
| train mAP | 우리 | `train.py` 내부 | 학습 중 | 학습이 진행되는지 확인 (참고용) |
| val mAP | 우리 | `train.py` 내부 | 매 에폭 | 과적합 감지, 체크포인트 선택 기준 |
| 캐글 Score | 캐글 서버만 | 캐글 채점 서버 | 제출 후 | 최종 순위 결정, 진짜 성능 |

### train mAP — 거의 보지 않는다

학습에 쓴 데이터로 다시 측정하므로 당연히 높게 나온다. "모델이 학습 데이터를 얼마나 외웠는가"를 보여줄 뿐, 실제 성능과 무관하다.

### val mAP — 우리가 직접 보는 유일한 지표

우리가 split으로 따로 떼어둔 20% 데이터에서 계산한다. 모델이 못 본 데이터에서 얼마나 잘 맞추는지를 나타내므로 체크포인트 선택의 기준이 된다.

단, **val mAP는 우리가 split한 방식에 따라 편향될 수 있다.** 랜덤 split이라면 train과 val의 분포가 비슷하게 나오지만, 실제 test 데이터 분포와는 다를 수 있다.

### 캐글 Score — 진짜 성능

캐글이 보유한 hidden test 데이터로 채점한다. 우리는 test 이미지의 정답을 볼 수 없다. 공식 평가 지표이므로 최종 순위는 이 숫자로 결정된다.

---

## val mAP와 캐글 Score가 다른 이유

둘 다 mAP 공식으로 계산하지만 **데이터가 다르기 때문에** 항상 차이가 난다.

### 케이스별 해석

| val mAP | 캐글 Score | 해석 | 대응 |
|---|---|---|---|
| 높음 ↑ | 높음 ↑ | 진짜 성능 향상 | 이 방향 유지 |
| 높음 ↑ | 낮음 ↓ | **val 과적합** — val 분포에만 잘 맞춤 | Augmentation 강화, 규제 추가 |
| 낮음 ↓ | 높음 ↑ | val split이 편향됐을 가능성 | split 방식 재검토 |
| 낮음 ↓ | 낮음 ↓ | 모델 자체가 약함 | 학습 전략 전면 재검토 |

### val mAP가 캐글 Score보다 높게 나오는 주요 원인

1. **데이터 분포 차이**: 우리 train/val은 같은 원천 데이터에서 split했지만 test는 다른 촬영 조건·배경·조명일 수 있다.
2. **val set이 너무 작음**: 186장 중 20%면 val이 약 37장 수준. 샘플이 적으면 특정 클래스가 우연히 쉽게 나올 수 있다.
3. **과적합**: 모델이 val에도 은연중에 맞춰진 경우 (예: 하이퍼파라미터를 val mAP 기준으로 계속 튜닝하면 val에 과적합).

---

## 어떻게 같이 써야 하는가

```
val mAP → 매 에폭 보면서 학습 방향 결정
캐글 Score → 최종 제출 전 체크포인트 몇 개를 비교할 때 사용
```

val mAP가 올랐다고 무조건 제출하지 말고, 올랐을 때 한 번 제출해서 캐글 Score도 같이 올랐는지 확인한다. 만약 val mAP는 올랐는데 캐글 Score는 제자리면 val 과적합 신호다.

---

## split 전 mAP가 높았던 이유 (이 프로젝트 사례)

split.py 도입 전, `PillDataset(split="val")`이 val 폴더가 없어 train_images 전체를 로드했음.
→ train과 val이 완전히 같은 데이터 → 학습 데이터로 mAP 측정 → **0.1823** (과적합 수치)
→ split 도입 후 진짜 val 기준 → **0.0700** (정직한 수치)

숫자가 절반 이하로 떨어졌지만 이게 오히려 정확한 현재 성능이다.

---

## 관련 개념

- [[concepts/NMS]] — 중복 박스 제거 후 mAP 계산
- [[concepts/Bounding Box]] — 박스 형식과 좌표계
- [[concepts/Confidence Score]] — mAP 계산에 쓰이는 score
