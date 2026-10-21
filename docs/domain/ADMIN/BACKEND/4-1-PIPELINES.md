# 4-1 처리 흐름

이 문서는 ADMIN 도메인의 요청 수신부터 응답까지의 처리 단계와 다른 도메인의 관리자 API가 쓰는 판정과 감사 기록의 단계를 정한다.

요청 필드, 응답 필드와 실패 응답은 계약에, 토큰 수명과 복구 규칙은 오류 처리에, 트랜잭션 규칙은 동시성에 있다. ([4-2 계약](4-2-CONTRACT.md), [5-3 오류 처리](5-3-ERROR-HANDLING.md), [5-2 동시성](5-2-CONCURRENCY.md))

<br>

### 4-1-1 공통 처리

모든 요청은 상관관계 필터에서 요청 ID를 받는다. 관리자 로그인은 토큰을 읽지 않는다. 그 밖의 관리자 경로는 관리자 판정 필터가 요청자를 정한다. 앱 경로의 토큰 검증은 관리자 표식이 있는 토큰을 거절한다.

관리자 경로는 `/api/v1/admin/` 아래 전체다. 다른 도메인의 관리자 API도 같은 접두 아래에 두어 같은 필터를 거친다. 필터를 거치지 않는 관리자 경로는 없다.

관리자 판정은 토큰의 값으로 끝내지 않는다. 요청마다 토큰 주체의 회원 행을 읽어 관리자 역할과 계정 상태를 다시 확인한다.

흐름도에서 Google과 다른 도메인을 호출하는 단계는 주황색이다.

<br>

### 4-1-2 관리자 로그인

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**신원 증명 검증**
ACCOUNT 검증기, Google`"] --> B["`**활성 연동으로 회원 조회**
ACCOUNT`"]
    B --> C{"`**회원이 있고 활성이며
관리자 역할이 있는가**`"}
    C -->|아니오| X["`**거절**
사유 구분 없음`"]
    C -->|예| D["`**관리자 토큰 발급**
표식 포함`"]
    D --> E["`**응답**
토큰과 만료까지 남은 초`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class C,D,E,X comp
    class A,B task
```

- 검증 실패와 자격 없음은 다른 상태로 응답하되 자격 없음 안에서 회원 없음, 역할 없음, 정지, 탈퇴는 구분하지 않는다.
- 계정을 만들지 않고 가입 보상, 체험 스냅샷, 세션 생성, 로그인 분석 이벤트도 수행하지 않는다.
- 로그인 결과는 구조화 로그로 남긴다. 성공은 회원 공개 식별자를 기록하고 실패는 사유 분류만 기록한다.

<br>

### 4-1-3 관리자 판정

