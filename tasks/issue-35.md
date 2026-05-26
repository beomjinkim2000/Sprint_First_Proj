---
issue: 35
title: "[inference] src/engine/postprocess.py 구현"
assignee: cjkj1234
label: inference
st: done
milestone: Milestone
priority: p1
target: 2026-05-25
github: https://github.com/beomjinkim2000/Code_IT_Team_1_FirstProject/issues/35
---

# issue-35 — postprocess.py 구현

## 상태

- PR #37 merge 완료: 2026-05-25
- `src/engine/postprocess.py` 구현 완료
- `tests/test_postprocess.py` 추가 및 통과

## 구현 범위

- Prediction dict 후처리
- raw model output → Prediction list 변환
- raw bbox `cxcywh` → 내부 표준 `xyxy` 변환
- confidence threshold filtering
- class-aware NMS
- `max_detections` 제한
- 빈 예측 결과도 인터페이스 형식 유지

## 입출력

입력 raw output:

```python
tuple[torch.Tensor]  # first tensor shape: [B, 4 + num_classes, num_anchors]
```

출력 Prediction list:

```python
[
    {
        "image_id": int,
        "boxes": torch.Tensor,   # [N, 4], xyxy 절대 픽셀
        "labels": torch.Tensor,  # [N], int64
        "scores": torch.Tensor,  # [N], float32
    }
]
```

## 테스트

```bash
python -m py_compile src/engine/postprocess.py tests/test_postprocess.py
python -m pytest tests/test_postprocess.py
```

## 다음 연결

`postprocess_raw_outputs()` 출력은 `make_submission()` 입력으로 연결한다.
통합 테스트에서는 `DummyModel → predict_batch → postprocess_raw_outputs → make_submission` 흐름을 확인한다.
