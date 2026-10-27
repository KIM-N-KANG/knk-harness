# 5-5 테스트 케이스

이 문서는 ADMIN 도메인 코드의 계약과 오류 처리 규칙을 검증할 테스트 범위, 입력과 상황, 기대 결과를 정한다.

실행 명령과 수동 호출 파일 위치는 AGENTS.md에 있으며 기대 결과의 상태 코드는 계약에 있다. ([AGENTS.md](AGENTS.md)와 [4-2 계약](4-2-CONTRACT.md))

<br>

### 5-5-1 테스트 범위

| 종류 | 확인 범위 | 외부 호출 | 실행 |
|---|---|---|---|
| 단위 | 관리자 토큰 발급과 검증, 표식 판정, KST 오늘 범위 계산, 페이지와 정렬 해석, 설치 보고서 CSV 해석과 합산, 인프라 지표의 집계 간격 판정과 단위 변환과 건수 0 채움 | 없음 | CI |
| 통합 | 로그인, 판정 필터, 감사 기록, 대시보드 요약과 차트, 스토리, 채팅, 회원, 결제 목록과 상세, 이프 내역, 감사 로그 조회, 분석 지표, 캠페인 분석, 사용자와 전환과 기능 지표, Amplitude 값 저장, 설치 지표, 인프라 지표, DB 테이블 크기 | 신원 검증기는 고정 신원을 돌려주는 구성으로 대체<br>분석 도구, 보고서 저장소, CloudWatch와 ECS는 고정 응답을 돌려주는 대역으로 대체<br>DB 테이블 크기의 카탈로그 조회는 대역으로 대체 | CI<br>H2, 스키마 자동 생성, 마이그레이션 비활성 |
| 회귀 | 등록된 모든 관리자 경로의 인증과 권한 거절 | 없음 | CI |
| 수동 | 엔드포인트 호출 | 실행 환경의 실제 의존성 | 서버 저장소의 HTTP 요청 파일 |

테스트 프로파일은 마이그레이션을 건너뛴다. 전체 테스트를 통과해도 DB 제약을 검증했다고 볼 수 없다. DB 테이블 크기의 카탈로그 쿼리는 H2에 없는 PostgreSQL 함수를 쓰므로 통합 테스트는 조회 계층을 대역으로 바꾸고 실제 쿼리는 로컬 PostgreSQL에 붙인 HTTP 요청 파일로 확인한다.

**외부 의존성과 테스트 데이터**

| 대상 | 방법 |
|---|---|
| Google | 통합 테스트는 고정 신원을 돌려주는 검증기를 등록 |
| DB | 통합 테스트는 공유 H2의 PostgreSQL 모드<br>CHECK 제약은 실제 PostgreSQL에서 DB 문서 생성 스크립트로 검증 |
| 시각 | 주입한 고정 시계로 토큰 만료와 KST 자정 경계 검증 |
| 회원 데이터 | 관리자 역할이 있는 활성, 정지, 탈퇴 계정과 역할 없는 활성 계정 준비 |
| 공식 계정 | 설정값에 테스트 회원의 공개 식별자를 넣어 오리지널 범위 검증 |
| Amplitude | 사용자 수, 세분화, 퍼널, 리텐션, 세션 조회 요청을 받아 고정 JSON을 돌려주는 대역<br>요청 수, 순서, 쿼리를 기록 |
| Redis | 배치 슬롯 선점을 성공, 이미 선점됨, 예외로 돌려주는 대역 |
| Google Cloud Storage | 객체 목록과 내려받기를 고정 바이트로 돌려주는 대역<br>UTF-16LE로 인코딩한 뒤 gzip으로 압축한 월별 CSV 2개 이상 |
| AWS CloudWatch, ECS | `GetMetricData`와 `DescribeServices` 요청을 받아 고정 응답이나 AWS 오류 코드를 돌려주는 대역<br>요청의 질의 목록, 통계, 차원, 시각, 간격을 기록 |

<br>

### 5-5-2 관리자 로그인과 토큰

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 로그인 | 역할 있는 활성 회원의 유효 증명 | 200, `expiresIn` 7200, `admin.isAdmin` true, 성공 로그 |
| 자격 없음 | 역할 없는 회원, 역할 있는 정지 회원, 역할 있는 탈퇴 회원, 회원 없는 신원 | 전부 403, 같은 `message`, 거절 로그의 `reason` 4종 |
| 증명 오류 | 서명 불일치<br>만료 | 401 |
| 부수효과 없음 | 회원 없는 신원 | 계정, 세션, 보상, 로그인 분석 이벤트 없음 |
| 토큰 클레임 | 발급된 토큰 | 대상 `manyak-admin`, 주체는 회원 공개 식별자, 만료는 발급 뒤 2시간 |
| 앱 필수 경로 | 관리자 토큰으로 세션 조회 호출 | 401 |
| 앱 선택 경로 | 관리자 토큰으로 정책값 조회와 공개 스토리 목록 호출 | 200, 익명 처리 |
| 앱 토큰 미조회 경로 | 관리자 토큰을 첨부한 앱 로그인 | 헤더 무시하고 처리 |
| 관리자 경로 거절 | 앱 접근 토큰으로 대시보드 호출 | 401 |
| 만료 | 2시간 뒤 대시보드 호출 | 401 |

<br>

### 5-5-3 권한 판정과 회귀

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 모든 관리자 경로 | 등록된 핸들러 매핑에서 `/api/v1/admin/` 접두 경로를 자동 수집해 로그인을 제외한 전부를 토큰 없이 또는 일반 회원의 앱 접근 토큰으로 호출 | 전부 401<br>수집된 경로 수가 1 이상 |
| 역할 회수 | 유효한 관리자 토큰<br>역할 행 삭제 뒤 호출 | 403 |
| 정지 | 유효한 관리자 토큰<br>계정 정지 뒤 호출 | 403 |
| 탈퇴 | 유효한 관리자 토큰<br>탈퇴 뒤 호출 | 403 |
| 요청자 확정 | 변경 API 호출 | 감사 로그 처리자가 토큰 주체 |

<br>

### 5-5-4 감사 기록

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 변경 기록 | 다른 도메인의 변경 API 성공 | 변경과 같은 트랜잭션에 로그 1행, 작업 이름, 대상 식별자, 사유, 전후 값, 요청 ID |
| 기록 실패 | 감사 로그 삽입 예외 | 변경도 롤백<br>500 |
| 트랜잭션 없음 | 트랜잭션 밖에서 변경 기록 호출 | 거부 |
| 접속 기록 | 검색어 있는 회원 목록<br>회원 상세 | `MEMBER_SEARCHED`와 정규화한 검색어, `MEMBER_VIEWED`와 회원 공개 식별자, 사유와 전후 값 없음 |
| 전후 값 범위 | 이프 지급과 계정 정지 | `before`와 `after`에 기록 허용 필드만 있고 이메일, 닉네임, 소셜 식별자 없음 |
| 접속 기록 실패 | 삽입 예외 | 500<br>조회 데이터 대신 공통 실패 응답 본문 |
| 요청 ID 길이 | 64자 헤더로 변경 API, 65자 헤더로 변경 API | 감사 로그 `request_id`가 헤더 값, 감사 로그와 응답 헤더가 같은 서버 생성 값 |
| 멱등 재시도 | 같은 멱등 키의 지급 재요청 | 로그 추가 없음 |
| 조회 필터 | 처리자, 작업 이름, 대상 종류와 식별자, `category`, `from`과 `to`, 사유 일부 `q` | 조건에 맞는 행만 최신순 |
| 조회 정렬 | `sort=admin&order=asc` | 처리자 닉네임 오름차순<br>같으면 감사 로그 공개 식별자 오름차순 |
| 필터 오류 | `targetId`만 지정, UUID 아닌 `adminId`, `category=READ`, `sort=reason` | 400 |

<br>

