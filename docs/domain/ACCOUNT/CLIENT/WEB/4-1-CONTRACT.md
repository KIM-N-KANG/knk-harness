# 4-1 ACCOUNT 웹 연동 계약

<br>

### 4-1-1 인증과 게스트 API

서버 요청 형식과 응답 해석은 공통 계약을 사용한다. ([공통 4-1](../4-1-CONTRACT.md))

| 웹 경로 | 계약 |
|---|---|
| `/api/auth/[...nextauth]` | Auth.js 로그인, 콜백, 세션과 연동 전용 `link-*` |
| `/api/auth/signup-consent` GET | 가입 대기의 동의 상태와 만료 시각. 없으면 404. `no-store`, 대기 코드 노출 금지 |
| 같은 경로 DELETE | 대기 쿠키 삭제. 서버 코드는 TTL로 만료 |
| `/api/auth/session-refresh` POST | 브라우저의 단일 재발급. 204, 확정 만료 401과 `x-manyak-session-expired: 1`, 일시 실패 503 |
| `/api/auth/popup-complete?attempt=<UUID>` | `authenticated`, `consentRequired`만 알림. 토큰과 회원 정보 전송 금지 |
| `/api/v1/guests/consents` GET과 POST | `guestPrivacy.requiredVersion`, `needsConsent` 조회 및 해당 버전 저장. 같은 버전과 `false` 응답으로 완료 확인 |

공용 BFF 프록시의 헤더와 요청 타임아웃은 공통 웹 구조를 사용한다. ([BFF 프록시](../../../../client/WEB/AGENTS.md), [요청 타임아웃](../../../../client/WEB/AGENTS.md))

<br>

### 4-1-2 법적 콘텐츠

| 항목 | 연동 |
|---|---|
| 본문 | 웹 법적 콘텐츠 모듈의 시행일, 표시 버전과 본문 |
| Android 공급 | `WEB_BASE_URL/terms`, `/privacy`의 같은 본문을 WebView로 표시 |
| 동의 요구 버전 | 백엔드 `MANYAK_LEGAL_TERMS_VERSION`, `MANYAK_LEGAL_PRIVACY_VERSION` |
| 개정 | 재동의가 필요한 개정만 요구 버전 변경. 그 밖의 문구 개정은 공지 후 시행일부터 적용 |
| 시행일 | 공지 기간과 실제 공개일 확인. 미래 시행일을 현재 시행본으로 표시하지 않음 |

본문 변경 자체가 서버의 요구 버전을 바꾸지 않는다. ([공통 2-2-2 문서 동일성과 버전 구분](../2-2-REQUIREMENTS.md#2-2-2-로그인과-동의))