관리자 판정 필터는 `/api/v1/admin/` 아래에서 로그인을 제외한 모든 요청에 실행된다.

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A{"`**토큰이 있고 서명과 만료가
유효하며 관리자 표식이 있는가**`"} -->|아니오| X["`**인증 실패로 거절**`"]
    A -->|예| B["`**회원 조회**
ACCOUNT`"]
    B --> C{"`**활성 상태이고
역할 행이 있는가**`"}
    C -->|아니오| Y["`**권한 없음으로 거절**`"]
    C -->|예| D["`**요청자 확정**
핸들러로 전달`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,C,D,X,Y comp
    class B task
```

- 앱 접근 토큰은 표식이 없어 첫 단계에서 거절된다. 유효한 관리자 토큰이라도 그 사이 역할이 회수되거나 계정이 정지되면 두 번째 단계에서 거절된다.
- 요청자는 회원 내부 ID로 확정해 핸들러와 감사 기록에 전달한다.

<br>

### 4-1-4 감사 기록

다른 도메인의 관리자 API가 변경을 적용한 뒤 같은 트랜잭션에서 호출한다. ADMIN의 회원 검색과 상세는 조회 뒤 접속 기록으로 호출한다.

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**변경 적용**
호출 도메인의 트랜잭션`"] --> B["`**변경 전후 값 조립**
호출 도메인`"]
    B --> C["`**감사 로그 행 추가**
같은 트랜잭션`"]
    C --> D{"`**커밋**`"}
    D -->|성공| E["`**변경과 로그 확정**`"]
    D -->|실패| F["`**변경과 로그 모두 롤백**`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    class A,B,C,D,E,F comp
```

- 변경 전후 값은 호출 도메인이 응답 구조와 같은 필드로 조립한다. 생성은 변경 전 값이 없고 삭제는 변경 후 값이 없다.
- 대상은 외부 식별자로 기록한다. 순차 PK를 넣지 않는다.
- 접속 기록은 조회 응답을 만든 뒤 독립 트랜잭션으로 기록한다. 기록에 실패하면 조회 응답도 실패로 바꾼다.

<br>

### 4-1-5 대시보드 요약

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**현재 시각과 KST 오늘 범위 고정**`"] --> B["`**도메인별 집계 조회**
ACCOUNT, STORY, CHAT, PAYMENT, MODERATION`"]
    B --> C["`**응답 조립**
오늘과 누적`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,C comp
    class B task
```

- 지표 정의는 제품 제약을 따른다. ([2-4 제품 제약](2-REQUIREMENTS.md#2-4-제품-제약))
- 오늘 범위는 요청 시작 때 한 번 계산해 모든 집계에 같은 값을 쓴다. 자정을 걸치는 요청에서 지표끼리 기준이 어긋나지 않게 한다.
- 집계는 읽기 전용이며 캐시하지 않는다.
- 팀 계정 제외 목록은 설정에서 읽어 모든 집계의 소유 회원 조건에 적용한다. 회원 검색과 상세, 감사 로그 조회에는 적용하지 않는다.

<br>

### 4-1-6 결제 내역

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**페이지와 정렬 해석**
범위 밖은 거절`"] --> B["`**완료와 환불 주문 조회**
PAYMENT, 전체 건수와 현재 페이지`"]
    B --> C["`**주문 소유자 조회**
ACCOUNT`"]
    C --> D["`**응답 조립**
페이지 구조`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,D comp
    class B,C task
```

| 항목 | 규칙 |
|---|---|
| 대상 | 완료 시각이 있는 주문<br>대기 주문은 제외 |
| 정렬 | 요청한 열과 방향<br>같으면 주문 공개 식별자 오름차순 |
| 페이지 | 전체 건수 조회와 현재 페이지 조회를 각각 실행<br>건너뛸 행 수는 `(page - 1) × size` |

<br>

### 4-1-7 회원 검색과 상세

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A{"`**검색어가
UUID 형식인가**`"} -->|예| B["`**공개 식별자로 조회**
ACCOUNT`"]
    A -->|아니오| C["`**닉네임 부분 일치 조회**
ACCOUNT, 최대 20건`"]
    B --> D["`**요약 조립**`"]
    C --> D
    D --> E["`**접속 기록**
독립 트랜잭션`"]
    E --> F["`**응답**`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,D,E,F comp
    class B,C task
```

- 닉네임 검색은 대소문자와 공백을 무시한 정규화 키의 부분 일치다. 탈퇴 계정은 닉네임이 익명화되어 닉네임으로는 검색되지 않고 공개 식별자로만 검색된다.
- 상세는 요약에 잔액, 소유 스토리 수, 채팅 수, 가입 시각, 탈퇴 시각을 더한다. 잔액은 PAYMENT의 잔액 연산을 쓴다.
- 검색은 검색어를 대상으로 접속 기록을 남기고 상세는 회원 공개 식별자를 대상으로 접속 기록을 남긴다.

<br>

### 4-1-8 감사 로그 조회

```mermaid
%%{init: {"flowchart": {"curve": "basis", "nodeSpacing": 24, "rankSpacing": 40}}}%%
flowchart LR
    A["`**필터와 페이지 해석**`"] --> B["`**감사 로그 조회**
전체 건수와 현재 페이지`"]
    B --> C["`**처리자 표시 조립**
ACCOUNT, 닉네임과 공개 식별자`"]
    C --> D["`**응답**
페이지 구조`"]
    classDef comp fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class A,B,D comp
    class C task
```

- 정렬은 기록 시각이며 같으면 감사 로그 공개 식별자 오름차순이다. 페이지 규칙은 결제 내역과 같다.
- 감사 로그 조회 자체는 접속 기록을 남기지 않는다.
