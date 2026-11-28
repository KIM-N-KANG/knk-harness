# 3 실행: iOS

기준: [상태 관리](2-STATE-MANAGEMENT.md).

<br>

### 3-1 요청과 취소

| 대상 | 규칙 |
|---|---|
| 중복 요청 | 작업 종류마다 `Task` 핸들을 들고 실행 중이면 새 요청을 무시(single-flight) |
| 새로고침 | 이전 작업을 취소하고 새로 시작. 취소된 작업의 늦은 결과는 Event로 보내지 않음 |
| 화면 이탈 | 화면이 계층에서 빠지면 Store가 보관한 작업 핸들을 모두 직접 취소. 작업이 Store를 강하게 잡아 해제를 막지 않게 함 |
| 취소 | `CancellationError`와 `URLSession`의 취소 오류는 실패로 바꾸지 않음. 오류 표시, 보고와 분석 이벤트 없음 |
| 재시도 | 한 계층에서만 담당. 소셜 로그인과 계정 연동은 자동 반복하지 않음 |
| 무거운 작업 | 데이터베이스 접근, 큰 응답 디코딩과 이미지 처리는 메인 액터 밖에서 실행 |
| 실행 계기 | `body` 재평가, 반복되는 `onAppear`와 `.task` 시작을 도메인 호출의 계기로 삼지 않음. 첫 조회는 Store가 한 번만 시작 |

저장이 필요한 결과는 Effect 소비에만 의존하지 않는다. 요청 함수는 취소만 `CancellationError`로 던지고 그 밖의 실패는 `DomainResult`의 실패로 돌려준다.

<br>

### 3-2 네트워크 요청

`ManyakNetwork`는 `URLSession`의 async 메서드 위에 요청 래퍼를 둔다. 인증이 없는 클라이언트(로그인, 재발급)와 인증 클라이언트 두 가지를 두며 공통 헤더, 인증과 오류 변환은 이 래퍼에서만 처리한다. 헤더의 의미와 오류 본문 형식은 [공통 연동](../CONTRACT.md)을 따른다.