### 5-5-5 대시보드 요약과 차트

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 누적 가입자 수 | 활성 2, 정지 1, 탈퇴 1, 팀 계정 제외 목록의 회원 1 | `members.total` 4, `active` 3, `withdrawn` 1<br>`total`이 `active`와 `withdrawn`의 합 |
| 오늘 경계 | KST 23:59에 가입한 회원과 00:01에 가입한 회원<br>00:30 조회 | `joinedToday` 1 |
| 턴 수 | AI 응답 메시지 3개<br>그중 하나에 판본 2개 | `turnsTotal` 3 |
| 이프 적립과 소모 | 출석 250, 구매 5000, 관리자 지급 100, 채팅 턴 -20, 만료 -30, 환불 +20 | `grantedTotal` 5350<br>`spentTotal` 20 |
| 결제 | 완료 1건 4800<br>환불 1건 2000 | `completedTotal` 2, `amountKrwTotal` 6800 |
| 응답 범위 | 요약 응답 | 환불, 검수 보류 필드 없음<br>`members.active`와 `members.withdrawn`이 있음 |
| 기준 시각 | 응답 | `asOf`와 `todayStartsAt`이 같은 시계 기준 |
| 팀 계정 제외 | 제외 목록의 회원 1명과 일반 회원 1명이 각각 가입, 채팅 시작, 턴 1개, 스토리, 출석 보상, 결제 완료<br>게스트 채팅 1건 | 요약과 차트의 모든 지표가 일반 회원과 게스트 행만 집계<br>회원 목록에는 팀 계정이 보임 |
| 제외 목록 비움 | 설정값 빈 값 | 제외 없이 전부 집계 |
| 차트 기간 | `days` 7, 생략, 90, 10 | `daily` 7개, 30개, 90개, 400 |
| 차트 날짜 범위 | `from=2026-01-01&to=2026-01-31`<br>`from`과 `to` 366일<br>367일, `from` > `to`, `to` 내일, `from`만, `days`와 함께 | `daily` 31개와 응답 `from`, `to` 그대로, 막대 링크의 날짜도 같음<br>366개<br>전부 400 |
| 빈 날짜 | 범위 중 활동 없는 날 | 그 날짜 항목이 모든 값 0으로 존재 |
| 일별 출석 | 한 회원이 같은 날 출석 보상 1건, 다른 회원 1건 | `attendance` 2 |
| 턴 수 분포 | 현재 턴 0, 1, 4, 5, 6, 7, 50인 채팅 | `turns` 차트의 `0`, `1`, `4`, `5`, `6`, `7~9`, `50+`가 각 1이고 나머지 구간 0<br>항목 13개 |
| 장르별 평균 턴 수 | 장르 `판타지, 미스터리` 스토리의 채팅 2개(턴 2, 4) | `판타지`와 `미스터리` 막대 모두 `value` 3, `chats` 2, `totalTurns` 6 |
| 장르 순서와 소표본 | `던전` 채팅 1개(턴 465), `로맨스` 채팅 6개(턴 합 60) | 점 순서 `던전`(465, `chats` 1), `로맨스`(10, `chats` 6)<br>채팅이 1개인 장르도 응답에 있음 |
| 게스트 비율 | 게스트 채팅 1, 회원 채팅 3 | `게스트` 25, `회원` 75 |
| 회원별 채팅 | 회원 A 채팅 1, 회원 B 채팅 5 | `1개` 1, `5~9개` 1 |
| 첫 메시지 시간 | 첫 사용자 메시지가 30초, 60초, 1000초인 채팅과 메시지 없는 채팅 | `평균` 45<br>`description`에 900초 초과 1과 입력 없음 1 |
| AI 지연과 성공률 | `chat_response` 성공 2(지연 1초, 3초), 실패 1, 진행 중 1 | `ai-latency`의 `chat_response` 2<br>`ai-success`의 `chat_response` 66.67 |
| 실시간 이미지 AI 지표 | `chat_image` 성공 2(지연 4초, 지연 없음 1), 실패 2, 팀 계정 채팅의 성공 1 | `ai-latency`의 `chat_image` 4<br>`ai-success`의 `chat_image` 50, 팀 계정 채팅 제외<br>두 차트 항목 순서가 `chat_response`, `choice_generation`, `chat_image`, `storyline_generation`, `story_completion` |
| 간편 제작별 입력 주변 인물 수 | 주변 인물 행 없는 세션, 입력한 주변 인물 2명 세션<br>공식 계정의 세션 1건 | `0명` 1, `2명` 1<br>공식 계정 세션 포함 |
| 빈 자리 인물 제외 | 주변 인물 행 3개 중 이름만 있는 1개, 특징 태그만 연결된 1개, 이름, 성별, 태그가 모두 빈 1개 | `2명` 1<br>스토리 목록 `supportingCharacterCount=2`에 그 스토리 포함 |
| 제작 세션 팀 제외 | 공식 계정이 아닌 제외 목록 회원의 세션 | 집계에서 제외 |
| 차트 구역 | 분포 차트 8개 | `category`가 `users` 2개, `engagement` 3개, `content` 1개, `ai-quality` 2개 |
| 막대 링크 | `turns` 차트 둘째 막대 | `link.list` `chats`, `params.turnBucket` `1`, `from`과 `to`가 응답의 `from`, `to`와 같음 |
| 링크 삭제 필터 | 범위 안에 같은 턴 구간의 삭제된 채팅 1개와 삭제되지 않은 채팅 2개<br>그 구간 막대의 `link`로 목록 호출 | 모든 막대의 `link.params`에 `deleted` 없음<br>목록 `totalElements` 2이고 삭제된 채팅 없음 |
| 링크 일치 | 건수 차트 막대의 `link`로 목록 호출(팀 계정과 삭제 행 없는 데이터)<br>`genre-depth`, `started-as`, `first-message` 막대의 `link`로 목록 호출<br>`ai-latency`, `ai-success` 막대의 `link`로 목록 호출 | 목록 `totalElements`가 막대 `value`와 같음<br>목록 항목이 막대 산식의 대상과 같고 그 항목으로 산식을 계산하면 `value`와 같음<br>목록이 조건에 맞는 호출 기록이 하나 이상 연결된 스토리나 채팅과 정확히 같음<br>AI 차트 값은 호출 단위라 목록 항목으로 재계산하지 않음 |

<br>

### 5-5-6 스토리와 채팅

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 스토리 범위 | 공식 계정 스토리 1, 회원 스토리 1, 게스트 스토리 1 | `scope=original` 1건, `scope=user` 2건, 게스트 스토리의 `owner` `null` |
| 공식 계정 미설정 | 설정값 빈 값 | `scope=original` 0건 |
| 장르 필터 | `genre=판타지` | 장르 문자열에 판타지가 있는 스토리만 |
| 태그와 인물 수 | 제작 세션으로 완성한 스토리와 일반 등록 스토리<br>세션에 빈 자리 인물 1개 포함 | 태그 배열과 빈 자리를 뺀 `supportingCharacterCount`<br>일반 등록은 빈 배열과 `null` |
| 보류 상태 | 보류 제출본 있는 스토리<br>대기 제출본만 있는 스토리 | `HELD`<br>`APPROVED` |
| 채팅 기간 | `chatFrom`, `chatTo` 안에 채팅 1건, 밖에 2건인 스토리와 기간에 채팅 없는 스토리 | `chatCount` 1, `totalTurns`는 그 채팅의 턴<br>채팅 없는 스토리 제외 |
| AI 호출 필터 | `aiFeature=story_completion&aiStatus=FAILED` | 실패 기록이 연결된 스토리만 |
| 이미지 호출 필터 | 채팅 목록 `aiFeature=chat_image&aiStatus=FAILED` | 실패한 `chat_image` 기록이 연결된 채팅만 |
| 스토리 검색 | 제목 일부, 소유자 닉네임 일부, 스토리 공개 식별자 | 각각 일치하는 스토리 |
| 삭제 필터 | 삭제된 스토리 1, 삭제되지 않은 스토리 2<br>`deleted` 없음, `include`, `only` | 2건, 3건, 1건<br>삭제된 스토리의 `deletedAt`은 삭제 시각이고 나머지는 `null` |
| 범위 목록 삭제 필터 | 회원 A의 삭제된 스토리 1과 삭제되지 않은 스토리 1, 다른 회원의 삭제된 스토리 1<br>`memberId`가 A이고 `deleted=only` | 회원 A의 삭제된 스토리 1건 |
| 삭제 필터 오류 | 스토리 목록 `deleted=all`과 `deleted=exclude`<br>채팅 목록 `deleted=INCLUDE` | 400 |
| 삭제 스토리 상세 | 삭제된 스토리의 상세 | 200<br>`deletedAt`이 삭제 시각 |
| 공개 중단 표시 | 공개 중단된 스토리와 그렇지 않은 스토리의 목록과 상세 | 앞 스토리만 `takenDownAt`과 `takedownReason`, 나머지는 셋 다 `null`<br>`ETC`로 공개 중단된 스토리만 `takedownReasonDetail` |
| 삭제 스토리 집계 | 삭제된 스토리에 삭제되지 않은 채팅 2개(턴 3, 5)와 삭제된 채팅 1개(턴 10) | `deleted=include` 목록 항목과 상세의 `chatCount` 2, `totalTurns` 8<br>`retention`은 두 채팅으로 계산하고 `recentChats`는 삭제되지 않은 채팅 2개 |
| 기준 턴 도달률 | 채팅 턴 0, 1, 5, 12 | 항목 12개가 `turn` 1, 2, 3, 4, 5, 6, 7, 10, 15, 20, 30, 50 순서<br>`turn` 1은 0.75, 2부터 5까지 0.5, 6부터 10까지 0.25, 15 이상은 0 |
| 최근 채팅 | 채팅 7개 | `recentChats` 5개 생성 시각 내림차순 |
| 스토리 설정 | 다른 회원이 소유한 `DRAFT`, `PRIVATE` 스토리<br>제목과 본문에 `{username}`, 통글 4필드, 시작 설정 2개(추천 입력 3개, 엔딩 1개와 0개), 주요 사건 2개, 인물 2명 | 200<br>모든 텍스트 필드가 저장값 원문 그대로이고 `{username}`이 치환되지 않음<br>시작 설정은 등록 순서, 주요 사건은 `sortOrder` 순서, 인물은 저장 순서 |
| 스토리 설정 이미지 | 표지 `PENDING`<br>인물 하나에 `APPROVED`, `PENDING`, `REJECTED` 이미지 각 1장 | `thumbnailUrl`이 그 표지 URL이고 `thumbnailModerationStatus` `PENDING`<br>`images` 3장 전부가 표시 순서로 있고 각 `moderationStatus`가 저장값 |
| 스토리 설정 빈 값 | 설정 행, 시작 설정, 주요 사건, 인물이 없는 스토리 | `storySettings` 네 필드 모두 `null`<br>`startSettings`, `mainEvents`, `characters` 빈 배열 |
| 오리지널 설정 | 공식 계정이 소유한 스토리 | 200<br>오리지널 상세의 수정 폼 필드와 같은 값 |
| 게스트 스토리 설정 | 소유자가 없는 스토리 | 200 |
| 승인 전 제출본 | 대기 상태의 수정 제출본이 있는 스토리 | 제출본의 값이 아니라 현재 저장값 |
| 스토리 설정 응답 범위 | 반려된 수정 제출본이 있는 스토리 | 응답에 `submission`과 `characters[].images[].objectKey` 필드가 없음 |
| 삭제 스토리 설정 | 삭제된 스토리 | 200<br>삭제 전 저장값 그대로이고 `deletedAt`이 삭제 시각 |
| 스토리 설정 대상 없음 | 없는 UUID<br>UUID 아닌 `storyId` | 404<br>400 |
| 스토리 설정 권한 | 일반 회원의 앱 접근 토큰<br>역할 없는 회원의 관리자 표식 토큰 | 401<br>403 |
| 스토리 설정 접속 기록 | 스토리 설정 조회 성공 | 감사 로그 행 없음 |
| 채팅 게스트 여부 | 게스트 채팅<br>이관된 채팅 | `GUEST`<br>`MEMBER` |
| 턴 구간 필터 | `turnBucket=12`<br>`turnBucket=5`와 `6` | 현재 턴 50 이상만<br>각각 현재 턴 5만, 6만 |
| 첫 메시지 필터 | `hasFirstMessage=true`<br>`false` | 900초 이내 메시지 있는 채팅<br>초과와 없는 채팅 |
| 턴 날짜 | `turnDate`에 AI 응답이 있는 채팅과 그 전날만 있는 채팅 | 전자만 |
| 이프 소모 | 채팅 턴 -20 두 건과 이미지 -5 한 건을 참조하는 채팅 | `creditsSpent` 45 |
| 원문 없음 | 채팅 목록과 상세 응답 | 메시지, 요약, 추천 입력, 페르소나 필드 없음 |
| 채팅 검색 | 스토리 제목 일부, 회원 닉네임 일부, 채팅 공개 식별자 | 각각 일치 |
| 채팅 삭제 필터 | 삭제된 채팅 1, 삭제되지 않은 채팅 2, 삭제된 스토리의 삭제되지 않은 채팅 1<br>`deleted` 없음, `include`, `only` | 3건(삭제된 스토리의 채팅 포함), 4건, 1건 |
| 범위 목록 채팅 삭제 필터 | 스토리 S의 삭제된 채팅 1과 삭제되지 않은 채팅 1<br>`storyId`가 S이고 `deleted=include` | 2건 |
| 삭제 채팅 상세 | 삭제된 채팅의 상세 | 200<br>`deletedAt`이 삭제 시각이고 메시지 원문 필드 없음 |
| 필터 오류 | `startedAs=BOT`, `from=2026-13-01`, `from` > `to`, UUID 아닌 `storyId` | 400 |

