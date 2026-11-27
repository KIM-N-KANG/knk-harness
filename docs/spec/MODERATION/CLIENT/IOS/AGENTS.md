# MODERATION iOS 클라이언트

공통: [CLIENT](../AGENTS.md).

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: iOS |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: iOS |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: iOS |
| [DECISIONS.md](DECISIONS.md) | MODERATION iOS 결정 기록 |

<br>

### 2 코드 위치

iOS 저장소 `manyak-ios`는 생성 전이다. 아래는 이 세트를 구현할 계획 모듈이며 파일 링크를 두지 않는다.

| 계획 모듈 | 맡는 범위 |
|---|---|
| `ManyakReport` | 신고 상태, `StoryReportController`, 신고 시트, 신고 요청과 문구 |
| `ManyakStory`, `ManyakStudio`, `ManyakChat` | 스토리 상세, 제작 목록, 채팅 목록과 채팅방의 신고 진입과 신고 상태 |
| 앱 타깃 `Manyak` | 신고 요청 구현의 조립 |

모듈 의존과 공용 포트는 [IOS 기반](../../../../platform/CLIENT/IOS/AGENTS.md)을 따른다. STORY의 입력 거절과 검수 상태는 [STORY 공통 클라이언트](../../../STORY/CLIENT/AGENTS.md)에서 확인한다.

<br>

### 3 작성과 검증

- 새로운 신고 기준이나 제재 결과를 구현에서 추측하지 않는다.
- 과거 ADR은 원래 소유 범위에 보존하고 현재 계약으로 대체하지 않는다.
- 링크와 앵커, ID 중복, 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.
