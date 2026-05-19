---
type: concept
title: "src/utils 사용 가이드"
created: 2026-05-19
updated: 2026-05-19
tags:
  - architecture
  - utils
status: mature
related:
  - "[[architecture/interfaces]]"
  - "[[architecture/module-design]]"
  - "[[workflow/dev-rules]]"
---

# src/utils 사용 가이드

> 팀 공통 유틸 모음. 직접 구현하지 말고 여기서 import해서 쓸 것.

---

## bbox.py — 바운딩 박스 좌표 변환

알약 위치를 표현하는 좌표 형식이 두 가지라 변환이 필요함.

| 형식 | 설명 | 언제 씀 |
|---|---|---|
| `[x1, y1, x2, y2]` | 좌상단 + 우하단 픽셀 좌표 | 모델 학습/예측 내부 |
| `[x, y, w, h]` | 좌상단 + 너비/높이 | Kaggle 제출 CSV |

```python
from src.utils.bbox import xyxy_to_xywh, xywh_to_xyxy

boxes = torch.tensor([[10, 20, 50, 80]])  # [x1, y1, x2, y2]

xyxy_to_xywh(boxes)  # → [[10, 20, 40, 60]]  (x, y, w, h)  제출용
xywh_to_xyxy(boxes)  # → [[10, 20, 50, 80]]  (x1, y1, x2, y2)  로딩 시
```

- **dataset.py 작성 시**: annotation이 xywh면 `xywh_to_xyxy()` 후 반환
- **make_submission.py 작성 시**: 예측 boxes를 `xyxy_to_xywh()` 후 CSV 저장

---

## collate.py — DataLoader 배치 묶음 함수

DataLoader에 반드시 넘겨야 하는 함수. **직접 구현하지 말 것**.

```python
from src.utils.collate import collate_fn
from torch.utils.data import DataLoader

loader = DataLoader(dataset, batch_size=16, collate_fn=collate_fn)

images, targets = next(iter(loader))
# images:  List[Tensor]  길이=batch_size, 각 shape [3, H, W]
# targets: List[Dict]    길이=batch_size, 각 dict에 boxes/labels/image_id
```

**왜 필요한가?** 알약 개수가 이미지마다 다르기 때문. 기본 collate는 shape이 다른 tensor를 stack하려다 에러 발생.

---

## validate.py — 데이터셋 / 배치 입력 검증

**2단계 검증 구조:**
- Stage 1: 랜덤 10장 먼저 확인 → 실패 시 즉시 중단 + 원인 출력
- Stage 2: 통과 시 전체 이미지 확인

```python
from src.utils.validate import validate_dataset, validate_batch

# train.py 학습 시작 전 — 데이터셋 전체 검증
validate_dataset(train_dataset, img_size=cfg.train.img_size)

# engine/train.py 루프 진입 직전 — 첫 배치 빠른 확인
images, targets = next(iter(train_loader))
validate_batch(images, targets, img_size=cfg.train.img_size)
```

**필수 조건 (위반 시 AssertionError):**
- torch.Tensor 타입
- 차원 `[C, H, W]` 또는 `[B, C, H, W]`
- 채널 수 = 3
- H, W가 32의 배수 (YOLO backbone 요구사항)
- 패키지 설치 여부

**권장 조건 (위반 시 warning만):**
- dtype `float32`
- 값 범위 `0~1` (정규화 여부)

> 전처리를 못 믿어서가 아니라, 형식 불일치를 학습 중간이 아닌 **시작 전에** 잡기 위함.

---

## tests/mock_dataset.py — 검증 테스트용 Mock

실제 데이터 없이 validate_dataset이 올바르게 동작하는지 확인하는 도구.
**Data 담당자가 dataset.py 구현 후 형식이 맞는지 확인할 때 기준점으로 사용.**

```bash
python tests/mock_dataset.py
```

**두 가지 용도:**

1. 정상 케이스 — 올바른 형식으로 만든 mock이 validation을 통과하는지 확인
2. 위반 케이스 — 각 조건을 의도적으로 깨서 validator가 제대로 잡는지 확인

```python
from tests.mock_dataset import MockDataset
from src.utils.validate import validate_dataset

# 정상 mock으로 validate_dataset 동작 확인
validate_dataset(MockDataset(img_size=640), img_size=640)

# 내 dataset.py가 올바른 형식인지 확인
from src.data.dataset import PillDataset
validate_dataset(PillDataset("data/processed", split="train"), img_size=640)
```

**break_rule 옵션** (의도적 위반 생성):

| break_rule | 위반 조건 | 예상 결과 |
|---|---|---|
| `"not_tensor"` | torch.Tensor가 아님 | AssertionError |
| `"wrong_ndim"` | 차원이 잘못됨 | AssertionError |
| `"wrong_channel"` | 채널 수가 3이 아님 | AssertionError |
| `"wrong_size"` | H, W가 32배수 아님 | AssertionError |
| `"wrong_dtype"` | dtype이 float32 아님 | warning만 |
| `"wrong_range"` | 값 범위가 0~1 벗어남 | warning만 |

---

## seed.py — 재현성 시드 고정

```python
from src.utils.seed import set_seed

set_seed(cfg.train.seed)  # train.py 맨 앞에서 한 번만 호출
```

seed 값은 `configs/default.yaml`의 `train.seed`에서 읽을 것.

---

## visualize.py — 바운딩 박스 시각화

이미지 위에 예측/정답 박스를 그려서 확인. 주로 노트북에서 씀.

```python
from src.utils.visualize import draw_boxes
from PIL import Image

image = Image.open("sample.jpg")
boxes = torch.tensor([[10, 20, 50, 80]])  # xyxy
result = draw_boxes(image, boxes, labels=["aspirin"], scores=torch.tensor([0.95]))
result.show()
```

---

## Connections

- [[architecture/interfaces]] — 각 함수가 따르는 형식 계약
- [[architecture/module-design]] — 어떤 모듈에서 어떤 유틸을 쓰는지
- [[workflow/dev-rules]] — utils 직접 구현 금지 규칙
