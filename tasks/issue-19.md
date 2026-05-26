---
issue: 19
title: "[submission] make_submission.py 구현"
assignee: beomjinkim2000
label: submission
st: done
milestone: v0.1
priority: p1
target: 2026-05-24
github: https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/19
---

# issue-19 — make_submission.py 구현

## 상태

- PR #40 merge 완료: 2026-05-25
- `src/submission/make_submission.py` 구현 완료
- `tests/test_make_submission.py` 추가 완료

## 구현 범위

- postprocess 출력 형식인 `List[Prediction]` 입력
- `annotation_id`를 1부터 순서대로 생성
- 내부 bbox `xyxy`를 Kaggle 제출용 `xywh`로 변환
- CSV 컬럼 순서 고정
- 예측 결과가 비어 있어도 header-only CSV 생성 가능

## 테스트

```bash
python -m py_compile src/submission/make_submission.py tests/test_make_submission.py
python -m pytest tests/test_make_submission.py
```

## 남은 확인

- label과 Kaggle `category_id`가 동일한지 확인
- 다르면 `configs/class_mapping.json` 기준으로 label → category_id 매핑 추가
- predict → postprocess → submission 통합 테스트에서 다시 검증
