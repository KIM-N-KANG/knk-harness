# 4-1 처리 흐름

이 문서는 NOTICE 도메인의 요청 수신부터 응답까지의 처리 단계를 정한다.

요청 필드, 응답 필드와 실패 응답은 계약에, 복구 규칙은 오류 처리에, 잠금과 알림 1회성은 동시성에 있다. ([4-2 계약](4-2-CONTRACT.md), [5-3 오류 처리](5-3-ERROR-HANDLING.md), [5-2 동시성](5-2-CONCURRENCY.md))

<br>

### 4-1-1 공통 처리

모든 요청은 상관관계 필터에서 요청 ID를 받는다. 공개 조회는 토큰을 읽지 않는다. 관리자 경로는 관리자 판정 필터가 요청자를 정하고 통과하지 못하면 거절한다.

상태를 바꾸는 관리자 작업은 공지 행에 비관적 잠금을 건 뒤 상태를 다시 확인한다. 변경을 적용한 뒤 같은 트랜잭션에서 감사 기록을 호출한다.

흐름도에서 다른 도메인을 호출하는 단계는 주황색이다.

<br>

### 4-1-2 공개 목록과 상세

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A{"`**요청**`"} -->|목록| B["`**커서 해석**
형식 오류는 거절`"]
    B --> C["`**게시된 공지 조회**
게시 시각 내림차순, 페이지 크기 + 1건`"]
    C --> D["`**응답**
제목과 게시 시각, 다음 커서`"]
    A -->|상세| E["`**공개 식별자로 조회**`"]
    E --> F{"`**게시 상태인가**`"}
    F -->|아니오| X["`**없는 것으로 응답**`"]
    F -->|예| G["`**응답**
제목, 본문, 게시 시각`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    class A,B,C,D,E,F,G,X comp
```

- 목록은 본문을 싣지 않는다. 정렬은 게시 시각 내림차순이며 같으면 내부 ID 내림차순이다. 커서는 마지막 항목의 게시 시각과 내부 ID를 담은 불투명 문자열이다.
- 상세는 없는 공지와 초안을 같은 결과로 응답한다.

<br>

### 4-1-3 작성과 수정

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A{"`**요청**`"} -->|작성| B["`**초안 행 생성**
작성 관리자 기록`"]
    A -->|수정| C["`**공지 행 잠금**`"]
    C --> D["`**제목과 본문 덮어쓰기**
보낸 필드만`"]
    B --> E["`**감사 기록**
ADMIN, 같은 트랜잭션`"]
    D --> E
    E --> F["`**응답**
관리자 공지 구조`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,B,C,D,F comp
    class E task
```

- 수정은 상태와 무관하게 허용한다. 게시된 공지의 수정은 공개 조회에 바로 반영되고 알림을 다시 보내지 않는다.
- 감사 기록의 변경 전후 값은 제목과 상태다. 본문은 변경 전후 값의 길이 상한을 넘을 수 있어 넣지 않는다.

<br>

### 4-1-4 게시

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**공지 행 잠금**`"] --> B{"`**초안인가**`"}
    B -->|아니오| X["`**거절**`"]
    B -->|예| C["`**게시 상태로 전환**
게시 시각 기록`"]
    C --> D{"`**알림을 요청했고
요청한 적이 없는가**`"}
    D -->|예| E["`**공지 발송 요청**
NOTIFICATION, 같은 트랜잭션`"]
    E --> F["`**알림 요청 시각 기록**`"]
    D -->|아니오| G["`**감사 기록**
ADMIN`"]
    F --> G
    G --> H["`**응답**
알림 요청 여부 포함`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,B,C,D,F,H,X comp
    class E,G task
```

| 항목 | 규칙 |
|---|---|
| 알림 요청 입력 | 공지 공개 식별자, 제목, 본문 앞 300자(줄바꿈은 공백), 유형, 딥링크 |
| 딥링크 | 운영 웹 주소에 `/notices/{공지 공개 식별자}`를 붙인 값 |
| 유형 | `SERVICE`는 정보성<br>`MARKETING`은 광고성<br>알림 도메인이 유형별 대상과 표기를 정함 |
| 1회성 | 알림 요청 시각이 이미 있으면 알림을 요청하지 않고 응답의 알림 요청 여부를 `false`로 함 |
| 실패 | 알림 요청 기록에 실패하면 게시도 롤백 |

<br>

### 4-1-5 게시 해제

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**공지 행 잠금**`"] --> B{"`**게시 상태인가**`"}
    B -->|아니오| X["`**거절**`"]
    B -->|예| C["`**초안으로 전환**
게시 시각은 유지`"]
    C --> D["`**감사 기록**
ADMIN`"]
    D --> E["`**응답**`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,B,C,E,X comp
    class D task
```

- 이미 기록된 알림 요청은 취소하지 않는다. 캠페인의 취소는 알림 도메인의 캠페인 취소로 한다.

<br>

### 4-1-6 초안 삭제

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**공지 행 잠금**`"] --> B{"`**초안이고 알림을
요청한 적이 없는가**`"}
    B -->|아니오| X["`**거절**`"]
    B -->|예| C["`**물리 삭제**`"]
    C --> D["`**감사 기록**
ADMIN, 변경 전 값만`"]
    D --> E["`**응답**`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,B,C,E,X comp
    class D task
```

<br>

### 4-1-7 관리자 목록과 상세

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**상태 필터와 페이지 해석**`"] --> B["`**공지 조회**
전체 건수와 현재 페이지`"]
    B --> C["`**작성자 표시 조립**
ACCOUNT`"]
    C --> D["`**응답**
관리자 공지 구조`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,B,D comp
    class C task
```

- 관리자 목록은 상태와 무관하게 조회하고 요청한 열로 정렬한다. 같은 값은 공지 공개 식별자 오름차순이다. 관리자 조회는 감사 로그에 남기지 않는다.