| 헤더 | 처리 |
|---|---|
| `X-Manyak-Device-Id` | 첫 요청 전에 만든 기기 ID를 모든 요청에 실음. 값이 없으면 필수 경로 요청을 보내지 않음 |
| `X-Manyak-Session-Id` | 분석 세션 값이 있을 때만 실음 |
| `X-Manyak-App-Version` | 미정(서버 선행 변경 필요). 현재 서버는 이 헤더가 있으면 분석 `platform`을 `Android`로 기록하므로 싣지 않음 ([I-019](DECISIONS.md#i-019)) |
| `X-Manyak-Request-Id` | 생성하지 않음. 응답 값을 오류의 `requestId`로 보관 |

기기 ID의 생성, 교체와 분석 SDK 주입 순서는 ACCOUNT가 정한다. 인증 클라이언트는 `ManyakAuth`가 구현한 토큰 포트로 access 토큰을 붙인다. 만료 전 선제 재발급, 401 뒤 재발급 한 번과 원 요청 재전송 한 번, 앱 전체에서 재발급을 하나만 실행하는 직렬화는 이 경계에서만 처리하며 재발급 결과별 세션 처리와 시간 기준은 ACCOUNT를 따른다. ([ACCOUNT iOS 재발급](../../../spec/ACCOUNT/CLIENT/IOS/4-4-EXECUTION.md#4-4-2-재발급))

| `DomainError` | 의미 |
|---|---|
| `Network` | 연결 실패와 시간 초과. 세션을 끝내지 않음 |
| `Serialization` | 응답 해석 실패. 계약 불일치라 재시도로 낫지 않음 |
| `Server(status, code, requestId)` | 서버 오류 응답. `requestId`는 사용자에게 보이지 않음 |
| `Unauthorized` | 인증 거절 |
| `AccountSuspended` | 정지 계정 |
| `ProviderCancelled` | 사용자가 제공자 화면을 닫음. 실패 안내와 폴백 없음 |
| `ProviderFailed(provider, diagnostic)` | 제공자 인증 실패. 제공자는 Google과 Kakao |
| `ProviderNotConfigured(provider)` | 빌드에 제공자 키가 없음. SDK 호출 전에 거름 |
| `Unknown` | 분류하지 못한 실패 |

| 입력 | 기본 변환 |
|---|---|
| `CancellationError`, `URLError`의 취소 | 변환하지 않고 `CancellationError`로 전파 |
| 그 밖의 `URLError` | `Network` |
| 성공 본문 해석 실패, 본문이 필요한 성공에 본문 없음 | `Serialization` |
| 본문 없는 성공(204 등) | 본문 해석 없이 성공 |
| 401 | `Unauthorized` |
| 403 | `AccountSuspended` |
| 그 밖의 오류 상태 | `Server`. `code`는 오류 본문의 `code`, 본문 해석 실패면 없음 |

요청마다 다른 해석이 필요하면 그 요청이 기본 변환을 바꾼다. 예를 들어 수정 요청의 403은 권한 없음으로 처리한다. `Unauthorized`와 `AccountSuspended` 결과만으로 세션을 끝내지 않으며 세션 종료는 ACCOUNT의 재발급 결과가 정한다. 오류 원인 메시지에는 URL과 헤더가 섞일 수 있으므로 사용자 문구, 분석 값과 로그에 넣지 않는다.

SSE는 `URLSession.bytes`로 받고 같은 공통 헤더와 인증 경계를 쓴다. 이벤트 해석, 시간 제한과 실패 변환은 [CHAT iOS](../../../spec/CHAT/CLIENT/IOS/4-4-EXECUTION.md#4-4-1-요청과-sse-해석)가 정한다.

<br>

### 3-3 직렬화와 시각

| 대상 | 규칙 |
|---|---|
| 직렬화 | `Codable`과 `JSONDecoder`, `JSONEncoder`. DTO는 `Data`에 두고 Domain 모델로 바꿔 넘김 |
| 알 수 없는 필드 | 무시 |
| 필수 필드 누락, 형식 불일치 | `Serialization` |
| 서버 시각 | ISO 8601 UTC. 소수 초 유무와 관계없이 해석 |
| 절대 날짜 | `Asia/Seoul` 고정 시간대와 그레고리력으로 YYYY-MM-DD를 만듦. 사용자 달력, 지역 설정과 기기 시간대에 영향받지 않음 |
| 상대 날짜 | 기기 시간대 |
| 현재 시각 | 시각을 쓰는 코드는 시계를 주입받고 현재 시각을 직접 읽지 않음 |

절대 날짜와 상대 날짜를 쓰는 화면은 공통 연동의 날짜 규칙을 따른다. ([2 응답과 날짜](../CONTRACT.md#2-응답과-날짜))

<br>

### 3-4 이미지

원격 이미지는 `ManyakDesignSystem`의 이미지 컴포넌트가 Nuke로 불러온다. 화면은 `AsyncImage`나 직접 만든 로더를 쓰지 않는다. 메모리와 디스크 캐시는 앱 전체가 하나의 Nuke 설정을 공유하고 로그아웃 정리에서 비운다. ([I-009](DECISIONS.md#i-009))

AI 본문의 인물과 장면 이미지 주소는 아래 조건을 모두 만족할 때만 요청한다. 조건이 맞지 않는 주소는 이미지로 요청하지 않으며 본문 마커의 처리는 [CHAT 계약](../../../spec/CHAT/CLIENT/4-1-CONTRACT.md#4-1-4-이미지와-텍스트)을 따른다.

| 조건 | 허용 값 |
|---|---|
| 스킴 | `https` |
| 사용자 정보와 포트 | 없음 |
| 호스트 | `cdn.manyak.app`, `dev-cdn.manyak.app` |
| 경로 | `/characters/generated/`, `/characters/originals/`, `/characters/uploaded/`, `/chat-images/`, `/scenes/originals/`로 시작하고 접두어 뒤에 경로가 더 있음 |

이미지 뷰어는 Nuke가 돌려준 원본 크기로 맞춤(fit) 그림 영역을 계산하고 현재 확대와 이동을 거꾸로 적용해 탭 위치를 판정한다. 원본 크기를 모르면 그림이 없는 것으로 본다. 화면이 URL과 닫기 콜백을 가지며 이미지 요소는 URL 검사와 실패 처리 뒤 탭을 전달한다. 분석 이벤트는 화면 Store에서 보낸다.

<br>

### 3-5 관측

Amplitude와 Firebase Crashlytics만 사용한다. Firebase Analytics, Meta SDK, 광고 식별자, App Tracking Transparency 요청과 설치 귀속은 두지 않는다. ([I-010](DECISIONS.md#i-010))

| 대상 | 규칙 |
|---|---|
| 초기화 | 앱 타깃이 시작 때 한 번. 첫 이벤트와 `setOnce` 사용자 속성 전에 기기 ID를 Amplitude에 주입하고 같은 대기열로 처리 |
| Amplitude 키 | 빌드 구성별 키. 값이 비면 SDK를 만들지 않고 Debug는 콘솔에만 남김 |
| 사용자 | 로그인은 공개 사용자 ID를 Amplitude와 Crashlytics에 연결. 로그아웃은 세션 정리 순서에 맞춰 사용자 해제와 기기 ID 교체 |
| 이벤트 | [분석 기준](../../../reference/ANALYTICS.md)의 앱 이벤트 이름과 프로퍼티를 그대로 사용. 플랫폼 구분은 SDK 자동 수집 값이며 iOS SDK가 싣는 `platform` 값은 확인하지 않음 |
| 발화 위치 | Store와 관측 어댑터. reducer와 `body`에서 관측 호출 금지. 화면 노출 이벤트는 화면 표시 한 번에 한 번 |
| `error_type` 값 | 분석 기준이 `DomainError` 종류로 정한 이벤트에 한해 고정 문자열 `Network`, `Serialization`, `Server`, `Unauthorized`, `AccountSuspended`, `ProviderCancelled`, `ProviderFailed`, `ProviderNotConfigured`, `Unknown`으로 보냄. Swift case 이름이나 타입 설명을 그대로 쓰지 않음. 이벤트가 따로 값을 정했으면 분석 기준의 값을 씀 |
| Crashlytics 키 | 지속 키는 `screen_name`, `feature`, 필요할 때 공개 `story_id`, `chat_id`. `request_id`는 실패한 그 요청의 non-fatal에만 |
| 행동 기록 | 화면 이름과 P0 행동 이벤트 이름만 Crashlytics 로그로 남김. Amplitude 어댑터에서 한 번 연결 |
| 보고 대상 | 처리되지 않은 크래시, 예상하지 못한 네트워크, 파싱과 5xx non-fatal |
| 보고 제외 | 토큰, 입력 원문, 개인정보, URL 원문, 예상한 4xx, 취소와 제공자 로그인 취소 |
| 수집 범위 | Release만 수집하고 Debug는 끔. 앱 멈춤(hang)의 수집 범위는 확인하지 않음 |