<br>

### 5-5-7 회원과 결제

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 닉네임 검색 | `등대`, `  등대  `, `EQUAL`와 `equal`, `등 대` | 처음 셋은 닉네임 `차분한 등대`와 `Equal`에 부분 일치<br>`등 대`는 `차분한 등대`에 일치하지 않음 |
| 식별자 검색 | 회원 공개 식별자<br>없는 UUID | 1건<br>빈 `items` |
| 이메일 검색 | 연동 이메일 전체를 대문자 섞어 입력<br>이메일 앞부분만 | 1건<br>빈 `items` |
| 탈퇴 연동 이메일 | 탈퇴 처리된 연동의 이메일 | 빈 `items` |
| 탈퇴 회원 | 익명화 이름으로 검색<br>공개 식별자로 검색<br>`excludeDeleted=true` | 빈 `items`<br>1건과 `DELETED`<br>제외 |
| 검색어 오류 | 공백만<br>51자 | 400 |
| 검색어 없는 목록 | `status=ACTIVE`만 지정 | 활성 회원 전체 페이지<br>감사 로그 없음 |
| 확장 필드 | 채팅 2개, 소모 -40, 완료 결제 4800과 환불 결제 2000 | `chatCount` 2, `creditsSpent` 40, `paidKrw` 4800, `lastActiveAt`은 가장 최근 활동 |
| 활동 없음 | 가입만 한 회원 | `lastActiveAt` `null` |
| 채팅 구간 | `chatBucket=0`<br>`chatFrom`과 `chatTo` 지정 | 채팅 1개 회원만<br>기간의 채팅 수로 판정하고 `periodChatCount` 채움 |
| 원장 필터 | `creditDirection=spent&creditDate=날짜`<br>`creditDate`만 | 그날 소모 행 있는 회원<br>400 |
| 출석 필터 | `attendanceDate` | 그날 출석 보상 받은 회원 |
| 정렬 | `sort=paidKrw&order=desc` | 결제액 내림차순<br>같으면 공개 식별자 오름차순 |
| 상세 | 지갑 있는 회원<br>지갑 없는 회원 | `creditBalance` 잔액<br>0 |
| 누적 턴 수 | 회원의 채팅 셋(그중 하나는 삭제, 하나는 게스트 때 만들어 이관)에 AI 응답 메시지 2, 3, 4개와 사용자 메시지, 한 AI 응답의 재생성 판본 2개 | 목록 항목과 상세의 `turnCount` 모두 9<br>사용자 메시지와 판본은 세지 않음<br>목록의 `chatCount`는 삭제를 뺀 2 |
| 기간 턴 수 | 같은 회원, `chatFrom`과 `chatTo`가 AI 응답 3개인 채팅과 삭제된 AI 응답 2개 채팅의 생성일만 포함 | `periodChatCount` 1, `periodTurnCount` 5, `turnCount` 9 |
| 기간 없음 | `chatFrom`과 `chatTo` 없이 목록 조회 | `periodChatCount`와 `periodTurnCount` 모두 `null` |
| 턴 수 정렬 | 턴 수가 9, 0, 9, 4인 회원 넷과 `sort=turnCount&order=desc`<br>`chatFrom`, `chatTo`를 함께 지정 | 9, 9, 4, 0 순서이고 같은 9는 공개 식별자 오름차순<br>기간이 있어도 `turnCount` 누적 값 순서 |
| 턴 수 정렬 계획 | 수동 확인<br>로컬 PostgreSQL에 마이그레이션을 적용하고 `sort=createdAt`과 `sort=turnCount` 회원 목록 쿼리의 실행 계획 | `createdAt`은 턴 수 집계가 현재 페이지 행에만 실행<br>두 정렬 모두 `story_chats (user_id, created_at)`와 `story_messages (chat_id, role, created_at)` 인덱스 사용 |
| 상세 오류 | 없는 회원<br>UUID 아님 | 404<br>400 |
| 응답 범위 | 목록과 상세 응답 | 이메일과 소셜 식별자 필드 없음 |
| 이프 내역 | 원장 행 5건, `size` 2 | 기록 시각 내림차순, `balanceAfter`는 그 행까지의 누계, `totalPages` 3, 식별자 필드 없음 |
| 이프 내역 동률 | 같은 기록 시각에 +250, -20 순으로 기록된 원장 행 2개<br>기본 `desc`와 `order=asc` | `desc`는 -20 행이 먼저이고 `balanceAfter`는 230, 250 순<br>`asc`는 +250 행이 먼저 |
| 출석 기록 | 서로 다른 날 출석 2건 | 날짜 내림차순 2건과 `creditAmount` |
| 접속 기록 | 검색어 있는 목록, 상세, 이프 내역, 출석 기록 | `MEMBER_SEARCHED` 1행과 `MEMBER_VIEWED` 3행 |
| 결제 내역 필터 | `status=REFUNDED`, `memberId`, `from`과 `to` | 조건에 맞는 주문만 |
| 결제 검색 | 주문 공개 식별자, 회원 공개 식별자, 닉네임 일부 | 각각 일치 |
| 결제 상세 | 첫 완료 주문 전에 턴 2, 후에 턴 3과 환불 +20, 소모 -60 | `firstPaidAt`, `before.turns` 2, `after.turns` 3, `after.creditsSpent` 40 |
| 결제 상세 오류 | 대기 주문<br>없는 주문<br>UUID 아님 | 404<br>404<br>400 |
| 이프 내역 목록 | 회원 A 출석 적립 +250, 소모 -20, 환불 +20, 만료 -30과 회원 B 소모 -250, 팀 계정 소모 -20 | 필터 없이 6건 기록 시각 내림차순<br>`direction=granted` 1건, `direction=spent` 3건(팀 계정 포함), 환불과 만료는 어느 방향에도 없음 |
| 이프 내역 동률 | 같은 기록 시각의 행 2개 | 내부 ID 내림차순 |
| 이프 내역 필터 | `date`에 KST 자정 직전과 직후 행<br>탈퇴 회원의 행 | 그 날짜의 행만<br>탈퇴 회원 행도 포함되고 `member.status` `DELETED` |
| 이프 내역 응답 범위 | 응답 항목 | 원장 행 식별자, `balanceAfter`, 이메일 필드 없음<br>`member`는 회원 요약 구조 |
| 이프 내역 오류 | `direction=refund`, `date=2026-13-01`, `memberId` 지정 | 400, 400, 무시하고 전체 |
| 이프 내역 접속 기록 | 목록 조회 | 감사 로그 없음 |

<br>

### 5-5-8 분석 지표

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 조회 | 빈 저장소에서 `days` 7 | 대역에 세분화 조회 5회(`_active` 웹, 앱·국내, 앱·해외 로그인과 `_new` 웹, 앱·국내), `m=uniques`, `i=1`, `start`와 `end`가 7일 범위의 `YYYYMMDD`<br>`daily` 7개, `pendingDates` 빈 배열, `todayActiveUsers`가 마지막 항목의 `activeUsers`와 같음 |
| 조건 | 위 요청 | 웹 조회의 이벤트 필터에 `platform` `Web`과 `subprop_type` `user`의 `country` `South Korea`, `(none)` 조건<br>앱·국내 조회는 같은 `country` 조건과 `platform` `Android`<br>앱·해외 로그인 조회는 `country` `is not` `South Korea`, `(none)`, `platform` `Android`, `user_id` `is not` `(none)`<br>합계 조회와 `platform` `(none)` 조회 없음 |
| 플랫폼 값 | 그날 `_active` 웹 200, 앱·국내 18, 앱·해외 로그인 2<br>`_new` 웹 30, 앱·국내 4 | `activeUsers`의 `total` 220, `web` 200, `android` 20<br>`newUsers`의 `total` 34, `android` 4 |
| 해외 앱 사용자 | 국가가 `United States`인 Android 사용자 둘(로그인 1명, 비로그인 1명)과 Web 사용자 1명이 그날 활동 | 로그인한 Android 사용자만 `android`와 `total`에 들고 비로그인 Android 사용자와 Web 사용자는 어디에도 들지 않음<br>로그인한 해외 Android 사용자도 `newUsers`에는 들지 않음 |
| 과거 범위 | `from`과 `to`가 지난달 | `daily`는 그 범위, `todayActiveUsers`는 오늘 날짜 `_active` 세 조회 값으로 만든 값 |
| 코호트 제외 | 코호트 ID 설정 있음<br>빈 값 | 모든 세분화 요청의 `s`에 `userdata_cohort`와 `is not`과 코호트 ID<br>`s` 없음 |
| 오늘 값 갱신 | 10분 안에 같은 범위 두 번 호출<br>고정 시계를 10분 뒤로 옮긴 뒤 호출 | 대역 호출은 처음 5회뿐<br>오늘 날짜만 다시 조회 |
| 자정 경계 | 오늘을 포함한 범위를 KST 23:55에 조회한 뒤 다음 날 00:01에 같은 `from`, `to`로 조회<br>00:01 조회 때 대역이 500 | 00:01 조회는 어제가 된 날짜와 새 오늘 날짜를 조회<br>대역 500이면 `todayActiveUsers` `null`, 전날 값을 오늘 값으로 주지 않음 |
| 비용 예산 | 코호트 ID를 설정하고 빈 저장소에서 오늘로 끝나는 30일 범위 갱신<br>같은 설정의 빈 저장소에서 90일 범위 갱신 | 예산 계수기 300 증가, `pendingDates` 빈 배열<br>최근 50일만 받아 500 증가, 나머지는 `pendingDates` |
| 실패 | 대역이 500, 429, 5초 무응답<br>저장 값 없음 | 503, `admin_analytics_fetch_failed`의 `reason` 각각 `http_error`, `rate_limited`, `timeout` |
| 실패와 저장 값 | 오늘 값이 만료된 상태에서 대역 500 | 200, 만료된 오늘 값을 그대로 쓰고 `asOf`는 그 값을 받은 시각 |
| 쿨다운 | 실패 뒤 30초 안에 재요청<br>61초 뒤 재요청 | 대역 호출 없이 저장 값 또는 503<br>대역 재호출 |
| 단일 갱신 | 오늘 값이 만료된 뒤 대역이 3초 지연하는 동안 같은 범위 동시 요청 3건 | 갱신 요청은 1건이고 그 요청의 대역 조회는 오늘 날짜의 세분화 5회<br>나머지 2건은 기다리지 않고 저장 값으로 응답 |
| 부분 실패 | 빈 저장소에서 `_active` 세 조회 성공, `_new` 웹 조회 실패 | `_active` 값은 저장되지만 준비된 날짜가 없어 503<br>쿨다운 뒤 요청은 `_new` 두 조회만 보냄 |
| 자격 증명 없음 | 키 빈 값, 저장 값 없음 | 대역 호출 없이 503, `reason` `no_credentials` |
| 기간 오류 | `days` 10, 367일 범위, `to` 내일, `days`와 `from` 동시 | 400 |
| 격리 | 대역 500 상태에서 요약과 차트 호출 | 200 |

