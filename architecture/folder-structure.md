---
type: concept
title: "폴더 구조"
created: 2026-05-19
updated: 2026-05-19
tags:
  - architecture
  - setup
status: mature
related:
  - "[[index]]"
  - "[[architecture/module-design]]"
  - "[[architecture/interfaces]]"
---

# 폴더 구조

## 디렉토리 트리

```text
project/
├── README.md
├── requirements.txt
├── .gitignore
├── interfaces.md              ← 팀 인터페이스 계약서 (변경 시 팀장 승인)
├── train.py                   ← 루트 진입점: python train.py --config configs/default.yaml
├── configs/
│   └── default.yaml           ← 하이퍼파라미터, 경로, 클래스 목록
├── data/
│   ├── raw/                   ← .gitignore 처리 (AI Hub 원본)
│   ├── processed/             ← YOLO 포맷 변환 결과
│   └── sample_submission.csv  ← Kaggle 제출 형식 확인용
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_visualize_bbox.ipynb
├── src/
│   ├── data/
│   │   ├── dataset.py         ← Dataset __getitem__ → (image, target_dict)
│   │   ├── transforms.py      ← 이미지 + bbox 동시 변환
│   │   └── split.py           ← train/val 분리
│   ├── models/
│   │   └── baseline.py        ← build_model(num_classes) → nn.Module
│   ├── engine/
│   │   ├── train.py           ← 1 epoch 학습 루프
│   │   ├── evaluate.py        ← val mAP 계산
│   │   └── predict.py         ← 이미지 → pred_dict 리스트
│   ├── submission/
│   │   └── make_submission.py ← pred_dict → submission.csv
│   └── utils/
│       ├── bbox.py            ← [x1,y1,x2,y2] ↔ [x,y,w,h] 변환
│       ├── visualize.py       ← 바운딩 박스 오버레이
│       └── seed.py            ← 재현성 시드 고정
├── outputs/                   ← .gitignore 처리
│   ├── checkpoints/           ← best.pt, last.pt
│   ├── predictions/           ← 예측 결과 중간 저장
│   └── submissions/           ← submission_v1.csv, submission_v2.csv
└── reports/
    ├── figures/               ← 학습 곡선, 혼동행렬 이미지
    └── experiment_log.md      ← 버전별 실험 기록
```

## .gitignore 핵심 항목

```
data/raw/
data/augmented/
outputs/
*.pt
*.onnx
.venv/
__pycache__/
.DS_Store
```

## configs/default.yaml 예시

```yaml
model:
  name: yolov8n          # yolov8n / yolov8s / yolov8m
  num_classes: <EDA 후>

data:
  train: data/processed/images/train
  val: data/processed/images/val
  nc: <EDA 후>
  names: [<클래스 목록>]

train:
  epochs: 50
  batch_size: 16
  lr: 0.001
  img_size: 640
  seed: 42

paths:
  checkpoint: outputs/checkpoints/
  submission: outputs/submissions/
```

## Connections

- [[architecture/module-design]] — 각 파일의 책임과 입출력
- [[architecture/interfaces]] — 고정된 인터페이스 계약
