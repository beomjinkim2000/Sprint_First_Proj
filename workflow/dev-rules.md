---
type: concept
title: "개발 규칙"
created: 2026-05-19
updated: 2026-05-19
tags:
  - workflow
  - coding-standards
status: mature
related:
  - "[[workflow/git-strategy]]"
  - "[[architecture/interfaces]]"
  - "[[architecture/utils]]"
---

# 개발 규칙

> 브랜치/PR 규칙은 [[workflow/git-strategy]] 참고. 여기는 코드 규칙만.

---

## 커밋 메시지

```
[PILL-번호] 한 줄 요약

[PILL-8] Dataset __getitem__ 구현
[PILL-12] train loop 1 epoch 반환값 추가
[fix/PILL-16] submission bbox 형식 xywh로 수정
```

- 현재형 동사 ("추가", "수정", "제거")
- 한 커밋에 한 가지 변경

---

## 코드 규칙

**타입 힌트 필수** — 함수 인자와 반환값에 항상 표기

```python
# Good
def build_model(num_classes: int) -> torch.nn.Module:

# Bad
def build_model(num_classes):
```

**공통 유틸 직접 구현 금지** — `src/utils/` import해서 쓸 것

```python
from src.utils.bbox import xyxy_to_xywh   # bbox 변환
from src.utils.collate import collate_fn   # DataLoader 배치
from src.utils.seed import set_seed        # 시드 고정
from src.utils.validate import validate_batch  # 입력 검증
```

→ 유틸 상세: [[architecture/utils]]

**마법 숫자 금지** — config에서 읽어서 쓸 것

```python
# Bad
model = YOLO("yolov8n.pt")
DataLoader(dataset, batch_size=16)

# Good
model = YOLO(f"{cfg.model.name}.pt")
DataLoader(dataset, batch_size=cfg.train.batch_size)
```

---

## interfaces.md 변경 시

> 팀 전체 계약서 — 멋대로 바꾸면 다른 사람 코드가 깨짐

1. 팀장에게 먼저 카톡으로 변경 내용 공유
2. 팀장 확인 후 PR에서 변경
3. PR approve: 팀장 필수 (예외 없음)

→ 상세: [[architecture/interfaces]]

---

## Connections

- [[workflow/git-strategy]] — 브랜치/PR 규칙
- [[architecture/interfaces]] — 팀 인터페이스 계약서
- [[architecture/utils]] — 공통 유틸 사용법