<br>

### 5-5-9 설치 지표

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 해석 | UTF-16LE로 인코딩한 뒤 gzip으로 압축한 월별 CSV 2개(9월 행 5개, 10월 행 3개) | 두 달 합산, `totalInstalls`가 8행의 기기 설치 합, `activeDevices`와 `asOf`는 날짜가 가장 늦은 행 |
| 총 사용자 설치 열 | 모든 행이 0인 열 | 어떤 응답 값에도 쓰이지 않음 |
| 일별 추이 | 첫 날짜부터 마지막 날짜까지 45일인 보고서, 그중 행 없는 날 2일, 설치가 1, 2, 3인 첫 세 행 | 누락일을 포함해 `daily` 45개, 날짜 오름차순, `cumulativeInstalls`가 1, 3, 6으로 이어지고 마지막 항목은 `totalInstalls`와 같음, 행마다 `activeDevices` |
| 빈 날 채움 | 10월 2일 행이 없고 1일 누계 5, 3일 설치 2 | 2일 항목이 `installs` 0, `uninstalls` 0, `cumulativeInstalls` 5, `activeDevices` `null`<br>3일 누계 7 |
| 날짜 | 보고서 날짜 `2026-10-17` | `asOf`가 그대로 `2026-10-17` |
| 캐시 | 1시간 안에 두 번 호출 | 대역 호출은 처음 한 번 |
| 캐시 만료 | 고정 시계를 1시간 뒤로 옮긴 뒤 호출 | 대역 재호출 |
| 실패 | 대역이 500, 설치 개요 객체 없음, 10초 무응답, 깨진 CSV<br>캐시 없음 | 503, `admin_play_stats_fetch_failed`의 `reason` 각각 `http_error`, `no_reports`, `timeout`, `parse_error` |
| 키 형식 오류 | base64가 아닌 키, base64이지만 JSON이 아닌 키 | 기동 정상<br>조회는 저장소 호출 없이 503, `reason` `http_error`, `status` `null` |
| 부분 실패 | 월별 파일 2개 중 하나가 500 | 503, 캐시 미갱신 |
| 실패와 캐시 | 캐시 있는 상태에서 대역 500 | 200과 캐시 값 |
| 쿨다운 | 실패 뒤 30초 안에 재요청 | 대역 호출 없이 503 또는 캐시 |
| 키 없음 | 설정값 빈 값 | 대역 호출 없이 503, `reason` `no_credentials` |
| 격리 | 대역 500 상태에서 요약, 차트, 분석 지표 호출 | 모두 영향 없음 |

<br>

### 5-5-10 캠페인 분석

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 캠페인 목록 | 조회 | 설정 파일의 4항목이 시작일 오름차순, 4차만 `endDate` `null` |
| 추이 조회 | `days` 7, 캠페인 생략 | 대역에 세분화 조회 16회가 순서대로, 모든 요청에 `s`가 없고 모든 이벤트 필터에 `subprop_type` `user`의 `country` 조건, Android 가입자 조회 2회만 `platform` `Android`이고 나머지 14회는 `platform` `Web`, 캠페인은 종료일 없는 마지막 항목의 값 |
| 목록 밖 캠페인 | `campaign=TEST_2026` | 200, 그 값으로 조회 |
| 세그먼트 차 | 전체 `_new` 10, 광고 7 | `newVisitors` `all` 10, `ads` 7, `nonAds` 3 |
| 소스별 | 광고 7, `ig` 2, `th` 1, `dc` 0, 그 밖 1 | `newVisitorsBySource` 각 값과 `ads`는 `newVisitors.ads`와 같음 |
| 가입자 합산 | Web 조건 구글 전체 3과 광고 2, 카카오 전체 1과 광고 1<br>Android 조건 구글 5, 카카오 2 | `signups` `all` 4, `ads` 3, `nonAds` 1<br>`androidSignups` 7, `signups`에 Android 값이 섞이지 않음 |
| Android 가입자 조회 | `days` 7 | Android 가입 조회 2회에 `is_new_user` `true`, `country`, `platform` `Android` 필터만 있고 `gp:initial_utm_campaign` 필터 없음<br>`totals.androidSignups`는 일별 합 |
| 누계 | 이틀 가입 4, 2 | `cumulativeSignups.all` 4, 6 |
| 합계 | 이틀 DAU 100, 200과 신규 방문자 전체 10, 광고 7 | `activeUsersAverage` 150, `adsShare` 0.7 |
| 추이 기간 | 366일<br>367일, `days` 90 | 200<br>400 |
| 간편 제작 퍼널 | `days` 7 | 대역에 퍼널 조회 2회, 순서 모드와 `cs` 86400, 6단계, `s` 없음, 단계마다 이벤트 필터에 `country`와 `platform` 조건 |
| 퍼널 빈 결과 | 퍼널 대역이 HTTP 200과 `data: []` | 모든 단계의 사용자 수 0, 정상 응답과 값 저장 |
| 퍼널 형식 오류 | `data` 없음, `data` `null`, 6단계 요청에 5단계 항목 | 503, `admin_analytics_fetch_failed`의 `reason` `parse_error`, 값 저장 안 함 |
| 퍼널 세그먼트 차 | 1단계 전체 100, 광고 80 | `steps[0].users` `all` 100, `ads` 80, `nonAds` 20 |
| 상세 진입 퍼널 | `days` 7, `storyId` 생략, 캠페인은 4차 | 대역에 퍼널 조회 1회, `storyId`는 목록 항목의 값, 1단계 필터에 `story_id`와 `gp:utm_campaign`, 3~7단계 `turn_number` `"1"`~`"5"` |
| 대상 스토리 없음 | `campaign=TEST_2026`, `storyId` 생략 | 400 |
| 퍼널 기간 | 간편 제작 20일과 상세 진입 31일<br>간편 제작 21일이나 `days` 30, 상세 진입 32일 | 200<br>400 |
| 유입 소스 | `days` 7 | 대역에 세분화 조회 2회, 첫 조회는 `g`에 `gp:initial_utm_source`만 두고 `g2` 없음, 둘째 조회는 이벤트 묶음 `utm_content` 하나, 예산 계수기 350 증가, `sources`는 `newVisitors` 내림차순<br>둘째 조회의 이벤트 필터가 `utm_medium`, `subprop_op` `is`, 값 `["community","social"]`이고 `in`을 쓰지 않음 |
| 유입 소스 기간 | 10일<br>11일, `days` 30 | 200<br>400 |
| 캠페인 없음 | 목록에 종료일 없는 항목이 없고 `campaign` 생략<br>101자 `campaign` | 400 |
| 저장 키 | 같은 범위에 다른 `campaign` 두 번 | 대역 호출 두 묶음, 캠페인 값이 다른 매개변수 해시 |
| 지난 기간 | 그저께까지의 범위를 한 번 조회한 뒤 10분 뒤, 25시간 뒤, 30일 뒤에 다시 호출 | 대역 재호출 없음 |
| 푸시 열람 조회 | 측정 시작일이 범위 첫날 이전, `days` 7 | 대역에 세분화 조회 1회, 이벤트 필터 `utm_source` `is` `["push"]`, 이벤트 묶음 `utm_campaign` 하나, `limit` 1000, `s`와 `country`와 `platform` 조건 없음, 예산 계수기 175 증가 |
| 푸시 열람 대응 | 묶음 값이 캠페인 공개 식별자, `attendance_reminder`, `KR_META_WEB_ACTIVATION_COLD_202610`, `(none)` | 앞의 둘만 그 캠페인과 출석 리마인드에 들고 나머지는 버림 |
| 푸시 열람 날짜 합 | 캠페인 하나의 푸시 열람 10-23 30명, 10-24 5명, 도달 100명 | `openState` `MEASURED`, `pushOpens` 35, `pushOpenRate` 0.35 |
| 열람률 1 초과 | 도달 2명, 날짜별 열람 합 3 | `pushOpenRate` 1.5 |
| 딥링크 없는 발송 | 딥링크 포함 여부가 거짓인 프로모션 | `openState` `NO_LINK`, `pushOpens`와 `pushOpenRate` `null`, `deliveredMembers`는 값 |
| 측정 시작 전 캠페인 | 측정 시작일 10-21, 마지막 회차 선점 10-19 | `openState` `BEFORE_MEASUREMENT`, `pushOpens` `null` |
| 발송 기록 없음 | 딥링크 포함 여부가 `null`인 캠페인(회차 진행 중이거나 커밋 전 실패) | `openState` `PENDING`, `pushOpens`와 `pushOpenRate` `null`, `MEASURED`가 아님 |
| 측정 시작일 미설정 | 설정값 비어 있음 | 대역 호출 없음, 200, `asOf`와 `measuredFrom`과 `activityFrom` `null`, `pendingDates` 빈 배열, 모든 `openState` `BEFORE_MEASUREMENT`, 활동 알림의 `deliveredMembers`는 범위 전체 |
| 범위 전체가 측정 전 | 측정 시작일 10-21, 범위 10-10~10-16 | 대역 호출 없음, 200, `asOf` `null`, `pendingDates` 빈 배열, `activityFrom` `null` |
| 활동 알림 집계 구간 | 범위 10-18~10-24, 측정 시작일 10-21, 예산 부족 없음 | 대역 조회 날짜는 10-21~10-24, `activityFrom` 10-21, 활동 알림의 `deliveredMembers`도 10-21~10-24, `pendingDates`에 10-18~10-20 없음 |
| 활동 알림 도달 중복 | 같은 회원에게 10-23 스토리 완성 3건 도달 | 그날 도달 회원 1 |
| 도달 없음 | 활동 알림 도달 0, 열람 2 | `pushOpens` 2, `pushOpenRate` `null` |
| 캠페인 범위 | 선점 시각이 범위 전날인 캠페인, 선점 전에 취소한 캠페인 | 둘 다 `campaigns`에 없음 |
| 활동 알림 항목 | 열람과 도달이 모두 없음 | `activityTypes` 3항목이 고정 순서, `openState` `MEASURED`, 값 0, `pushOpenRate` `null` |
| 푸시 열람 부분 응답 | 예산이 3일치만 남음 | 최근 3일만 조회, 나머지 날짜는 `pendingDates`, 열람 수는 준비된 날짜의 합, `deliveredMembers`는 집계 구간 전체 |
| 푸시 열람 기간 | 366일<br>367일, `days` 90 | 200<br>400 |
| 비용 예산 | 빈 저장소에서 5분 안에 예산을 450 소비한 뒤 추이 7일 갱신(하루 16) | 남은 50으로 최근 3일만 조회해 200, 나머지 4일은 `pendingDates`<br>예산을 490 소비한 뒤에는 하루치도 예약하지 못해 대역 호출 없이 503, `reason` `budget_exceeded`, 그 키에 60초 쿨다운 |
| 기본 예산 | 설정값 없음 | 태스크 예산 500 |
| 상한 비용 | 간편 제작 퍼널 20일 갱신 | 예산 계수기 480 증가, 호출 성공 |
| 부분 실패 | 빈 저장소에서 세분화 16회 중 5번째가 500 | 앞 4회의 값은 저장, 남은 11회는 보내지 않음, 준비된 날짜가 없어 503, 이후 요청은 60초 쿨다운<br>쿨다운 뒤 요청은 저장되지 않은 12개 조회만 보냄 |
| 예약분 반환 | 추이 7일 갱신(비용 112)에서 세분화 3번째 조회가 500 | 계수기에는 성공한 2회의 비용 14만 남음 |
| 원자적 예약 | 남은 예산 120에서 서로 다른 캠페인의 빈 7일 추이 갱신 둘이 동시에 시작 | 하나는 7일(112)을 예약해 호출하고 다른 하나는 남은 8로 하루치(16)도 예약하지 못해 `budget_exceeded` |
| 직렬 호출 | 서로 다른 엔드포인트의 갱신 둘이 동시에 시작 | 대역에 동시에 들어온 요청이 항상 1개 이하 |
| 격리 | 대역 500 상태에서 요약, 차트, 분석 지표 호출 | 모두 영향 없음 |

