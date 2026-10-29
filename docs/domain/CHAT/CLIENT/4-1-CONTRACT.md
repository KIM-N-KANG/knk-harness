# 4-1 연동 계약

<br>

### 4-1-1 서버 계약과 입력

| 동작 | 기준 계약 | 클라이언트 입력과 사용 |
|---|---|---|
| 채팅 생성 | [4-2-2](../BACKEND/4-2-CONTRACT.md#4-2-2-채팅-생성) | `storyId`, 선택한 `startSettingId`, 회원의 선택 `personaId`. 생략은 서버 기본 |
| 상세 | [4-2-4](../BACKEND/4-2-CONTRACT.md#4-2-4-상세) | 제목, 프롤로그, 턴, `persona`, `model`, `longResponse`, `generatingTurn` |
| 삭제 | [4-2-5](../BACKEND/4-2-CONTRACT.md#4-2-5-삭제) | 204 완료 안내, 404 무음 성공. 다른 실패는 복구 |
| 이어쓰기 | [4-2-6](../BACKEND/4-2-CONTRACT.md#4-2-6-이어쓰기) | `userInput`, 화면 마지막 턴의 `lastTurnId`, `realtimeImage`. 첫 턴도 `lastTurnId: null` 명시 |
| 재생성 | [4-2-7](../BACKEND/4-2-CONTRACT.md#4-2-7-재생성) | 마지막 `turnId`, `realtimeImage`. 사용자 입력 재전송 없음 |
| 추천 | [4-2-8](../BACKEND/4-2-CONTRACT.md#4-2-8-선택지-생성) | 마지막 턴 대상. 200은 저장 완료 신호, 화면은 다시 받은 상세의 `choices` 사용 |
| 공유 | [발급](../BACKEND/4-2-CONTRACT.md#4-2-9-공유-발급), [열람](../BACKEND/4-2-CONTRACT.md#4-2-10-공유-열람) | 발급 ID로 서비스 origin의 `/share/{shareId}` 생성. 열람은 스냅샷 |
| 피드백 | [4-2-11](../BACKEND/4-2-CONTRACT.md#4-2-11-피드백-등록) | 앞뒤 공백을 뺀 `body`, 비어 있으면 null인 `email`, 고정 `platform` |
| 이어받기 | [4-2-13](../BACKEND/4-2-CONTRACT.md#4-2-13-생성-스트림-재연결) | `generationId`의 이벤트를 처음부터 재수신. 생성과 과금 재시작 없음 |
| 모델과 설정 | [목록](../BACKEND/4-2-CONTRACT.md#4-2-14-모델-목록), [변경](../BACKEND/4-2-CONTRACT.md#4-2-15-채팅-설정-변경) | `model` 또는 `longResponse` 중 바꾼 필드만 PATCH. 이어쓰기와 재생성 본문에 모델을 추가하지 않음 |

`realtimeImage`는 기기 설정을 항상 명시한다. 서버 기본값 true에 의존하지 않는다. 피드백 `platform`은 웹 `WEB`, Android `ANDROID`이며 사용자에게 선택받지 않는다. 피드백 서버 상한 2000자는 UI의 500자 상한과 다르다.

<br>

### 4-1-2 SSE 이벤트

POST 응답은 `Accept: text/event-stream`과 공용 `X-Manyak-*` 식별자를 사용한다. 클라이언트와 서버 사이 전달 계층은 청크를 버퍼링하지 않는다.

| 이벤트 | 필드 | 처리 |
|---|---|---|
| `started` | `chatId`, `generationId` | 생성 ID 보관. 이어받기 시작이면 진행 조각 초기화 |
| `token` | `text` | 마지막 조각이 텍스트면 이어 붙이고 아니면 새 텍스트 조각 |
| `character_image` | `name`, `imageUrl` | 도착 위치에 새 이미지 조각. 반복 이벤트도 반복 표시 |
| `completed` | `chatId`, `turnId`, `aiOutput`, `choices`, `reachedEnding` | 상세 재조회 성공 프레임에 확정 턴으로 교체. 이벤트의 별도 이미지 목록이나 choices를 렌더 기준으로 사용하지 않음 |
| `error` | `code`, `message` | 명시적 실패. 상세 확인 후 기본 실패 안내 |

`token` 데이터는 JSON의 `text`와 원문 텍스트를 모두 허용한다. 이미지 다음의 토큰은 새 텍스트 조각으로 시작한다. 이미지가 인물명 토큰보다 먼저 오면 그 순서 그대로 표시한다.

서버의 클라이언트향 전체 상한은 error 없이 EOF가 될 수 있고 AI 이벤트 간 idle 상한은 `AI_STREAM_FAILED`가 된다. 생성 마감 120초는 접수부터 세며 재연결로 늘어나지 않는다. 서버 상한의 정본은 서버 계약이다.

<br>

### 4-1-3 상세와 오류의 해석

| 값 또는 결과 | 처리 |
|---|---|
| 턴 0개 | `suggestedInputs`를 처음 추천으로 사용 |
| 턴 있음 | 마지막 `turns[].choices` 사용. 선택지가 꺼져 있으면 숨김 |
| `generatingTurn.type=CONTINUE` | `userInput` 사용자 버블과 진행 블록 |
| `generatingTurn.type=REGENERATE` | `targetTurnId` 자리에 진행 블록 |
| 402 | 회원 부족 시트, 웹 게스트 로그인 안내. 재생성은 기존 본문 유지 |
| 409 `CHAT_TURN_IN_PROGRESS` | 입력 되돌리기, 상세 확인과 진행 중 생성 이어받기 |
| 409 `CHAT_TURN_STALE` | 입력 되돌리기, 최신 상세 표시 |
| 409 `CHAT_ENDED` | 재생성 불가. 최신 상세 표시 |
| 시작 전 503 `SERVICE_UNAVAILABLE` | 생성과 과금 없음. 실패 안내 |
| 재연결 404, 503 또는 생성 ID 미확인 | 상세의 `generatingTurn.generationId`로 이어받기 시도 |
| `longResponse` 없음 | false |
| 이름 토큰 | 조회 결과는 서버가 치환한 텍스트. 클라이언트 치환 없음 |

<br>

### 4-1-4 이미지와 텍스트

| 종류 | 유효 조건과 처리 |
|---|---|
| 배경 | 인라인 `[[image:<imageKey>]]`를 `images[]`의 `{imageKey, type, url}`에 연결. 없는 키는 마커 문자열까지 숨김 |
| 인물 저장 마커 | 독립 한 줄 `[[URL]]`, 빈 줄 하나, 비어 있지 않은 `인물명:` 대사 라벨, 허용 URL. 이름은 대체 텍스트에 사용 |
| 장면 저장 마커 | 독립 한 줄 `[[URL]]`과 허용된 `/scenes/originals/` 경로. 대사 라벨 없이 장면 이미지, 주변 빈 줄은 블록 간격으로 대체 |
| 불일치 | 인물 저장 마커 조건이 안 맞으면 요청하거나 제거하지 않고 일반 본문으로 유지 |
| 반복 | 유효한 마커도 위치와 횟수대로 표시. 이름으로 합치지 않음 |
| 호환 | 이전 `[[인물이름:URL]]` 형식이나 별도 인물 이미지 목록에 의존하지 않음 |
| 공용 파싱 | 이어쓰기, 재생성, 확정 상세, 공유본, 프롤로그와 스토리 상세 상황 설명에 같은 해석 |
| 미리보기 | 공유 설명의 프롤로그 발췌에서 이미지 마커 줄 제거 |

허용 URL은 플랫폼에서 검사하며 임의 생성 문자열을 이미지 요청으로 보내지 않는다. 표현은 앞 단계 계약을 따른다. ([3-3-4](3-3-LAYOUT.md#3-3-4-생성-대기와-이미지))
