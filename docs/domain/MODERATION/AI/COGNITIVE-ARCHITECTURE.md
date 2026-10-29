# 인지 구조 설계

<br>

### 서브태스크의 인지 구조

**1. 게시물 검수**

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    A["<b>입력</b><br/>게시물 텍스트와 이미지"] --> B["<b>AI 검수</b>"]
    B --> C["<b>응답 검사</b>"]
    C --> D["<b>검수 결과</b>"]
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    classDef check fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
    class A,D data
    class B task
    class C check
```

텍스트와 이미지를 하나의 맥락으로 묶어 모델이 함께 판단한다. 모델의 판정은 코드가 형식과 일관성을 확인한 뒤 결과로 반환한다.

<br>

### 모델과 코드의 책임

| 맡는 쪽 | 맡는 일 |
|---|---|
| 모델 | 표현과 맥락을 해석해 서비스 기준 위반 여부 판단 |
| 코드 | 모델이 검사할 입력 준비, 응답 유효성 확인, 최종 결과 구성 |