<br>

### 5-5-11 사용자, 전환, 기능과 품질 지표

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 사용자 활동 | `days` 7, `to` 10-21 | 대역에 세분화 14회(`_active` 5, `_new` 4, 평균 2, MAU 3), 사용자 수 조회 없음<br>MAU는 `_active` 3회이고 `start` 09-22, `end` 10-21, Android 외와 앱·국내와 앱·해외 로그인 조건<br>앱·해외 로그인 조건은 `_active`와 MAU에만 있음<br>세분화에는 `g`와 `s`가 없음 |
| MAU 값 | MAU 세분화 응답의 `seriesCollapsed` Android 외 1100, 앱·국내 90, 앱·해외 로그인 10, 일별 `series` 합 3000 | `monthlyActiveUsers` 1200 |
| MAU 기간 중 조건 변경 | 30일 가운데 앞 10일은 국내 웹, 뒤 20일은 해외 로그인 앱으로 활동한 사용자 하나 | Android 외 1, 앱·해외 로그인 1이라 `monthlyActiveUsers`에 2로 듦 |
| MAU 비용과 키 | 같은 `to`로 두 번 요청 | 처음에만 MAU 조회 비용 90 예약<br>범위 지표 키는 MAU 조회 정의와 09-22, 10-21 |
| 세션 날짜 형식 | 세션 응답 `xValues`가 `2026-10-22T00:00:00` | 그 값이 2026-10-22 항목에 들어감 |
| 리텐션 코호트 키 | 리텐션 응답의 코호트 키 `Oct 23, 2026` | 코호트 날짜 2026-10-23으로 저장하고 응답 |
| 플랫폼별 값 | `_active` Android 외 11, 웹 10, 앱·국내 2, 앱·해외 로그인 1, 플랫폼 없음 2<br>`_new` Android 외 5, 앱·국내 1 | `activeUsers`의 `all` 14, `web` 10, `android` 3, `unknown` 2<br>`newVisitors`의 `all` 6, `android` 1<br>셋의 합 15와 `all`이 달라도 그대로 |
| 사용자당 전송 수 | 평균 응답 Web 4.5 | `messagesPerUser.web` 4.5, `all`과 `unknown`은 `null` |
| 활동 기간 | 366일<br>367일 | 200<br>400 |
| 리텐션 | `days` 7 | 대역에 리텐션 조회 3회, 시작 `_new`와 복귀 `_active`, `rm` 없음, 코호트 7개, `s` 없이 시작과 복귀 이벤트의 필터에 전체는 `country`만, Web은 `country`와 `platform` `Web`, Android는 `country`와 `platform` `Android`, `user_id` 조건 없음, 예산 계수기 168 증가 |
| 플랫폼 전환 복귀 | 10-20에 웹에서 처음 방문하고 10-21에 앱으로만 활동한 국내 사용자 | 10-20 코호트의 `all` `d1`에 복귀로 듦<br>`web` `d1`에는 복귀로 들지 않고 `android` 코호트에는 없음 |
| 리텐션 인덱스 | 신규 방문일이 오늘에서 20일 전인 코호트 배열<br>인덱스 0이 `count`와 `outof` 20, 인덱스 1(Day 0)이 `count` 19와 `outof` 20<br>인덱스 2부터 6까지가 `outof` 20에 `count` 5, 4, 3, 2, 1, 인덱스 7이 `outof` 0, 인덱스 8이 `incomplete`<br>길이가 11이라 인덱스 31 없음 | `users` 20<br>`d1` 0.25, `d2` 0.2, `d3` 0.15, `d4` 0.1, `d5` 0.05, `d6` `null`, `d7` `null`, `d30` `null` |
| D1 인덱스 회귀 | 신규 방문일이 오늘에서 10일 전인 코호트 배열<br>인덱스 0이 `count`와 `outof` 200, 인덱스 1(Day 0)이 `count` 199와 `outof` 200, 인덱스 2가 `count` 30과 `outof` 200<br>세 칸 모두 `incomplete` 아님 | `d1`은 인덱스 2를 읽은 0.15<br>인덱스 1의 0.995는 어느 필드에도 없음 |
| 리텐션 요약 | 고정 시계 KST 10-26, 범위 10-21~10-23<br>인덱스 4(Day 3)가 10-21 코호트는 `count` 1과 `outof` 10, 10-22 코호트는 `count` 9와 `outof` 30, 10-23 코호트는 `count` 5와 `outof` 5 | `summary.d3` 0.25<br>10-23 코호트의 `d3`은 10-26이 끝나지 않아 `null`이고 요약에 들지 않음 |
| 리텐션 기간 | 366일<br>`to`가 오늘, 367일, `days` 30 | 200<br>400 |
| 세션 | `days` 14 | 대역에 평균 세션 길이 조회 3회, 사용자당 세션 수 조회 없음, `s`는 전체가 `country`, Web과 Android가 `country`와 `platform`, `user_id` 조건 없음, `averageSessionSeconds`의 `all`, `web`, `android`, 예산 계수기 448 증가 |
| 세션 기간 | 366일, 쿼리 생략 시 14일<br>367일, `days` 30 | 200<br>400 |
| 세션 대상 | `days` 7, `segment=member`<br>`segment=guest`<br>`segment=visitor` | 세션 조회 3회의 `s`에 `{"prop":"user_id","op":"is not","values":["(none)"]}`가 더해지고 예산 계수기 308 증가, `segment` 생략 때와 다른 저장 키<br>같은 조건의 `op`가 `is`<br>400 |
| 세션 실패 | 대역이 세션 조회에 500 | 503, `reason` `http_error` |
| 신규 가입자 | 회원 3명(구글 2, 카카오 1), 그중 1명 `migrated_at` 있음, 팀 계정 1명 | `signups.total` 3, `google` 2, `kakao` 1, `migratedFromGuest` 1, 팀 계정 제외, `signups`에 `other` 필드 없음 |
| 재가입 예전 계정 | 10-20 구글로 가입하고 `migrated_at`이 있는 회원 A가 탈퇴<br>10-22 같은 구글 계정으로 재가입해 회원 B 생성, A의 연동 행이 B로 옮겨짐 | 10-20 `signups.total` 0, `migratedFromGuest` 0<br>10-22 `signups.total` 1, `google` 1<br>재가입 전 같은 범위를 조회했을 때 10-20 `total` 1 |
| 탈퇴만 한 회원 | 탈퇴해 연동 행이 모두 `deleted_at`을 가진 회원 | 가입일의 `signups`와 누계에 듦 |
| 누적 가입자 | 범위 첫날 전에 가입한 회원 5명(그중 탈퇴 1, 재가입으로 연동을 넘긴 예전 계정 1), 범위 첫날 2명, 둘째 날 1명(탈퇴), 팀 계정 1명<br>끝 날짜가 오늘 | `cumulativeSignups` 6, 7<br>같은 데이터의 요약 `members.total` 8보다 1 작음 |
| 신규 가입자 플랫폼 | `days` 7 | 대역에 세분화 6회, 구글과 카카오 이벤트마다 `is_new_user` `true`와 `country`, 웹은 `platform` `Web`, 앱·국내는 `Android`, 플랫폼 없음은 `(none)`, `user_id` 조건과 `s` 없음 |
| 플랫폼 합 | 하루 구글 웹 3, 앱 5, 없음 1과 카카오 웹 1, 앱 2, 없음 0 | `signupsByPlatform` `all` 12, `web` 4, `android` 7, `unknown` 1 |
| 플랫폼 준비 중 | 예산이 3일치만 남은 7일 요청 | 200, 7일 모두 DB 값, 최근 3일만 `signupsByPlatform` 값, 나머지 4일은 `signupsByPlatform` `null`이고 `pendingDates`에 있음 |
| 플랫폼 시간 한도 | 빈 저장소, 대역이 신규 가입자 플랫폼 조회마다 2초씩 늦게 응답<br>같은 상태에서 채팅 턴 도달률과 채팅 옵션 비중 요청 | 5초 안에 200, DB 값 정상, 받은 조회 값만 저장, 받지 못한 날짜는 `signupsByPlatform` `null`과 `pendingDates`, `admin_analytics_fetch_failed`의 `reason` `timeout`, 그 키에 60초 쿨다운<br>두 엔드포인트도 5초 안에 200이고 플랫폼 값만 `null`과 `pendingDates` |
| 플랫폼 사용 불가 | 대역 500, 저장 값 없음<br>자격 증명 빈 값 | 두 경우 모두 200, DB 값은 정상, 모든 날짜가 `pendingDates`, `platformAsOf` `null`<br>대역 500이면 `admin_analytics_fetch_failed` |
| 전환 퍼널 | `web-first-visit` `days` 7 | 대역에 퍼널 조회 1회, 6단계, `s` 없음, 단계마다 이벤트 필터에 `country`와 `platform` `Web` |
| 앱 첫 접속 퍼널 | `android-first-visit` `days` 7 | 대역에 퍼널 조회 1회, 2단계, 단계마다 이벤트 필터에 `country`와 `platform` `Android`, `user_id` 조건과 `s` 없음 |
| 전환 퍼널 빈 결과 | 퍼널 대역이 HTTP 200과 `data: []` | 단계 사용자 수 모두 0, 정상 응답 |
| 퍼널 플랫폼 | `story-creation` `platform=android`<br>`web-first-visit`에 `platform` 지정 | 단계마다 이벤트 필터 `country`와 `platform` `Android`, `user_id` 조건 없음<br>400 |
| 상세 스토리 한정 | `story-detail-chat` `storyId` 지정<br>생략 | 1단계와 2단계에 `story_id` 필터<br>필터 없음 |
| 게스트 한도 퍼널 | 구글 퍼널 2단계 6과 3단계 5, 카카오 3단계 2 | 대역에 퍼널 조회 2회, `steps[1].users` 6, `steps[2].users` 7로 앞 단계보다 커도 그대로, `event` `login_succeeded` |
| 퍼널 기간 | 31일<br>32일, 모르는 퍼널 이름 | 200<br>400 |
| 턴 도달률 | 게스트 채팅 턴 0, 5와 회원 채팅 턴 10, 20 | `reached` 12개<br>`all` `chats` 4, 턴 1부터 5까지 비율 0.75, 6부터 10까지 0.5, 15와 20은 0.25, 30과 50은 0<br>`guest`와 `member`의 `chats` 각 2 |
| 게스트에서 회원으로 | 이관 시각 전 생성 채팅 턴 5와 7, 이관 뒤 생성 채팅 턴 8 | `chatsReached5` 2, `chatsReached6` 1, `rate` 0.5 |
| 턴 도달률 플랫폼 | `days` 7, `segment` 생략 | 대역에 세분화 36회, 모두 `server_chat_aiMessage_processed_succeeded`의 합계, 이벤트 필터에 `is_regenerated` `false`와 `turn_number` `"1"`~`"50"` 중 하나, `country`와 `platform` 조건, `user_id` 조건 없음<br>`segment` `all` |
| 게스트와 회원 구분 | `segment=guest`<br>`segment=member`<br>`segment=visitor` | 36회 모두 `user_id` `is` `(none)` 필터<br>36회 모두 `user_id` `is not` `(none)` 필터, `segment` 생략 때와 다른 저장 키<br>400 |
| 플랫폼 도달 값 | 웹의 턴 1 이벤트 이틀 합 10, 턴 5 합 4, 턴 50 합 0<br>앱·국내 턴 1 합 20, 턴 5 합 10<br>플랫폼 없음 모두 0 | `web` `chats` 10, 턴 5 `rate` 0.4<br>`all` `chats` 30, 턴 5 `chats` 14<br>`unknown` `chats` 0과 모든 `rate` 0 |
| 플랫폼 도달 1 초과 | 범위 안 턴 1 이벤트 2, 턴 2 이벤트 3 | 턴 2 `rate` 1.5 |
| 플랫폼과 DB 분리 | `segment=member`, DB에 게스트 채팅 1개와 회원 채팅 1개 | `segments` 세 항목은 `segment` 생략 때와 같음<br>대역 500이면 200, `platforms` `null`, `segments`와 `guestToMember`는 정상 |
| 기능 사용 | `days` 7, `platform=web` | 대역에 세분화 12회(전송 합계, 입력 방식 필터 3개, 스트림 오류, 사용자 수 7개), `g`와 `s` 없음, 모든 이벤트 필터에 `country`와 `platform` `Web` 조건 |
| 기능 사용 플랫폼 | `days` 7, `platform=android`<br>`platform=all` | 앱·국내 12회와 앱·해외 로그인 12회, 응답 값은 두 묶음의 합<br>Android 외 12회와 앱 두 묶음 24회, 응답 값은 세 묶음의 합 |
| 기능 사용 대상 | `days` 7, `platform=all`, `segment=guest`<br>`platform=all`, `segment=member` | Android 외와 앱·국내 24회만 보내고 모든 이벤트 필터에 `user_id` `is` `(none)`, 앱·해외 로그인 묶음은 조회 없이 0<br>Android 외와 앱·국내 24회에 `user_id` `is not` `(none)` 필터, 앱·해외 로그인 12회는 `segment` `all`과 같은 저장 키라 저장 값이 있으면 다시 받지 않음 |
| 입력 방식과 오류율 | 전송 합계 100, `choice` 60, `plain` 25, `block` 10, 스트림 오류 5 | `messagesByInputMode`의 `choice` 60, `plain` 25, `block` 10, `unknown` 5, `streamErrorRate` 0.05 |
| 오류율 1 초과 | 전송 합계 2, 스트림 오류 3 | `streamErrorRate` 1.5 |
| 기능 사용 기간 | 366일<br>367일, `days` 90 | 200<br>400 |
| 채팅 옵션 비중 | 채팅 4개 중 페르소나 1개, 모델 `AURORA` 1개와 `LITE` 3개 | `withPersona` 1, `byModel` `{"AURORA": 1, "LITE": 3}` |
| 모델별 턴 수 | 10-21 AI 응답: 메시지 `model_code` `AURORA` 2개(그중 하나는 재생성 판본 2개), 10-20에 만든 채팅의 `LITE` 3개, 삭제된 채팅의 `LITE` 1개, 채팅 모델이 `AURORA`인 게스트 채팅의 `LITE` 1개, `model_code`가 `NULL`인 1개, 팀 계정 채팅의 1개 | 10-21의 `turnsByModel` `{"AURORA": 2, "LITE": 5, "UNRECORDED": 1}`<br>합 8이 같은 데이터의 대시보드 차트 10-21 `turns`와 같음 |
| 모델 변경과 재분류 | `LITE`로 턴 3개를 만든 뒤 채팅 모델을 `AURORA`로 바꿈 | `turnsByModel`은 그대로 `LITE` 3, `byModel`은 그 채팅을 `AURORA`로 셈 |
| 채팅 옵션 플랫폼 | `days` 7, `chat_models`에 `LITE`와 `AURORA` | 대역에 세분화 12회<br>채팅 시작 클릭 6회는 `persona_type` `default`나 `persona` 필터와 세 플랫폼 조건<br>성공 이벤트 6회는 `is_regenerated` `false`, `model_code` `LITE`나 `AURORA` 필터와 세 플랫폼 조건 |
| 페르소나 클릭 값 | 하루 웹 클릭 `default` 8, `persona` 2와 앱·국내 `default` 5, `persona` 0 | `chatStarts` `all` 15, `web` 10, `android` 5<br>`personaChatStarts` `all` 2, `web` 2, `android` 0 |
| 플랫폼 모델 턴 | 하루 웹 `LITE` 4, `AURORA` 1과 앱·국내 `LITE` 3, `AURORA` 0 | `platformTurnsByModel` `{"AURORA": {"all": 1, "web": 1, "android": 0, "unknown": 0}, "LITE": {"all": 7, "web": 4, "android": 3, "unknown": 0}}` |
| 모델 추가 | 저장 값이 있는 범위에서 `chat_models`에 새 코드 추가 | 새 코드의 조회 3회만 보내고 기존 코드의 날짜는 다시 받지 않음 |
| 채팅 옵션 준비 중 | 대역 500, 저장 값 없음 | 200, `chats`, `withPersona`, `byModel`, `turnsByModel`은 정상, 플랫폼 값 셋은 `null`, 모든 날짜가 `pendingDates` |
| AI 비용 | 환율 1,400, Langfuse 대역이 10-21 KST의 `채팅 턴` 모델 `gpt-x` 0.004 USD와 `채팅 선택지` 0.001 USD, AI 호출 기록에 같은 날 `chat_response` `gpt-x` 성공 2회와 `choice_generation` 1회 | `chat_response` 항목 `calls` 2, `costKrw` 5.6, `choice_generation` 항목 `costKrw` 1.4, `costPerTurnKrw` 3.5 |
| KST 날짜 합산 | 대역의 1시간 단위 값이 UTC 10-21 14:00(KST 22-23시)와 UTC 10-21 15:00(KST 10-22 00시) | 앞의 값은 10-21, 뒤의 값은 10-22 항목 |
| 한쪽에만 있는 조합 | AI 호출 기록에만 있는 모델 `gpt-y`, Langfuse에만 있는 모델 `gpt-z` | `gpt-y` 항목 `costKrw` `null`, `gpt-z` 항목 `calls` 0과 비용 |
| 매핑 없는 이름 | Langfuse 추적 이름 `새 기능` 0.002 USD | `unmapped`에 `새 기능`과 2.8, `totals.costKrw`에 포함 |
| 실시간 이미지 | 장당 원가 48, `chat_image` 성공 3회와 실패 1회, Langfuse에 `이미지 생성:자식` 관측 | `chat_image` `costKrw` 144<br>Langfuse 질의에 `이미지 생성:자식` 제외 조건 |
| 비용 0 모델 | Langfuse 모델 `gpt-w`의 토큰 1,000과 비용 0 | `unpricedModels`에 `gpt-w` |
| 저장과 확정 | 고정 시계 10-23, 범위 10-15~10-23 첫 요청 뒤 두 번째 요청 | 첫 요청은 3일 구간 세 번으로 받고, 두 번째는 오늘 값이 10분 안이면 호출 없음<br>10-15~10-21은 `finalized_at` 기록<br>`value`는 `traceName`, `model`, `costUsd`, `totalTokens` 배열 |
| 빈 날 저장 | 정상 응답에 10-17 데이터가 없음 | 10-17 행이 빈 배열로 저장되고 다음 요청에서 다시 받지 않음, 비용 0 |
| 저장 키 | 환경 이름 설정을 바꾼 뒤 같은 범위 요청 | 다른 `params_hash`라 새로 받음, `params`에 공개 키 없음 |
| 긴 범위 | 고정 시계 10-24, 보관 일수 30, 비어 있는 90일 | 보관 시작일 09-26 전 61일은 호출 없이 `expiredDates`<br>보관 기간 안 29일 가운데 3일 구간 6번으로 최근 18일을 받고 나머지 11일은 `pendingDates` |
| 행 제한 분할 | 3일 구간 응답이 1,000행 | 저장하지 않고 36시간 두 구간으로 나눠 다시 받음 |
| 자정 경계 | KST 10-21 00:00:00.000에 시작한 관측이 있고 10-20과 10-21이 서로 다른 구간 | 앞 구간의 `toTimestamp`가 10-21 KST 00:00의 1밀리초 전이고 그 관측은 10-21에 한 번만 집계 |
| 자정 넘는 추적 | KST 10-20 23:59에 시작한 `채팅 턴` 추적의 10-21 00:01 관측 | v2 질의로 10-21 비용에 들어감 |
| v2 경로 | Langfuse 호출 | 경로가 `/api/public/v2/metrics`이고 `query`가 URL 인코딩된 JSON |
| 호출 간격 | 한 요청 안의 두 호출 | 두 호출 사이 1초 이상 |
| 호출 제한 | 대역이 429와 `Retry-After: 30` | 30초 동안 호출 없음, 저장 값만 응답, `reason` `rate_limited` |
| 실패와 저장 값 | 대역 500, 범위의 일부 날짜만 저장 | 200, 저장된 날짜만 비용, 나머지 `pendingDates`, `reason` `http_error` |
| 밖 저장 값과 안 실패 | 범위 09-20~09-28 가운데 보관 기간 밖 09-20만 저장 값, 보관 기간 안 조회가 대역 500 | 200, 09-20만 비용, 09-26~09-28은 `pendingDates`, 09-21~09-25는 `expiredDates` |
| 실패와 저장 없음 | 대역 500, 저장 값 없음 | 503 |
| 설정 없음 | Langfuse 비밀 키 빈 값 | 호출 없이 503, `reason` `not_configured` |
| 형식 오류 | 대역이 숫자가 아닌 비용 | 503 또는 저장 값 응답, `reason` `parse_error` |
| AI 비용 범위 | 실패 호출과 팀 계정 회원의 호출 | 호출 수, 토큰, 원가의 분모는 실패 제외와 팀 계정 포함<br>금액은 Langfuse의 실패한 추적 비용도 포함 |
| 보관 경계 | 고정 시계 KST 10-24, 보관 일수 30, 빈 저장소, 범위 09-25~09-28 | `retentionStartDate` 09-26, 호출은 09-26 KST 00:00부터 09-28 끝까지의 3일 구간 1번<br>09-25만 호출 없이 `expiredDates`, `costKrw` `null` |
| 저장값 재사용 | 위 상태에서 09-25에 확정 저장 값이 있음 | 09-25는 저장 값으로 비용을 채우고 `expiredDates`에 없음, 그 날짜 호출 없음 |
| 미확정 저장값 재사용 | 09-25에 `finalized_at`이 없는 저장 값 | 다시 받지 않고 그 값을 씀, `expiredDates`에 없음 |
| 과거 저장값의 `asOf` | 범위 09-01~09-05가 모두 보관 기간 밖이고 저장 값이 있음 | 호출 없음, `asOf`는 `null`이 아니고 쓴 저장 값의 받은 시각 가운데 가장 이른 시각 |
| 보관 기간 밖만 | 범위 07-01~07-31, 저장 값 없음<br>같은 범위에 Langfuse 비밀 키 빈 값<br>같은 범위에 실패 쿨다운 중 | 세 경우 모두 Langfuse 호출 없이 200, 31일 모두 `expiredDates`, `asOf` `null`, `totals.costKrw`는 실시간 이미지 비용만, `costPerTurnKrw` `null` |
| 400 회귀 | 대역이 보관 시작 전 구간에 400을 주도록 설정, 범위 07-01~10-24 | 대역에 보관 시작일 전 구간 호출 없음, `admin_ai_cost_fetch_failed` 없음, 200 |
| 원가 분모 | 10-21은 저장 값, 10-22는 `pendingDates`, 09-20은 `expiredDates`<br>세 날의 `chat_response` 성공 10, 20, 30회와 `story_completion` 성공 1, 2, 3회 | `costPerTurnKrw`의 분모는 10, `costPerStoryKrw`의 분모는 1 |
| 배치 저장 | 고정 시계 KST 10-24 00:05 배치 실행, 10-22 확정 값 없음 | Langfuse 호출 1번으로 10-22를 받아 `finalized_at` 기록<br>같은 날 다음 실행은 호출 없음 |
| 배포 직후 백필 | 빈 저장소, 고정 시계 10-24 첫 배치 실행 | 09-26~10-22 27일을 최근 날짜부터 3일 구간 6번으로 18일 받고 다음 실행에서 남은 9일을 받음 |
| 배치 호출 제한 | 배치 실행 중 대역 429와 `Retry-After: 60` | 그 실행을 끝내고 60초 동안 화면 요청과 배치 모두 호출 없음 |
| 400 쿨다운 공유 | 보관 기간 안 구간 조회에 대역이 400, 저장 값 없음 | 화면 요청은 503과 `admin_ai_cost_fetch_failed`의 `status` 400<br>60초 동안 화면 요청과 배치 실행 모두 Langfuse 호출 없음<br>60초 뒤 화면 요청과 배치 모두 다시 호출 |
| 배치 독립 실행 | 슬롯을 잡은 실행에서 Amplitude 백필 대상 없음<br>Amplitude 배치 몫 소진<br>Amplitude 대역 429 | 세 경우 모두 같은 실행에서 AI 비용 단계가 확정 값이 없는 날짜를 받음 |
| 호출 상한 분리 | 같은 5분 안에 화면 요청 하나와 배치 실행 하나, 받을 날짜가 많음 | 화면 요청 6번, 배치 6번, 두 경로의 호출이 겹치지 않고 1초 이상 간격 |
| DB 지표 기간 | 366일<br>367일 | 200<br>400 |
| 격리 | 대역 500 상태에서 DB 지표 호출 | 모두 200<br>신규 가입자, 턴 도달률, 채팅 옵션은 플랫폼 값만 `null`과 `pendingDates` |

