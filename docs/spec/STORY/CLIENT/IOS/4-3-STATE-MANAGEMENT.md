# 4-3 상태 관리: iOS

기준: [공통 상태](../4-3-STATE-MANAGEMENT.md), [iOS 구성](4-2-COMPONENT-ARCHITECTURE.md).

<br>

### 4-3-1 화면과 저장 수명

Store와 화면 상태는 프로세스 종료 뒤 복원하지 않는다. 저장소별 귀속과 정리 원칙은 [IOS 기반 로컬 저장](../../../../platform/CLIENT/IOS/2-STATE-MANAGEMENT.md#2-4-로컬-저장)을 따른다.

| 상태 | 기준 |
|---|---|
| 홈 | Store의 섹션 목록. 섹션마다 가로 줄의 스크롤 위치는 화면 상태 |
| 탐색 | Store가 마지막으로 새로 섞은 순서와 커서를 메모리에 둔다. 앱 타깃이 다른 탭에서 탐색 탭을 고른 진입마다 진입 번호를 올리며 탐색 스택이 루트일 때만 새로 섞는다. 그리드 스크롤은 진입 번호별 화면 상태라 새 순서는 맨 위, 상세 복귀는 같은 위치 |
| 스토리 검색 | 입력 글자는 화면 상태, 제출한 검색어, 결과와 커서는 Store 메모리. 새 검색어마다 결과 번호를 올려 새 결과는 맨 위부터, 상세 복귀는 같은 위치 |
| 상세 | 선택, 채팅 생성, 좋아요, 채팅 시작 시트 열림과 펼친 행은 Store. 시트에서 페르소나 생성으로 떠난 표시는 Store 메모리에 두고 다음 화면 표시 때 한 번 소비한다. 이미지 뷰어 URL은 Store이며 저장소와 라우트에 넣지 않음 |
| 제작 옵션 | Store의 대상 카드. 조회로 대상이 없어지거나 상태가 바뀌면 갱신 |
| 인물 접기 | 인물 ID 집합과 삭제 확인 대상. 탭과 시작 상황 이동에 유지하지만 초안 payload와 API에는 제외 |
| 일반 폼 | Store의 MVI 상태. 탭, 접기와 자르기는 화면 상태 |
| 저장 충돌 | Store에 현재 충돌 version을 두어 사용자 선택까지 유지 |
| 화풍과 공개 | 추가 정보 상태와 진행 기록의 사본. 재선택과 재생성에도 유지 |
| 서버 초안 목록 | 마지막 성공 목록을 회원 ID와 함께 메모리에 보관. 같은 회원의 재조회 실패는 마지막 목록 유지 |

<br>

### 4-3-2 제작 데이터베이스

`ManyakCreate`만 앱의 Application Support 아래 `manyak.db`를 GRDB로 연다. 테이블은 세 개이며 모든 읽기와 쓰기는 현재 회원 ID 조건을 건다. 회원 ID는 프로필에서 받은 현재 회원의 ID이고 아직 없으면 읽기는 빈 결과, 쓰기는 실패로 끝나며 받으면 다시 읽는다. ([I-110](DECISIONS.md#i-110), [I-112](DECISIONS.md#i-112))

| 테이블과 키 | 열 |
|---|---|
| `pending_story_creation`<br>기본 키 `draftId` | `draftId`, `ownerId`, `stage`, `generationCommand`, `completionCommand`, `generation`, `progress`, `keywordSnapshot`, `createdAt`, `serverDraftVersion` |
| `story_completion_request`<br>기본 키 `requestId` | `requestId`, `ownerId`, `completionCommand`, `generationCommand`, `generation`, `progress`, `submittedAt`, `status`, `storyId`, `storyTitle`, `createdAt`, `serverDraftVersion` |
| `general_story_draft`<br>기본 키 `ownerId`, `draftId` | `ownerId`, `draftId`, `acceptedSubmissionId` |

| 열 | 형식과 의미 |
|---|---|
| `ownerId` | 필수 TEXT. 소유 회원 ID. 빈 값으로 쓰지 않음 |
| `stage` | 필수 TEXT. `KEYWORD_DRAFT`(기기 세션의 키워드 입력), `STORYLINE_GENERATION`(생성 중), `STORY_DRAFT`(생성 결과와 추가 정보) |
| `status` | 필수 TEXT. `PENDING` 또는 `COMPLETED` |
| `generationCommand` | 선택 JSON. [스토리라인 생성 요청](../4-1-CONTRACT.md#4-1-2-간편-제작-요청) 전체와 requestId, parentCreationId. `STORY_DRAFT`에서는 재시도용 마지막 요청 |
| `completionCommand` | JSON. 완성 요청 전체와 requestId. 요청 행은 필수, 편집 행은 확정 실패에서 되돌린 원 명령일 때만 |
| `generation` | JSON. 생성 결과의 simpleCreationId, 스토리라인 세 개와 추천 정보. 요청 행은 필수 |
| `progress` | JSON. [STORY_DRAFT payload](../4-1-CONTRACT.md#4-1-5-간편-제작-payload-v1)의 단계, 선택 스토리라인, 추가 정보, 추천 선택, 화풍과 공개 범위. 요청 행은 필수 |
| `keywordSnapshot` | 선택 JSON. KEYWORD_DRAFT payload와 같은 키워드 입력 |
| `createdAt` | 선택 INTEGER. 처음 행을 만들거나 서버 초안에서 이어받은 최초 저장 시각(Unix epoch 밀리초). 다시 써도 바꾸지 않음 |
| `submittedAt` | 필수 INTEGER. 완성을 제출한 시각. `createdAt`과 같은 단위 |
| `serverDraftVersion` | 선택 INTEGER. null은 기기 세션, 0은 서버에 아직 저장한 적 없는 서버 세션, 그 밖은 기록 당시의 서버 기준 version |
| `acceptedSubmissionId` | 필수 TEXT. 일반 제작 202 접수의 submissionId |

JSON 열은 읽을 때 모르는 키를 무시하고 없는 키는 기본값으로 채운다. 해석하지 못한 행은 지우지 않고 카드와 세션에서 제외한다. 날짜 없는 행은 뒤로, 나머지는 `createdAt` 내림차순으로 읽고 완성 요청은 `submittedAt`도 내림차순으로 쓴다. 로그아웃은 세 테이블을 지우지 않고 행은 소유 회원별로 남는다. 세 테이블은 `UserScopedStore`에 등록하지 않는다. 탈퇴가 성공하면 중앙 종료를 시작하기 전에 그 회원이 소유한 세 테이블의 행을 지운다. 삭제 실패는 탈퇴와 종료를 막지 않고 남은 행은 회원 ID 격리로 다른 회원에게 보이지 않는다. ([I-122](DECISIONS.md#i-122))

일반 제작 입력은 서버 초안에만 둔다. `general_story_draft`는 접수한 draftId를 남겨 그 ID의 늦은 저장을 거절하고 카드에서 제외하며 같은 ID를 다시 쓰지 않게 한다. 진입은 접수 연결, 서버 상세 순서다.

<br>

### 4-3-3 간편 제작 세션

1. draftId를 모든 단계에 전달하고 세션 객체가 해당 ID를 맡는다. 새 제작은 새 UUID로 서버 세션을 열고 서버 상세를 조회하지 않는다. ([I-113](DECISIONS.md#i-113))
2. 카드로 재개하면 기기 행이 있을 때 그 행을 먼저 쓴다. `serverDraftVersion`이 있으면 서버 세션, 없으면 기기 세션이다. 행이 없으면 서버 상세를 확인하고 서버 세션으로 정한다. 조회 실패 때는 판정을 끝내지 않는다.
3. 서버 세션의 키워드는 서버에만 저장하고 입력이 모두 비면 삭제한다. 생성 중과 결과는 기준 version과 함께 기기에 보관하며 서버에 아직 없으면 기준 0이다.
4. 사용자 저장이 성공하면 세션의 기기 행을 제거한다. 결과 직후 기기 행은 이미 저장된 것으로 보아 변경 없이 백그라운드로 가도 서버에 새로 쓰지 않는다.
5. 표시 결과를 만든 요청과 재시도용 마지막 요청을 따로 보존한다. 스토리라인 선택은 서버 ID로 쓰고 복원할 때 순번으로 되돌린다.
6. 연결된 서버 version이 기기 기준 이하이면 서버 카드를 가린다. 새 서버 카드는 별도 키와 재개 및 삭제를 쓴다.
7. 새 서버 카드로 재개할 때 같은 ID의 기기 행은 새 UUID로 옮기고 서버 연결을 버려 기기 초안으로 보존한다.
8. 완성 요청 행은 draftId와 서버 연결 및 최초 시각을 이어받는다. 확정 실패는 원 명령의 draftId에 추가 정보 초안으로 복원한다.
9. 세션 결과와 기기 행 쓰기는 `SessionGate`의 세대를 확인한 뒤에만 반영해 로그아웃 뒤 늦은 결과가 다른 회원에 남지 않게 한다.

<br>

### 4-3-4 장르, 기기 기록과 가입 안내

장르 검색은 화면 Store 수명으로 전체 카탈로그와 검색 결과를 보관한다. 빈 결과도 성공 캐시에 포함하고 최대 20개에서 가장 먼저 받은 항목부터 제거하며 실패는 보관하지 않는다. 메뉴를 닫으면 검색과 로딩 타이머만 취소하고 대표 칩에 필요한 전체 카탈로그는 완료할 수 있다. 선택 ID와 추가 칩 순서는 초안 payload에 보존하고 누락 필드는 빈 목록으로 읽는다. 카탈로그와 초안 중 어느 쪽이 먼저 와도 대표 항목은 대표 위치로 정리하되 선택을 유지한다.

| UserDefaults 키 | suite와 값 |
|---|---|
| `recent_story_searches` | 기기 suite. 앞뒤 공백을 뺀 검색어의 최신순 문자열 배열, 최대 10개. 같은 문자열은 맨 앞으로 옮긴다. 읽거나 쓰지 못하면 남기지 않고 빈 목록으로 본다 |
| `create_tutorial_stage` | 기기 suite. 마지막으로 마친 단계 `intro`, `keyword`, `storyline`, `additional-info`, `completing` 또는 전체 완료 `done` |
| `story_onboarding_pending` | 회원 suite. 신규 가입이면 true, 완료하면 지움. 없으면 온보딩 없음 |

가입 온보딩 저장소는 `UserScopedStore`로 등록해 로그아웃 정리에서 표시와 같은 실행의 메모리 완료를 함께 지운다. 회원 루트는 표시를 읽기 전에 메인 셸을 그리지 않고 읽기 실패는 온보딩 없음으로 처리한다. 완료는 메모리 완료를 먼저 남긴 뒤 표시를 지워 저장 실패가 같은 실행에서 온보딩을 다시 열지 않게 한다. 저장 실패 뒤 다음 실행에서는 온보딩이 다시 열린다.

<br>

### 4-3-5 제작 안내

| 상태 | 기준 |
|---|---|
| 진행 기록 | 기기 suite의 `create_tutorial_stage`. `UserScopedStore`에 참여하지 않음 |
| 다음 단계 | 절차가 처음 한 번 읽고 마칠 때마다 메모리에서 바로 바꾼다. 기록이 없거나 읽지 못하면 인사, 알 수 없는 값이면 없음 |
| 열린 단계 | 화면 Store가 가진 절차의 상태. 테마와 글자 크기 변경, 백그라운드 복귀에 유지하고 프로세스 종료에는 남기지 않는다 |
| 기록 쓰기 | 버튼과 VoiceOver 닫기 동작으로 닫을 때만 쓴다. 닫자마자 화면을 떠나도 쓰기를 취소하지 않고 실패는 다음 진입에 같은 단계를 다시 여는 것으로 끝낸다 |
