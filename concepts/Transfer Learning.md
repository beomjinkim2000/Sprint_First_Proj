---
type: concept
title: "Transfer Learning (전이학습)"
tags: [concept, training, model]
related:
  - "[[concepts/YOLOv8]]"
  - "[[concepts/Augmentation]]"
  - "[[workflow/실험 전략]]"
  - "[[tasks/issue-61]]"
---

# Transfer Learning — 전이학습

이미 대규모 데이터로 학습된 모델의 가중치를 가져와 새 태스크에 맞게 재학습하는 방법.

## 왜 필요한가

YOLOv8은 COCO(자연 이미지 80 클래스, 33만 장)로 학습됨.
이 프로젝트의 알약 이미지는 COCO와 도메인이 크게 다름:
- 배경이 단순 (흰 배경 등)
- 객체가 작고 유사한 형태
- 클래스 수 56개, 이미지 수 적음

→ scratch 학습보다 pretrained 가중치 활용이 훨씬 효과적.

## Freeze 전략

학습 시 일부 레이어를 고정(freeze)하면 그 레이어의 가중치는 바뀌지 않음.

| 전략 | freeze 레이어 수 | 설명 |
|---|---|---|
| 전체 fine-tune | 0 | 모든 레이어 학습, 알약 도메인에 완전 적응 |
| 부분 freeze | 10 | backbone 초반 고정, 고수준 특징만 재학습 |
| backbone freeze | 22 | backbone 전체 고정, detection head만 학습 |

```python
# Ultralytics에서 freeze 설정
model.train(data="configs/pill.yaml", freeze=10, ...)
```

## 3-Phase 학습 전략 (이 프로젝트)

YOLOv8 Detect head 구조: cv1(box 특징) + cv2(box 예측) + cv3(클래스 예측)
cv3의 마지막 Conv2d만 새로 초기화(kaiming_normal)되고, 나머지는 pretrained 가중치 유지.

```
Phase 1 (freeze_ratio):   cv3 마지막만 학습 → 분류 레이어 적응
Phase 2 (finetune_ratio): Detect head 전체 학습 → box + cls 같이 개선
Phase 3 (나머지):          전체 언프리즈, backbone/neck은 낮은 lr로 살살
```

### Phase별 lr 설정 (configs/default.yaml)

```yaml
phase1_lr: 0.001 / phase1_lr_min: 0.00001   # Phase 1 코사인 범위
phase2_lr: 0.001 / phase2_lr_min: 0.00001   # Phase 2 코사인 범위
phase3_head_lr: 0.001                         # head lr
phase3_backbone_lr_ratio: 0.1               # backbone = head × ratio
phase3_lr_min: 0.00001
```

Phase가 바뀔 때 lr이 리셋되고 코사인으로 다시 감소함 → [[concepts/LR Scheduling]] 참고.

### freeze 안 하면 어떻게 되나

backbone이 lr=0.001로 처음부터 학습되면 COCO에서 학습된 특징이 망가짐.
사실상 scratch 학습과 같아서 186장으론 수렴 불가.

## 판단 기준

- freeze 많을수록 → 학습 빠름, 과적합 적음, COCO 특징 보존
- freeze 적을수록 → 알약 도메인에 더 잘 적응, 학습 시간 증가

## 관련 개념

- [[concepts/YOLOv8]] — 사용 모델
- [[concepts/Augmentation]] — freeze와 함께 overfitting 방지에 기여
- [[concepts/LR Scheduling]] — 코사인 스케줄러와 phase별 lr
