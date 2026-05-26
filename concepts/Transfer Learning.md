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

## Backbone / Neck / Head — 모델 구조

freeze 전략을 이해하려면 먼저 YOLOv8이 어떤 구역으로 나뉘는지 알아야 한다.

### 구역 구분

Ultralytics는 모델 구조를 `ultralytics/cfg/models/v8/yolov8.yaml`에 선언한다.

```yaml
backbone:
  - [-1, 1, Conv,  [64, 3, 2]]   # 0
  - ...
  - [-1, 1, SPPF, [512, 5]]      # 9  ← backbone 끝

head:  # Ultralytics는 neck+detect를 합쳐 head로 부름
  - [-1, 1, nn.Upsample, ...]    # 10 ← neck 시작
  - ...
  - [-1, 3, C2f, [256]]          # 15 ← P3 (작은 객체)
  - [-1, 3, C2f, [512]]          # 18 ← P4 (중간 객체)
  - [-1, 3, C2f, [512]]          # 21 ← P5 (큰 객체)
  - [[15,18,21], 1, Detect, ...] # 22 ← Detect head
```

→ **레이어 0~9 = backbone**, **10~21 = neck**, **22 = Detect head**

### 코드로 직접 확인

```python
from ultralytics import YOLO
model = YOLO("yolov8n.pt")

for i, layer in enumerate(model.model.model):
    print(f"[{i:2d}] {type(layer).__name__}")
```

```
[ 0] Conv
...
[ 9] SPPF      ← backbone 마지막. 여러 크기 풀링으로 넓은 맥락을 압축
[10] Upsample  ← neck 시작. FPN이 위쪽 방향으로 특징맵을 합침
...
[15] C2f       ← P3 출력 (작은 객체 탐지용)
[18] C2f       ← P4 출력
[21] C2f       ← P5 출력 (큰 객체 탐지용)
[22] Detect    ← cv2(box 좌표) + cv3(클래스)
```

backbone 끝은 SPPF 레이어로 찾는다:

```python
for i, layer in enumerate(model.model.model):
    if type(layer).__name__ == "SPPF":
        print(f"backbone 끝: layer {i}")  # → 9
        break
```

### Detect head 내부 (cv2 / cv3)

```python
detect = model.model.model[-1]

for name, module in detect.named_children():
    print(f"{name}: {module}")
```

```
cv2: ModuleList(Sequential → Conv → Conv → Conv2d)  ← box 좌표 예측 (3 스케일)
cv3: ModuleList(Sequential → Conv → Conv → Conv2d)  ← 클래스 예측 (3 스케일)
```

cv3 마지막 Conv2d만 kaiming_normal로 새로 초기화되는 이유:
클래스 수가 COCO(80) → 알약(56)으로 바뀌어 출력 채널이 달라지기 때문. 나머지는 pretrained 가중치 유지.

## Freeze 전략

학습 시 일부 레이어를 고정(freeze)하면 그 레이어의 가중치는 바뀌지 않음.
`freeze=N`을 주면 Ultralytics가 첫 N개 레이어의 `requires_grad=False`로 세팅한다.

| 전략 | freeze 값 | 고정 범위 | 설명 |
|---|---|---|---|
| 전체 fine-tune | 0 | 없음 | 모든 레이어 학습, 알약 도메인에 완전 적응 |
| 부분 freeze | 10 | 레이어 0~9 (backbone) | backbone 고정, neck+head 재학습 |
| head만 학습 | 22 | 레이어 0~21 (backbone+neck) | Detect head만 학습 |

```python
model.train(data="configs/pill.yaml", freeze=10, ...)
```

### freeze 안 하면 어떻게 되나

backbone이 lr=0.001로 처음부터 학습되면 COCO에서 학습된 특징이 망가짐.
사실상 scratch 학습과 같아서 186장으론 수렴 불가.

### 판단 기준

- freeze 많을수록 → 학습 빠름, 과적합 적음, COCO 특징 보존
- freeze 적을수록 → 알약 도메인에 더 잘 적응, 학습 시간 증가

## 3-Phase 학습 전략 (이 프로젝트)

freeze를 단계적으로 풀면서 학습하는 방식.

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
phase3_backbone_lr_ratio: 0.1                # backbone = head × ratio
phase3_lr_min: 0.00001
```

Phase가 바뀔 때 lr이 리셋되고 코사인으로 다시 감소함 → [[concepts/LR Scheduling]] 참고.

## Discriminative LR (차등 학습률)

Phase 3에서 레이어 그룹마다 다른 lr을 적용하는 방법.

- backbone/neck: 이미 좋은 특징 보유 → 크게 바꾸면 망가짐 → lr 작게
- head: 새 도메인에 맞게 학습 필요 → lr 크게

```python
backbone_layers = list(model.model.model[:10])
neck_layers     = list(model.model.model[10:22])
head_layer      = model.model.model[-1]

def get_params(layers):
    if isinstance(layers, list):
        return [p for l in layers for p in l.parameters()]
    return list(layers.parameters())

optimizer = torch.optim.AdamW([
    {"params": get_params(backbone_layers), "lr": 1e-5},  # 사전학습 특징 보존
    {"params": get_params(neck_layers),     "lr": 5e-5},
    {"params": get_params(head_layer),      "lr": 1e-4},  # 알약 도메인 적응
])
```

한 optimizer 안에서 param_group으로 분리해 각자 다른 lr로 업데이트 → [[concepts/Optimizer]] 참고.

## 관련 개념

- [[concepts/YOLOv8]] — 사용 모델
- [[concepts/Augmentation]] — freeze와 함께 overfitting 방지에 기여
- [[concepts/LR Scheduling]] — 코사인 스케줄러와 phase별 lr
- [[concepts/Optimizer]] — AdamW, SGD, momentum, weight decay
