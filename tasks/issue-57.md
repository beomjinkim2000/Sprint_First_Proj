---
issue: 57
title: "[inference] postprocess bbox filtering 개선"
assignee:
  - 박창준 (후처리)
label: inference
st: doing
milestone: v0.2
priority: p2
target: 2026-06-05
github: https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/57
---

# issue-57 — postprocess bbox filtering 개선

## 상태

- 브랜치: `fix/postprocess-score-improvement`
- PR 준비 중
- checkpoint 기반 시각화 확인 단계
- `--checkpoint none` 임시 옵션은 제거하고, 실제 checkpoint 로드 흐름으로 복구

## 작업 배경

Kaggle 제출 결과와 시각화에서 아래 문제가 확인됨.

- 같은 알약에 중복 bbox가 남는 경우
- 이미지 밖으로 나가는 bbox
- 이미지 대부분을 덮는 큰 false positive bbox
- 제출 CSV에서 음수 좌표 bbox와 큰 bbox가 확인됨

이번 작업은 모델 자체 성능 개선이 아니라, 제출 전 명백히 비정상적인 prediction bbox를 줄이는 목적이다.

## 구현 범위

### `configs/default.yaml`

```yaml
postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.7
  max_detections: 4
  class_agnostic_nms: true
  clamp_boxes: true
  max_box_area_ratio: 0.25
  min_box_area_ratio: null
```

### `src/engine/postprocess.py`

- `PostprocessConfig`에 후처리 옵션 추가
- class-agnostic NMS 지원
  - 클래스가 달라도 같은 위치에 겹치는 박스는 score 높은 하나만 남김

### root `predict.py`

- 모델 출력 bbox를 원본 이미지 크기로 scale back
- 원본 이미지 기준으로 bbox clamp 적용
- width/height가 0 이하인 bbox 제거
- `max_box_area_ratio` 기준으로 너무 큰 bbox 제거

## 좌표 기준 정리

모델은 resize된 `640x640` 이미지 기준으로 bbox를 예측한다.

- validation / resize 이미지 시각화: GT와 prediction 모두 640 기준 유지
- Kaggle submission: 원본 이미지 기준 좌표 필요

따라서 root `predict.py`에서는 Kaggle 제출용 prediction을 만들기 위해 640 기준 bbox를 원본 이미지 크기로 되돌린 뒤 clamp와 area filtering을 적용한다.

## 테스트

```bash
python3 -m py_compile predict.py
.venv/bin/python -m pytest tests/test_postprocess.py tests/test_make_submission.py tests/test_inference_submission_pipeline.py
```

결과:

```text
11 passed
```

## 시각화 확인

- test 이미지: prediction bbox만 빨간색으로 확인
- train 이미지: GT는 초록색, prediction은 빨간색으로 확인
- checkpoint 없이 기본 모델로 확인한 결과는 class/score 판단에 사용하지 않음
- 실제 checkpoint 확보 후 동일 코드로 후처리 효과를 다시 확인

## 2026-05-27 후처리 시각화 비교 상세

| 묶음 | 조건 | 목적 | 결과 | 판단 |
|---|---|---|---|---|
| Ultralytics NMS 기본 | `conf=0.25`, `iou=0.7`, `class_agnostic=False` | 기본 NMS 안정성 확인 | 가장 안정적 | 유지 후보 |
| Class-agnostic NMS | `conf=0.25`, `iou=0.7`, `class_agnostic=True` | 클래스가 다른 중복 bbox 제거 가능성 확인 | 일부 이미지에서 큰 false positive bbox 발생 | 기본값 적용은 신중 |
| Class-agnostic + clamp + max area | `class_agnostic=True` + bbox clamp + `max_box_area_ratio=0.25` | 큰 이상 bbox 제거 확인 | 특정 큰 bbox 제거에는 효과 있음 | 기본 적용은 보류 |
| Fallback | 후보를 넉넉히 뽑고 필터 후 부족하면 복구 | 후처리 후 bbox 부족 보완 | false positive까지 복구될 위험 있음 | 보류 |
| Threshold A | `conf=0.25`, `iou=0.7`, `class_agnostic=False` | threshold / NMS 기준선 | 가장 안정적 | 추천 |
| Threshold B | `conf=0.25`, `iou=0.7`, `class_agnostic=True` | class-agnostic 영향 확인 | 큰 false positive bbox 발생 | 보류 |
| Threshold C | `conf=0.10`, `iou=0.7`, `class_agnostic=True` | 낮은 confidence로 recall 증가 여부 확인 | false positive 증가 | 보류 |
| Threshold D | `conf=0.10`, `iou=0.5`, `class_agnostic=True` | 낮은 confidence + 강한 NMS 조합 확인 | 안정적인 개선으로 보기 어려움 | 보류 |

### 판단

