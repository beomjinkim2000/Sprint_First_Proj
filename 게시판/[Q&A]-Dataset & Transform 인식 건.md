---
글쓴사람: 황원재(Data)
날짜: 2026-05-22 01:49
상태: 미해결
tags:
  - qna
---
<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">질문</span><hr style="flex:1;margin:0"></div>








코덱스 5.5 high랑 두시간 싸우다가
데이터셋 트랜스폼에 대해서 질문 남깁니다.

데이터셋 : 이미지파일을 tensor(0~1 nomalize)로 변경(resize등 추가 전처리없음)
트랜스폼 : 0~1 텐서로 변한것을 mean/std nomalize + resize(0~1이미지/bbox) + augmentation

라고 인식했는데 트랜스폼에서 mean/std nomalize를 하면 데이터셋이 출력을 0~1텐서가 아닌 -2~2 범위 Tensor로 최종출력한다고 생각해서 질문 남깁니다.

한줄요약하자면 데이터셋 ~ 트랜스폼 과정에서 0~1 nomalize만 하는지 0~1 nomalize+mean/std nomalize를 하는건지 인식을 맞췄으면 합니다. 
이유 : 인터페이스 계약서 데이터셋 내용에 # image: torch.Tensor [C, H, W], float32, 0~1 정         규화로 명시
     트랜스폼 이슈에는 리사이즈와 노멀라이제이션 진행

추가
아 혹시 데이터셋 -> 트랜스폼 넘길때 이미지를 텐서0~1로 넘겨라는 뜻인가요?

다른 파트 모델이나 연구쪽에서 데이터셋 불러올때 0~1 사이 값을 받아서 뭔가를 하는걸로 이해했는데 아니라면 죄송합니다. 

<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">답변</span><hr style="flex:1;margin:0"></div>

> [!note] 유재열(Model)
> 1. 인터페이스 계약서에는 image: torch.Tensor [C,H,W], float32, 0~1 정규화 로 출력을 하도록 명시가 되어있다
> 2. YOLOv8은 보통 mean/std normalize를 안 씀
>
> 결론 : nomalize+mean/std nomaliz를 하지 않는게 맞다고 합니다.

> [!note] 김범진(PM)
> 3줄 요약
>
> - 우리 프로젝트는 **0~1 normalize만 한다. Mean/std normalize는 안 한다.**
> - transforms.py는 따로 도는 게 아니라 **dataset.py.__getitem__() 안에서 같이 호출되는 구조**다.
> - 증강은 transforms.py, 최종 tensor 변환 + 0~1 normalize는 dataset.py가 마무리한다.
>
>
>
>
>
> 최종 결론 : 0~1 normalize만 한다. Mean/std normalize는 하지 않습니다.
>
>
>
>< Normalize>
>
> 픽셀값 범위를 0~255에서 0~1로 바꿔서 입력값 스케일 자체를 줄임. -> 그럼 가중치가 팍 안튐.
>
>
>
> <Mean/std normalize>
>
> 평균을 계산이 들어가서 값을 0기준으로 맞춤 + 응집도 분포를 맞춤 -> 그럼 feature더 잘찾고 기울기가 이뻐져서 모델이 슥삭 김치함.
>
>
>
> <우리 프로젝트에서 Dataset과 Transform의 역할 차이>
>
> 결론 : **transforms.py는 dataset.py 내부에서 호출됩니다.**
>
> transforms.py가 dataset.py 다음에 따로 독립 실행되는 게 아니라,  
> dataset.py.__getitem__() 안에서 불려서 같이 돌아가는 구조입니다.
>
> 흐름은 아래와 같습니다.
>
> Dataset.py.__getitem__() 실행  
> → JPEG 열어서 numpy array로 읽기 (0~255 픽셀값)  
> → transforms.py 호출
>
> transforms.py 내부
>
> - resize
> - bbox 좌표도 같이 스몰라이트
> - flip, color jitter 등 증강
>
> (근데 아직 이 시점은 numpy, 픽셀값도 0~255 상태)
>
> 다시 dataset.py
>
> - [H, W, C] → [C, H, W] tensor 변환
> - 255로 나누기
> - 이때 0~1 normalize
> - return
>
> 즉
>
> dataset.py  
> → 이미지 로드
>
> transforms.py  
> → resize + bbox 조정 + 증강
>
> dataset.py  
> → tensor 변환 + normalize + return
>
> 정리하면
>
> - **증강은 transforms.py 담당**
> - **dataset.py는 transforms를 불러서 쓴 뒤 tensor 변환 + normalize 마무리**
>
>
>
> <분리 이유?>
>
> 결론 : **학습할 때랑 검증할 때 transform이 다르기 때문**
>
> - 학습할 때는 flip, color jitter 같은 증강 넣어서  
>     모델이 이것저것 보면서 **슥삭 김치하게 만듦**
> - 검증할 때는 증강 없이  
>     실제 이미지 그대로 넣어서 진짜 성능을 봐야 함
>
> 그래서 transform을 따로 분리해둡니다.
>
>
>
> <왜 인터페이스 계약서에서는 그렇게 보였을까?>
>
> 결론 : **혼란을 줄 수 있게 작성됨. 상세 작성 예정입니다.**
>
> transforms.py의 normalize는  
> 픽셀값 normalize 의미가 아니라,
>
> **resize 시 bbox 좌표 비율을 맞추는 normalize 의미**였는데  
> 계약서에 자세한 설명이 없다 보니 헷갈릴 수 있었습니다.
>
> 이 부분은 인터페이스 계약 명세서에 추가 예정입니다.
>
>
>
> <mean/std normalize 안 하는 이유>
>
> 결론 : **YOLOv8이 사전학습 때 mean/std normalize를 안 씀**
>
> YOLOv8 pretrained는
>
> - 0~1 normalize 사용
> - mean/std normalize 안 씀
>
> 사전학습 weight를 그대로 가져다 쓰려면  
> 전처리도 똑같이 맞춰줘야 됩니다.
>
> 괜히 여기서 mean/std 넣으면  
> YOLO 입장에서는 “어? 내가 먹던 밥 아닌데?” 하면서  
> feature 분포가 달라져서 **슥삭 김치 못할 수도 있음**
>
> 그래서 우리 프로젝트도
>
> - 0~1 normalize만 적용
> - mean/std normalize는 하지 않음
>
> 이 방향으로 갑니다.

<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">댓글</span><hr style="flex:1;margin:0"></div>

> [!note] 박창준(Exp)
> -0~1 normalize: 0~255 픽셀값을 0~1 float tensor로 변환
> -mean/std normalize: 0~1 tensor를 평균/표준편차 기준으로 표준화하므로 값 범위가 (-2~2) 등으로 바뀔 수 있음
>
> 계약서를 유지한다면 transform에서는 resize/augmentation/bbox 변환/ToTensor까지만 적용하고, mean/std normalize는 기본 비활성 또는 별도 옵션으로 분리라고 하네요
> --------저거 블록 어케 만들어요?---------

> [!note] 김범진(PM)
> 저거 그냥 쓰고 commit , push하면 알아서 hook으로 타는건데 버근가봐요 뭐지..