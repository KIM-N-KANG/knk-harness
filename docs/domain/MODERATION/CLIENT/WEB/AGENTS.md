# MODERATION 웹 클라이언트

단계마다 공통 문서 다음 해당 플랫폼 문서를 읽는다. 사용자 목표, 요구사항, 화면, 연동과 구현, 검증 순서다.

공통: [CLIENT](../AGENTS.md).

### 문서 역할

| 문서 | 내용 |
|---|---|
| [LAYOUT.md](LAYOUT.md) | 웹 MODERATION 표현 |
| [COMPONENT-ARCHITECTURE.md](COMPONENT-ARCHITECTURE.md) | 웹 MODERATION 구성 |
| [STATE-MANAGEMENT.md](STATE-MANAGEMENT.md) | 웹 MODERATION 상태 관리 |
| [VERIFICATION.md](VERIFICATION.md) | 웹 MODERATION 검증 |

### 코드 대응

- [src/features/stories/_shared/components/story-report-sheet.tsx](../../../../../../manyak-web/src/features/stories/_shared/components/story-report-sheet.tsx)
- [src/features/stories/_shared/constants/story-report.ts](../../../../../../manyak-web/src/features/stories/_shared/constants/story-report.ts)
- [e2e/stories/story-detail.spec.ts](../../../../../../manyak-web/e2e/stories/story-detail.spec.ts)

### 작성과 검증

- 새로운 신고 기준이나 제재 결과를 구현에서 추측하지 않는다.
- 과거 ADR은 원래 소유 범위에 보존하고 현재 계약으로 대체하지 않는다.
- 링크와 앵커, ID 중복, 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.
