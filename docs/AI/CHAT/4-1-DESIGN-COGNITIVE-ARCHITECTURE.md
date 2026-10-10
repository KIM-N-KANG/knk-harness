# 4-1 인지 구조 설계

본 문서는 태스크별 입력으로 결과를 만드는 판단과 생성 구조를 설계한다.

생성, 검사와 보완 단계를 나누고 각 단계에서 모델과 코드가 맡는 역할을 정한다.

<br>

### 4-1-1 서브태스크의 인지 구조

**1. 채팅 응답 생성**

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    A["<b>입력</b><br/>스토리 설정과 시작 설정<br/>대화 맥락, 사용자 입력<br/>사건과 엔딩 정보"] --> B["<b>본문 생성</b><br/>상황 설명과 주변 인물의 대사"]
    B -->|스트림 종료| D["<b>결과</b><br/>이번 턴의 본문"]
    B -->|호출 오류| E["<b>실패</b>"]
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    classDef check fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
    class A,D,E data
    class B task
```

- 엔딩 조건을 충족하면 해당 에필로그에 따라 결말을 쓴다.
- 안전성 기준에 따른 우회 서술은 본문 생성 프롬프트에서 처리하며 별도 검수 모델은 쓰지 않는다.
- 본문 생성에 실패하면 후속 작업을 하지 않는다.
- 본문 완성 후 판정과 이미지 처리를 병렬로 수행하고 선택지는 별도로 요청한다.
- 본문을 완성하고 표시할 이미지를 정한 뒤 이미지와 본문을 순서대로 전달한다.

<br>

**2. 사건과 엔딩 판정**

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    A["<b>입력</b><br/>사용자 입력, 이번 턴의 본문<br/>주요 사건과 판정 상태<br/>엔딩 후보"] --> B["<b>판정 대상 확인</b><br/>주요 사건 또는 엔딩 후보"]
    B -->|있음| C["<b>사건과 엔딩 판정</b><br/>모델 호출 1회"]
    C --> D["<b>형식과 이름 검사</b>"]
    D --> E["<b>결과</b><br/>목표 사건, 진행 턴 수<br/>완결된 사건, 도달한 엔딩"]
    B -->|없음| F["<b>생략</b>"]
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    classDef check fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
    class A,E,F data
    class C task
    class B,D check
```

- 목록에 없는 이름과 이미 완결된 사건은 해당 값만 비운다.
- 목표 사건이 이번 턴에 완결됐으면 목표 사건을 비운다.
- 엔딩 도달이 불확실하면 도달하지 않은 것으로 본다.
- 판정 결과가 비었거나 형식이 깨지면 실패로 처리한다.
- 남은 시간이 없거나 AI 서버의 판정 대기 한도를 넘으면 기존 목표와 진행 턴 수를 유지한다. 완결 사건과 도달 엔딩은 비운다.
- 공급자 시간 초과와 응답 파싱 실패는 판정값을 비우고 본문을 전달한다. 설정 오류와 내부 예외는 상위로 전파한다.

<br>

**3. 실시간 이미지 생성**

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    A["<b>입력</b><br/>이번 턴의 본문과 사용자 입력<br/>직전 대화, 인물 이미지 목록"] --> B["<b>대상 인물 선정</b><br/>기본 이미지가 있는 첫 화자"]
    B -->|있음| C["<b>실시간 이미지 생성</b><br/>대상 인물 1장"]
    C --> D["<b>이미지 확인</b>"]
    D -->|성공| E["<b>결과</b><br/>실시간 이미지"]
    D -->|실패| F["<b>기존 인물 이미지</b>"]
    B -->|없음| F
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    classDef check fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
    class A,E,F data
    class C task
    class B,D check
```

- 실시간 이미지는 요청된 턴에만 생성한다.
- 기본 이미지의 외형을 유지하며 본문과 대화 맥락에 맞는 표정과 상황을 그린다.
- 생성한 이미지만 대상 인물의 첫 대사 앞에 연결하고 다른 인물 이미지는 유지한다.
- 이미지 생성에 실패해도 재호출 없이 본문을 전달한다.

<br>

**4. 선택지 생성**

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    A["<b>입력</b><br/>스토리 설정, 대화 맥락<br/>이번 턴의 본문, 사건 정보"] --> B["<b>전체 생성</b><br/>선택지 3개"]
    B --> C["<b>형식, 개수와 중복 검사</b>"]
    C -->|부족| D["<b>추가 생성</b><br/>부족한 개수만"]
    D --> C
    C -->|3개 확보| E["<b>결과</b><br/>선택지 3개"]
    C -->|추가 생성 한도 소진| F["<b>대체 선택지로 채움</b>"]
    F --> E
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    classDef check fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
    class A,E data
    class B,D task
    class C,F check
```

- 주요 사건이 없거나 모두 완결됐으면 특정 사건으로 이끌지 않는다.
- 유효한 선택지는 유지하고 부족한 개수만 최대 2회 추가 생성한다.
- 선택지가 3개를 넘으면 앞의 3개만 남긴다.

<br>

**5. 저장 이미지 선택**

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    A["<b>입력</b><br/>대화 맥락과 인물별 이미지"] --> B["<b>화자와 후보 확인</b>"]
    B -->|복수 후보| C["<b>저장 이미지 선택</b><br/>인물별 질문을 한 번에 호출"]
    B -->|단일 후보| E["<b>선택 결과</b>"]
    C --> D["<b>응답 검사</b>"]
    D -->|정상| E
    D -->|실패| F["<b>기본 이미지 또는 첫 이미지</b>"]
    class A,E,F data
    class C task
    class B,D code
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    classDef code fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
```

- 실시간 이미지 OFF이면 대사한 인물의 저장 이미지를 후보로 삼는다.
- 후보가 여러 장인 인물의 질문을 묶어 모델을 한 번 호출한다. 모델은 대화와 이미지 이름으로 각 인물의 한 장을 고른다.
- 상황에 맞는 후보가 없으면 기본 이미지를 고르도록 지시한다.
- 코드의 응답 검사에 실패하면 해당 호출의 선택 결과 전체를 버리고 기본 이미지 또는 첫 이미지를 연결한다. 호출 없이 정한 단일 후보는 유지한다.

<br>

### 4-1-2 모델과 코드의 책임

코드는 사건 완결이나 엔딩 도달을 임의로 만들지 않는다.

본문 생성과 판정에는 별도 보완 호출을 하지 않는다.

| 맡는 쪽 | 맡는 일 |
|---|---|
| 모델 | 본문, 이미지와 선택지 생성 <br> 사건 진행과 완결, 엔딩 도달 판정 <br> 대화 맥락에 맞는 저장 이미지 선택 |
| 코드 | 프롬프트 구성, 형식과 이름 검사 <br> 이미지 후보와 화자 확인, 선택 결과 연결, 대체 선택지 적용 <br> 시간 한도 관리와 결과 조립 |