<br>

### 5-5-12 Amplitude 값 저장

고정 시계와 실제 저장 테이블을 쓰는 통합 테스트다. 날짜는 KST 기준이며 오늘을 D로 적는다. upsert 구문이 H2에서 다르게 동작하면 확정 행 보호는 DB 문서 생성 스크립트 경로의 PostgreSQL에서 검증한다.

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 비어 있는 날짜만 조회 | D-10부터 D-4까지 저장된 상태에서 D-13부터 D-2까지 캠페인 추이 요청 | 대역 조회는 D-13~D-11과 D-3~D-2 두 구간뿐<br>저장된 7일은 다시 조회하지 않음 |
| 확정일 경계 | D-2 값이 D-1에 받은 값<br>D-2 값이 D-2 당일에 받은 값 | 다시 조회하지 않고 `finalized_at`을 채움<br>한 번 다시 조회한 뒤 확정 |
| 어제 재갱신 | D-1 값이 D-1 당일에 받은 값인 상태로 D에 요청<br>같은 날 두 번째 요청 | D-1을 한 번 다시 조회<br>D-1은 다시 조회하지 않고 오늘만 10분마다 |
| 오늘 10분 | 오늘 값을 받은 지 9분과 11분 | 재조회 없음과 오늘만 재조회 |
| 확정 행 보호 | `finalized_at`이 있는 행에 같은 키로 upsert | 값과 `fetched_at`이 바뀌지 않음 |
| 예산 초과 시 부분 응답 | 빈 저장소에서 사용자 세션 60일 요청(하루 32) | 최근 15일만 조회해 200, 나머지 45일은 `pendingDates`, `admin_analytics_fetch_failed`의 `budget_exceeded`는 없음<br>예산이 남지 않은 상태의 다음 요청은 호출 없이 같은 응답과 `budget_exceeded`, 60초 쿨다운 |
| 이어 받기 | 위 상태에서 5분 뒤 요청 | 다음 15일만 조회하고 `pendingDates`가 30일로 줄어듦 |
| 범위 지표 | `to`가 D-3인 퍼널을 두 번 요청<br>`to`가 D인 퍼널을 10분 뒤 요청 | 두 번째는 대역 호출 없음<br>범위 전체를 다시 조회 |
| 리텐션 고정 | 코호트 날짜 D-40의 배열이 32칸이고 인덱스 0~31 모두 `incomplete` 아님<br>코호트 날짜 D-10의 배열에 `incomplete`가 있음 | D-40은 확정되어 다시 조회하지 않음<br>D-10은 하루 한 번만 다시 조회 |
| D30 미완료 | 코호트 날짜 D-32의 32칸 배열에서 인덱스 0~30은 `incomplete` 아님, 인덱스 31만 `incomplete`<br>코호트 날짜 D-32의 31칸 배열이 모두 `incomplete` 아님 | 두 경우 모두 확정하지 않고 하루 한 번 다시 조회 |
| 잘못 확정된 리텐션 행 | `finalized_at`이 있는 코호트 행의 배열에 인덱스 31이 없거나 인덱스 31이 `incomplete`<br>D-1에 받은 행과 D에 받은 행 | 두 행 모두 읽을 때 저장 행의 `finalized_at`을 비움<br>D-1에 받은 행은 D에 한 번 다시 조회해 새 값으로 저장하고 D에 받은 행은 D+1에 다시 조회<br>새 값의 인덱스 0~31이 모두 `incomplete` 아니면 다시 확정 |
| 다른 태스크가 먼저 저장 | 예산 예약 뒤 호출 직전에 다른 서비스 인스턴스가 같은 키의 날짜를 저장 | 그 날짜는 조회하지 않음 |
| 배포 후 유지 | 서비스 인스턴스를 새로 만들어 메모리 상태 없이 같은 지난 범위 요청 | 대역 호출 없이 저장 값으로 200, `admin_analytics_refreshed` 기록 없음 |
| 정의 변경 | 코호트 ID 설정을 바꾼 뒤 같은 범위 요청 | 매개변수 해시가 달라 새 키로 다시 조회, 옛 행은 남음 |
| 같은 사용자의 국내와 해외 | 한 앱 사용자가 같은 날 국가 한국 이벤트와 국가 미국 로그인 이벤트를 남김, 웹 활동 없음 | 앱·국내 1, 앱·해외 로그인 1이라 `android` 2, `total` 2 |
| 합을 이루는 조회 하나 실패 | 빈 저장소에서 앱·해외 로그인 `_active` 조회만 대역 500, 나머지 조회 성공 | 나머지 값은 저장, 준비된 날짜가 없어 503<br>`android`와 `total`을 앱·국내 값만으로 내지 않음<br>쿨다운 뒤 실패한 조회부터 다시 보냄 |
| 국가 조건 변경 뒤 | 결정 29 전 조건으로 저장된 분석 지표 행이 있는 범위 요청 | 웹과 앱·국내 행은 해시가 같아 그대로 쓰고 앱·해외 로그인 조회만 새 키로 받음 |
| 저장 실패 | upsert 예외 | 받은 값으로 200, `admin_analytics_store_failed`, 다음 요청에서 그 날짜를 다시 조회 |
| 응답 범위 | 저장 행 | 회원 식별자 없음, 값은 집계 수치뿐 |
| 새벽 배치 시작 | 고정 시계 KST 02:55와 03:00에 배치 실행 | 02:55는 새벽 배치 조회 없음<br>03:00부터 기본 지표 키의 어제 날짜 조회 |
| 새벽 배치 대상 | 03:00 실행 | 분석 지표, 사용자 활동, `segment` `all`의 세션, `segment` `all`의 기능 사용 `all`, `web`, `android`, 종료일 없는 캠페인 추이, 신규 가입자 플랫폼, `segment` `all`의 턴 도달률과 채팅 옵션 플랫폼의 어제 날짜와 확정 전 리텐션 코호트만 조회<br>퍼널, 유입 소스, MAU, 푸시 열람, 종료일 있는 캠페인, `segment` `guest`와 `member` 조회 없음 |
| 새벽 배치 리텐션 기간 | 03:00 실행, 확정 전 코호트 D-33과 D-34가 오늘 받은 값 없음 | 새벽 배치는 D-33까지 조회<br>D-34는 새벽 배치가 끝난 뒤 초기 백필이 조회 |
| 새벽 배치 이어 받기 | 그날 새벽 작업 비용이 배치 몫 300을 넘음 | 첫 실행은 300 이하만 예약하고 `admin_analytics_backfill`의 `phase` `nightly`, `result` `partial`, `reason` `budget_share`<br>5분 뒤 실행이 남은 키를 받아 `done` |
| 새벽 배치 완료 판단 | 그날 새벽 배치를 마친 뒤 실행 | 새벽 배치 조회 없이 초기 백필로 넘어감 |
| 단일 실행 | 서비스 인스턴스 둘이 같은 5분 슬롯에 실행 | 한 인스턴스만 슬롯 키를 잡아 조회하고 다른 인스턴스는 대역 호출과 로그 없음 |
| 슬롯 선점 실패 | Redis 예외 | 대역 호출 없음, `result` `skipped`, `reason` `claim_failed`<br>다음 실행은 정상 |
| 백필 범위와 순서 | 시작일 2026-07-01, 오늘 2026-10-23, 분석 지표가 2026-08-01부터 2026-10-21까지 저장된 상태 | 분석 지표는 2026-07-31부터 거꾸로 2026-07-01까지만 조회<br>캠페인 추이는 그 캠페인의 시작일부터 |
| 백필 종료 | 마지막 비어 있는 확정일을 받은 실행과 그다음 실행 | 앞 실행은 `phase` `backfill`, `result` `done`<br>뒤 실행은 대역 호출과 로그 없음 |
| 화면 요청 우선 | 같은 5분에 화면 요청이 400을 쓴 뒤 배치 실행<br>배치가 300을 쓴 뒤 화면 요청 | 배치는 100까지만 예약<br>화면 요청은 200까지 예약해 부분 응답 |
| 배치 키 실패 | 기본 지표 키 하나의 조회가 500 | 그 키에 쿨다운, 다음 키는 계속, `result` `partial` |
| 배치 한도 초과 | 조회가 429 | 그 실행을 끝내고 `reason` `rate_limited` |
| 배치 예외 격리 | 배치 안에서 예상하지 못한 예외 | 스케줄러가 멈추지 않고 다음 5분 실행이 돎 |

