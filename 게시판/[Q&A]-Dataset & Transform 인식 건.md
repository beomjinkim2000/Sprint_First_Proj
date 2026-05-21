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

아 혹시 데이터셋 -> 트랜스폼 넘길때 이미지를 텐서0~1로 넘겨라는 뜻인가요?

다른 파트 모델이나 연구쪽에서 데이터셋 불러올때 0~1 사이 값을 받아서 뭔가를 하는걸로 이해했는데 아니라면 죄송합니다. 

<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">답변</span><hr style="flex:1;margin:0"></div>

<div style="display:flex;align-items:center;gap:12px;margin:16px 0"><hr style="flex:1;margin:0"><span style="font-weight:bold;white-space:nowrap">댓글</span><hr style="flex:1;margin:0"></div>

