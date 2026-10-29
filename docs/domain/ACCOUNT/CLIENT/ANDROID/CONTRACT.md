# ACCOUNT Android 연동 계약

<br>

### 서버와 문서

| 대상 | 연동 |
|---|---|
| 서버 | 공통 ACCOUNT 요청과 응답 사용 |
| 소셜 로그인 | `/auth/social/{provider}`, `/auth/social/complete`. 구버전 `/auth/login/{provider}` 미사용 |
| 가입 완료 | `X-Manyak-Consent-Token`으로 대기 코드 전달. 광고 동의 답은 본문에 포함하지 않음 |
| 계정 연동 | 재인증 enum은 대문자, 공급자 경로는 소문자 |
| 법적 문서 | 설정된 웹 호스트의 HTTPS `/terms`, `/privacy`, `/about` |
| 외부 HTTP(S) | `ACTION_VIEW`, 브라우저 없으면 실패 토스트 |
| 차단 | 다른 스킴과 같은 호스트의 문서 외 페이지. 웹의 클라이언트 라우팅 링크 제거도 필요하며 WebView 검사로 대체하지 않음 |

서버 형식과 사용자 결과의 변환은 공통 계약을 사용한다. ([공통 4-1](../CONTRACT.md))

<br>

### 식별 정보

| 값 | 전달 |
|---|---|
| 기기 UUID | DataStore에 지속, 최초 로그인과 API 및 Amplitude 이벤트 전에 같은 값 주입. 빈 값 전송 금지 |
| 세션 ID | 인증과 무인증 HTTP 요청 모두 현재 SDK 값을 `X-Manyak-Session-Id`로 전달. 미설정 또는 음수이면 생략 |
| 분석 사용자 | 시작 시 이전 식별 해제. 회원 세션, 프로필과 필수 동의가 모두 준비된 뒤 설정 |

회원 체험 시드에 사용된 기기 식별자는 정상 흐름에서 되돌릴 수 없으므로 초기 주입 순서를 유지한다.
