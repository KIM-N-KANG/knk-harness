# MODERATION 웹 클라이언트

공통: [CLIENT](../AGENTS.md).

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: 웹 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: 웹 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: 웹 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: 웹 |

### 2 코드 대응

- [src/features/stories/_shared/components/story-report-sheet.tsx](../../../../../../manyak-web/src/features/stories/_shared/components/story-report-sheet.tsx)
- [src/features/stories/_shared/constants/story-report.ts](../../../../../../manyak-web/src/features/stories/_shared/constants/story-report.ts)
- [e2e/stories/story-detail.spec.ts](../../../../../../manyak-web/e2e/stories/story-detail.spec.ts)

### 3 작성과 검증

- 새로운 신고 기준이나 제재 결과를 구현에서 추측하지 않는다.
- 과거 ADR은 원래 소유 범위에 보존하고 현재 계약으로 대체하지 않는다.
- 링크와 앵커, ID 중복, 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.