<br>

### 5-5-13 인프라 지표와 DB 테이블 크기

| 확인 항목 | 입력과 상황 | 기대 결과 |
|---|---|---|
| 조회 구성 | 운영과 같은 설정(서비스 3개, Redis 노드 2개, 모든 리소스) | `GetMetricData` 질의 29개(ECS는 서비스마다 CPU와 메모리의 `Average`와 `Maximum`), 지표와 통계와 차원이 계약의 표와 같음<br>`TargetResponseTime`은 `p95`<br>`DescribeServices` 한 번에 서비스 3개 |
| 기본 기간 | 쿼리 없음, 고정 시계 2026-10-23 09:00 KST | `from`과 `to`가 2026-10-23, 조회 시작 2026-10-23 00:00 KST, 끝 09:00 KST, `periodSeconds` 300 |
| 지난 날짜 끝 | `from=2026-10-20&to=2026-10-21` | 조회 끝이 2026-10-22 00:00 KST |
| 집계 간격 | 기간 2일, 3일, 7일, 8일, 31일 | `periodSeconds` 300, 900, 900, 3600, 3600 |
| 오래된 시작 | 오늘에서 64일 전부터 2일 | `periodSeconds` 3600 |
| 기간 오류 | 32일, `to` 내일, `from`만, `from`이 `to`보다 뒤 | 전부 400, 대역 호출 없음 |
| 단위 변환 | `TargetResponseTime` 0.123, `ReadLatency` 0.0008, OpenSearch `FreeStorageSpace` 1024 | `responseTimeP95Ms` 123, `readLatencyMs` 0.8, `freeStorageBytes` 1,073,741,824 |
| 건수 0 채움 | 2시간 범위의 300초 간격에서 `RequestCount`가 24구간 중 3구간만 옴 | `requests` 점 24개, 나머지 21개는 0 |
| 비건수 빈 구간 | `CPUUtilization`이 24구간 중 20구간만 옴 | `cpu` 점 20개, 채우지 않음 |
| 태스크 수 | 대역이 `server` 실행 2, 목표 2, 시작 중 0 | `ecs.services[0]`의 `runningTasks` 2, `desiredTasks` 2, `pendingTasks` 0 |
| 최댓값 통계 | `CPUUtilization`의 `Average` 7.4, `Maximum` 21.0 | `cpu` 7.4, `cpuMax` 21.0 |
| 서비스 실패 항목 | `DescribeServices`의 `failures`에 `ai` | 503, `reason` `aws_error`, `service` `ecs` |
| 묶음 설정 없음 | Redis 노드 설정만 빈 값 | `redis`가 `null`, Redis 질의 없음, 나머지 묶음 정상 |
| 계정 ID 없음 | OpenSearch 도메인은 있고 계정 ID가 빈 값 | `opensearch`가 `null` |
| 설정 전부 없음 | 모든 리소스 설정이 빈 값 | 대역 호출 없이 503, `reason` `not_configured` |
| 권한 거부 | 대역이 `AccessDeniedException` | 503, `reason` `access_denied`, `error_code` 기록 |
| 호출 제한 | 대역이 `ThrottlingException` | 503, `reason` `throttled` |
| 시간 초과 | 대역이 5초 무응답 | 503, `reason` `timeout` |
| 이어 받기 | `GetMetricData`가 `NextToken`으로 두 번에 나눠 응답 | 두 응답의 점을 합친 하나의 응답 |
| 불완전 결과 | 이어 받은 뒤에도 `RequestCount` 결과의 `StatusCode`가 `PartialData`<br>캐시 없음 | 503, `reason` `incomplete`, 0으로 채운 점을 만들지 않고 캐시 미갱신 |
| 질의 오류 | 한 질의 결과의 `StatusCode`가 `Forbidden`이나 `InternalError`<br>같은 범위의 만료된 캐시 있음 | 200과 캐시 값, 캐시 미갱신, `reason` `incomplete` |
| 캐시 | 60초 안에 같은 범위 두 번 | 대역 호출은 처음 한 번 |
| 범위별 캐시 | 다른 `from`으로 요청 | 대역을 따로 호출 |
| 캐시 만료 | 고정 시계를 61초 뒤로 옮긴 뒤 같은 범위 | 대역 재호출 |
| 실패와 캐시 | 같은 범위의 만료된 캐시가 있고 대역 500 | 200과 캐시 값 |
| 쿨다운 | 실패 뒤 30초 안에 같은 범위 재요청 | 대역 호출 없이 503 또는 캐시 |
| 응답의 이름 | 정상 응답 | 계정 ID, ALB ARN 접미사, RDS 인스턴스 이름, OpenSearch 도메인 이름이 본문에 없음 |
| 격리 | 대역 500 상태에서 요약, 차트, DB 테이블 크기 호출 | 모두 영향 없음 |
| 테이블 정렬 | 카탈로그 대역이 전체 크기 300, 100, 200인 테이블 셋 | `tables`가 300, 200, 100 순서, `tableCount` 3 |
| 테이블 개수 | `limit=2`<br>`limit=0`, `101`, `abc` | 2개, `tableCount`는 전체 수<br>전부 400 |
| 테이블 캐시 | 5분 안에 같은 `limit` 두 번 | 카탈로그 조회는 처음 한 번 |
| 실제 쿼리 | 로컬 PostgreSQL에 붙인 HTTP 요청 파일로 호출 | `pg_catalog`과 `information_schema` 테이블이 없고 각 행의 `tableBytes`와 `indexBytes` 합이 `totalBytes` 이하 |
