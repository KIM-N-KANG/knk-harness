# CHAT IOS 클라이언트

작성 규칙: [클라이언트 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md).

공통 계약: [CLIENT](../AGENTS.md). 플랫폼 기반: [IOS 기반](../../../../platform/CLIENT/IOS/AGENTS.md), [공통 UI IOS](../../../../ui/IOS/AGENTS.md).

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항: iOS |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성: iOS |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름: iOS |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: iOS |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: iOS |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: iOS |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: iOS |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: iOS |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 배포: iOS |
| [DECISIONS.md](DECISIONS.md) | IOS 결정 기록 |

<br>

### 2 코드 위치

iOS 저장소 `manyak-ios`는 생성 전이다. 아래는 이 세트를 구현할 계획 모듈이며 파일 링크를 두지 않는다.

| 계획 모듈 | 맡는 범위 |
|---|---|
| `ManyakChat` | 채팅 목록과 채팅방, SSE 열기와 해석, 생성 따라가기, 채팅 설정과 안내, 채팅 메뉴, 공유 발급과 전달, `ChatStarter` 구현 |
| `ManyakMy` | 피드백 화면과 제출 |
| `ManyakDesignSystem` | 본문 텍스트와 이미지 조각 파서, 인물 이미지, 전체 화면 이미지 뷰어, 마스코트와 순환 문구 |
| `ManyakReport` | 채팅 메뉴와 목록 옵션의 참조 스토리 신고 |
| 앱 타깃 `Manyak` | 채팅방 라우트 쌓기와 교체, 포크한 방 쌓기, 삭제 뒤 채팅 탭 복귀, 장면 단계 전달 |

<br>

### 3 작성과 검증

- 공통 입력과 복구 의미를 유지하고 플랫폼의 수명, 공유 수단과 저장 위치를 구분한다.
- 새 계약 없이 구현 결과로 요구를 바꾸지 않는다. 확정 ADR과 기존 QA의 조건 및 기대 결과를 보존한다.
- 링크, 앵커, 유저 스토리와 QA ID, 단계 역참조를 검사하고 `git diff --check`를 실행한다.
- 검증 수단과 실제 실행 결과를 구분한다. 실행 환경과 결과는 PR과 CI에 남긴다.
- 명세 작성과 검토를 서브에이전트에 맡기지 않는다.
