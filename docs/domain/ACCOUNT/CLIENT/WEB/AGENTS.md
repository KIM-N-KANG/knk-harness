# ACCOUNT 웹 클라이언트

단계마다 공통 문서, 해당 플랫폼 문서 순서로 읽는다. 상위 계약은 하위 구현이나 검증 결과에 맞춰 변경하지 않는다.

```text
배경 → 유저 스토리 → 요구사항 → 화면 구성과 흐름, 배치
     → 연동 계약 → 구성 → 상태 → 실행 → 검증 → 배포
```

플랫폼 이동: [공통 CLIENT](../AGENTS.md). 작성 규칙은 [클라이언트 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md), 과거 결정은 [DECISIONS](DECISIONS.md)에서 확인한다.

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 ACCOUNT 웹 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 ACCOUNT 웹 화면과 URL |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 ACCOUNT 웹 화면 흐름 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 ACCOUNT 웹 화면 표현 |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 ACCOUNT 웹 연동 계약 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 ACCOUNT 웹 구성 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 ACCOUNT 웹 상태 관리 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 ACCOUNT 웹 실행 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 ACCOUNT 웹 검증 |

<br>

### 2 코드 대응

| 구성 | 구현 |
|---|---|
| 인증과 동의 | [src/features/auth](../../../../../../manyak-web/src/features/auth) |
| BFF와 토큰 | [src/lib/auth](../../../../../../manyak-web/src/lib/auth) |
| 프로필과 페르소나, 초대 | [src/features/my](../../../../../../manyak-web/src/features/my) |
| 법적 콘텐츠 | [src/features/legal](../../../../../../manyak-web/src/features/legal) |
| E2E | [e2e/auth](../../../../../../manyak-web/e2e/auth) |
| 단위 테스트 | [tests](../../../../../../manyak-web/tests) |

| 세부 구현 | 위치 |
|---|---|
| 인증, 가입과 프로필 세션 갱신 | [backend-session](../../../../../../manyak-web/src/lib/auth/backend-session.ts), [가입 쿠키](../../../../../../manyak-web/src/lib/auth/signup-consent-cookie.ts) |
| 회원 동의 | [consent-gate](../../../../../../manyak-web/src/features/auth/_shared/components/consent-gate.tsx), [consent-sheet](../../../../../../manyak-web/src/features/auth/_shared/components/consent-sheet.tsx) |
| 게스트 동의 | [provider](../../../../../../manyak-web/src/features/auth/_shared/components/guest-consent-provider.tsx), [응답 검증](../../../../../../manyak-web/src/features/auth/_shared/utils/guest-consent-status.ts) |
| 인증 팝업 | [start-popup-login](../../../../../../manyak-web/src/features/auth/_shared/utils/start-popup-login.ts), [start-social-login](../../../../../../manyak-web/src/features/auth/_shared/utils/start-social-login.ts) |
| 재발급 | [session-refresh-gate](../../../../../../manyak-web/src/lib/auth/session-refresh-gate.ts), [refresh-dedup](../../../../../../manyak-web/src/lib/auth/refresh-dedup.ts) |
| 이관과 정리 | [use-auto-migration](../../../../../../manyak-web/src/features/auth/_shared/hooks/use-auto-migration.ts), [clear-local-member-state](../../../../../../manyak-web/src/features/auth/_shared/utils/clear-local-member-state.ts) |
| 문구와 법적 본문 | [프로필](../../../../../../manyak-web/src/features/my/profile/constants.ts), [페르소나](../../../../../../manyak-web/src/features/my/personas/constants.ts), [이용약관](../../../../../../manyak-web/src/features/legal/content/terms-content.ts), [처리방침](../../../../../../manyak-web/src/features/legal/content/privacy-content.ts) |

<br>

### 3 작성과 검증

- 요구사항에는 사용자 결과, 화면 설계에는 배치와 전환, 구현 설계에는 책임과 수명을 작성한다.
- 공통 본문을 플랫폼별로 복제하지 않는다. 의도된 차이는 공통 적용 범위 안에서 구체화한다.
- ADR 본문과 ID를 보존한다. 현재 계약 변경은 해당 단계에서 시작하고 이후 문서에 반영한다.
- 기존 QA 케이스와 상위 요구의 연결, 링크, 앵커, ID 중복을 검사하고 `git diff --check`를 실행한다.
- 실제 검증 결과는 PR과 CI에 기록한다. 명세 작성과 검토를 서브에이전트에 맡기지 않는다.
