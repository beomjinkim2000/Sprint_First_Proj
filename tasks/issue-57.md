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

## 남은 확인

- 실제 checkpoint 기준 submission 재생성
- row 수 / 예측 image 수 / 음수 bbox 수 / 큰 bbox 수 비교
- 같은 train 이미지 5장 기준 수정 전후 시각화 비교
- Kaggle score 비교

## 참고

bbox clamp와 area filtering은 전처리에서도 유사하게 사용할 수 있지만 목적이 다르다.

- 전처리: GT annotation 정리
- 후처리: 모델 prediction을 제출 전에 정리

현재 `dataset.py`는 이미지 범위 밖 annotation을 skip하고 있고, 이번 PR은 inference 결과에 대한 방어 로직을 추가하는 작업이다.
