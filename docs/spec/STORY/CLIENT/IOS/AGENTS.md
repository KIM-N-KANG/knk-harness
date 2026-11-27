# STORY IOS 클라이언트

작성 규칙: [클라이언트 가이드](../../../../reference/CLIENT-SPEC-WRITING-GUIDE.md).

공통 계약: [CLIENT](../AGENTS.md).

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
| [DECISIONS.md](DECISIONS.md) | STORY iOS 결정 기록 |

앱 셸, 탭 스택과 외부 진입은 [공통 UI IOS](../../../../ui/IOS/AGENTS.md), 모듈 의존, 상태 수명과 저장 원칙은 [IOS 기반](../../../../platform/CLIENT/IOS/AGENTS.md)에서 확인한다.

<br>

### 2 코드 위치

iOS 저장소 `manyak-ios`는 생성 전이다. 아래는 이 세트를 구현할 계획 모듈이며 파일 링크를 두지 않는다.

| 계획 모듈 | 맡는 범위 | Android 대응 |
|---|---|---|
| `ManyakHome` | 홈 섹션, 탐색 목록과 새로 섞기, 스토리 검색과 기기 최근 검색어, `PopularOriginalStories` 구현 | `feature/home` |
| `ManyakStory` | 스토리 상세, 채팅 시작 시트, 좋아요, 상세 옵션과 이미지 뷰어 연결 | `feature/story` |
| `ManyakStudio` | 제작 카드 조합, 완성 중 카드 조회, 검수 제출본 목록과 삭제, `StoryDeletion` 구현 | `feature/studio` |
| `ManyakCreate` | 방식 선택, 간편 제작, 일반 제작, 수정과 재제출, 초안 저장, 제작 데이터베이스(GRDB), 완성 요청 실행, 제작 이미지 업로드, 제작 안내 기록 저장, `CreationProgressAccess` 구현 | `feature/create` |
| `ManyakOnboarding` | 신규 가입 온보딩과 온보딩 표시 저장 | `feature/onboarding` |
| `ManyakCommon` | 초안 접근, 채팅 시작과 인기 오리지널 조회 계약, 제작 안내 단계와 진행 기록 계약 및 절차, `StorySummary` | `core/common` |
| `ManyakDesignSystem` | 스토리 카드, 표지 뱃지와 장르 뱃지 줄, 옵션 시트, 이미지 뷰어, 선택 테두리, 마스코트와 순환 문구, 제작 안내 대화창 | `core/designsystem` |
| `ManyakNavigation` | 상세, 제작 단계, 일반 제작, 수정과 재제출 라우트 값 | `core/navigation` |
| 앱 타깃 `Manyak` | 탐색 탭 진입 판정, 제작 흐름의 스택 교체와 탭 복귀, 온보딩과 메인 셸 전환, 가입 시 호출 목록 등록 | `app` |

옮겨 올 Android 원본은 [IOS 기반 코드 위치](../../../../platform/CLIENT/IOS/AGENTS.md#2-코드-위치)의 기준 커밋이다. 제작 데이터베이스의 원본 스키마는 그 커밋의 `feature/create/schemas/` 아래 버전 6이다.

<br>

### 3 작성과 검증

- 공통 입력과 복구 의미를 유지하고 플랫폼의 수명, 공유 수단과 저장 위치를 구분한다.
- 새 계약 없이 구현 결과로 요구를 바꾸지 않는다. 확정 결정과 기존 QA의 조건 및 기대 결과를 보존한다.
- 링크, 앵커, 유저 스토리와 QA ID, 단계 역참조를 검사하고 `git diff --check`를 실행한다.
- 검증 수단과 실제 실행 결과를 구분한다. 실행 환경과 결과는 PR과 CI에 남긴다.