- 현재 시각화 기준으로는 `conf=0.25`, `iou=0.7`, `class_agnostic=False` 조합이 가장 안정적이었다.
- `bbox clamp`, `max_box_area_ratio`, `fallback`은 특정 케이스에서 효과가 있었지만 정답 bbox 제거 또는 false positive 복구 위험이 있어 기본 적용은 보류한다.
- 최신 checkpoint 확보 후 동일 train 샘플 기준으로 후처리 결과를 다시 비교한다.
- 해당 실험은 Kaggle에 제출하지 않았고, train 샘플 5장 시각화 비교만 진행했다.

## 남은 확인

- 실제 checkpoint 기준 submission 재생성
- row 수 / 예측 image 수 / 음수 bbox 수 / 큰 bbox 수 비교
- 같은 train 이미지 5장 기준 수정 전후 시각화 비교
- Kaggle score 비교

## 2026-05-28 YOLOv8m checkpoint 후처리 시각화 재비교

최신 main 기준 YOLOv8m 팀원 checkpoint로 후처리 결과를 다시 확인했다.

비교 대상:

| 구분 | checkpoint | postprocess 조건 | 결과 | 판단 |
|---|---|---|---|---|
| EMA default | `best_model_ema_YJY.pt` | `conf=0.25`, `iou=0.7`, `max_det=4`, `class_agnostic_nms=True` | GT와 prediction이 대부분 잘 맞음 | 유지 후보 |
| EMA agnostic false | `best_model_ema_YJY.pt` | `class_agnostic_nms=False` | 일부 이미지에서 큰 이상 bbox 발생 | 보류 |
| RAW default | `best_model_YJY.pt` | `conf=0.25`, `iou=0.7`, `max_det=4`, `class_agnostic_nms=True` | GT와 prediction이 잘 맞고 score가 전반적으로 높음 | 1순위 후보 |
| RAW agnostic false | `best_model_YJY.pt` | `class_agnostic_nms=False` | 일부 이미지에서 큰 이상 bbox 발생 | 보류 |

### 판단

- YOLOv8m checkpoint 기준으로는 최신 main 기본값인 `class_agnostic_nms=True`가 더 안정적이었다.
- `class_agnostic_nms=False`는 train 샘플 시각화에서 큰 false positive bbox가 발생해 기본값으로 쓰기 어렵다.
- EMA와 RAW 모두 default 조건에서는 bbox가 GT와 잘 맞았고, RAW 쪽 score가 조금 더 높게 나오는 경향이 있었다.
- 현재 기준 1순위 후처리 조합은 `best_model_YJY.pt` + `class_agnostic_nms=True` + `conf=0.25` + `iou=0.7` + `max_det=4`이다.
- Kaggle 제출 비교는 진행하지 않았고, train 샘플 5장 시각화 기준 판단이다.

### 이전 실험과 달라진 점

- 2026-05-27 v2.2 계열 시각화에서는 `class_agnostic_nms=False`가 더 안정적으로 보였다.
- 2026-05-28 YOLOv8m checkpoint에서는 반대로 `class_agnostic_nms=True`가 더 안정적이었다.
- 따라서 후처리 옵션은 모델/checkpoint가 바뀌면 다시 시각화로 확인해야 한다.

## 2026-05-28 YOLOv8m RAW conf threshold 비교

YOLOv8m RAW checkpoint와 `class_agnostic_nms=True` 조건을 고정한 뒤 `conf_threshold`만 변경해 시각화 결과를 비교했다.

비교 조건:

| 조건 | checkpoint | conf | iou | class_agnostic_nms | 결과 | 판단 |
|---|---|---:|---:|---|---|---|
| conf015 | `best_model_YJY.pt` | 0.15 | 0.7 | true | 기준 이미지 5장 모두 동일 | 변경 근거 없음 |
| conf025 | `best_model_YJY.pt` | 0.25 | 0.7 | true | 기준 이미지 5장 모두 동일 | 현재 기본값 유지 |
| conf035 | `best_model_YJY.pt` | 0.35 | 0.7 | true | 기준 이미지 5장 모두 동일 | 변경 근거 없음 |
| conf050 | `best_model_YJY.pt` | 0.50 | 0.7 | true | 기준 이미지 5장 모두 동일 | 변경 근거 없음 |

### 판단

- 이번 5장 시각화에서는 `conf_threshold`를 0.15부터 0.50까지 바꿔도 결과가 완전히 동일했다.
- 예측 score가 대부분 0.91 이상으로 높아 `conf=0.50`에서도 제거되는 bbox가 없었다.
- 따라서 현재 기준에서는 `conf_threshold`를 바꿀 근거가 부족하고, 기본값 `0.25`를 유지한다.
- 다음 후처리 실험은 confidence보다 NMS의 겹침 제거 기준인 `iou_threshold` 비교가 더 의미 있어 보인다.

## 참고

bbox clamp와 area filtering은 전처리에서도 유사하게 사용할 수 있지만 목적이 다르다.

- 전처리: GT annotation 정리
- 후처리: 모델 prediction을 제출 전에 정리

현재 `dataset.py`는 이미지 범위 밖 annotation을 skip하고 있고, 이번 PR은 inference 결과에 대한 방어 로직을 추가하는 작업이다.
