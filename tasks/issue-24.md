---
issue: 24
title: "[inference] predict.py 스켈레톤 구현"
assignee: cjkj1234
label: inference
st: done
milestone: Milestone
priority: p1
target: 2026-05-21
github: https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/24
---

# issue-24 — predict.py 스켈레톤 구현

## 상태

- PR #26 merge 완료: 2026-05-25
- `src/engine/predict.py` 구현 완료
- DummyModel 기반 테스트 작성 완료

## 구현 범위

- `predict_batch(model, images, device)`
- batch tensor를 device로 이동
- model forward 수행
- raw model output 그대로 반환

## 책임 경계

`src/engine/predict.py`는 model forward 단일 책임만 가진다.
아래 작업은 predict.py에서 하지 않는다.

- `model.eval()` 호출: 루트 `predict.py` 책임
- confidence filtering: `src/engine/postprocess.py` 책임
- NMS: `src/engine/postprocess.py` 책임
- pred_dict 생성: `src/engine/postprocess.py` 책임
- CSV 저장: `src/submission/make_submission.py` 책임

## 테스트

```bash
python -m pytest tests/test_predict_mock.py
```

## 다음 연결

`predict_batch()` 출력은 `postprocess_raw_outputs()` 입력으로 연결한다.
