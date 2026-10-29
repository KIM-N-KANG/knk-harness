# KNK Workspace LLM Working Harness

## Repository Context

- 이 파일의 상대경로는 이 파일이 위치한 하네스 루트(`knk-harness/`)를 기준으로 해석합니다. 연결된 문서와 스킬 안의 상대경로는 별도 기준이 명시되지 않았다면 해당 파일이 위치한 디렉터리를 기준으로 해석합니다.
- 제품·스펙 문서는 하네스의 `docs/`에서 작업과 관련된 항목만 확인합니다.

- 구현 맥락이 필요하면 다음 서비스 레포지토리 중 관련된 곳을 함께 참조합니다.

| 영역 | 참조 경로 |
| --- | --- |
| 웹 프론트엔드 | `../manyak-web` |
| 안드로이드 앱 | `../manyak-android` |
| 백엔드 서버 | `../manyak-server` |
| AI 서버 | `../manyak-ai` |
| 운영 Terraform | `../manyak-terraform` |
| 로컬·통합 인프라 | `../manyak-infra` |

## Knowledge Base

제품 문서는 [도메인 목록](docs/domain/AGENTS.md)에서 작업에 맞는 세트를 선택합니다. 각 도메인과 세트의 `AGENTS.md`가 문서 역할과 읽는 순서를 안내합니다.

| 도메인 | 다루는 것 | 세트 |
| --- | --- | --- |
| [ACCOUNT](docs/domain/ACCOUNT/AGENTS.md) | 계정, 로그인, 동의, 이관과 프로필 | BACKEND, CLIENT |
| [PAYMENT](docs/domain/PAYMENT/AGENTS.md) | 이프, 충전, 보상과 체험 한도 | BACKEND, CLIENT |
| [CHAT](docs/domain/CHAT/AGENTS.md) | 채팅, 선택지, 이미지, 공유와 피드백 | AI, BACKEND, CLIENT |
| [STORY](docs/domain/STORY/AGENTS.md) | 스토리 탐색, 제작, 상세, 공개와 검색 | AI, BACKEND, CLIENT |
| [MODERATION](docs/domain/MODERATION/AGENTS.md) | 검수, 15세 모드, 입력 검사와 신고 | AI, BACKEND, CLIENT |
| [NOTIFICATION](docs/domain/NOTIFICATION/AGENTS.md) | 공지, 알림함, 수신 설정과 푸시 | BACKEND, CLIENT |

- 클라이언트는 단계마다 `CLIENT/`의 공통 문서 다음 `WEB/` 또는 `ANDROID/`를 읽습니다. 여러 도메인이 사용하는 셸과 플랫폼 기반은 [공용 클라이언트](docs/client/AGENTS.md)에서 확인합니다.
- 사용자 목표는 각 CLIENT의 `2-1-USER-STORY.md`에서 정의합니다. ID는 파일과 절 번호에 독립적이며 WEB과 ANDROID가 같은 ID를 참조합니다.
- 문체와 파일명은 [제품 Spec 작성 가이드](docs/REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md), 세트별 구성은 [AI](docs/REFERENCE/AI-SPEC-WRITING-GUIDE.md), [백엔드](docs/REFERENCE/BACKEND-SPEC-WRITING-GUIDE.md), [클라이언트](docs/REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md) 작성 가이드를 따릅니다.

| 작업 상황 | 확인할 문서 |
| --- | --- |
| 용어, 한영 표기와 네이밍 | [용어집](docs/REFERENCE/GLOSSARY.md) |
| 서비스 배경과 대상 사용자 | [서비스 배경](docs/REFERENCE/SERVICE-BACKGROUND.md) |
| 분석 이벤트, 지표와 관측 | [분석 기준](docs/REFERENCE/ANALYTICS.md) |
| 공용 서비스 인터페이스와 상태 확인 | [서비스 인터페이스](docs/REFERENCE/SERVICE-INTERFACES.md) |
| 배포, 인프라, CI/CD와 복구 | [배포 Design](docs/design/4-deployment.md), [배포 ADR](docs/adr/4-deployment-adr.md) |
| 클라이언트 검증 | 공용 또는 해당 도메인의 플랫폼 세트 `5-1-VERIFICATION.md` |
| 작업 담당, 일정, 우선순위와 미결 사항 | Jira |

기존 백엔드와 AI의 통합 Design 및 ADR은 `docs/design/`과 `docs/adr/`에 보존합니다. 현재 도메인 명세가 우선이며, 과거 결정은 현재 계약을 대체하지 않습니다.

## Agent Skills

- 브랜치 생성, 커밋, PR 생성 등 팀 워크플로 스킬은 `.agents/skills/`에 있습니다. 스킬을 자동 로드하지 않는 에이전트는 해당 작업 전에 관련 `SKILL.md`를 직접 확인합니다.
- PR 생성·템플릿 선택은 [create-pr](.agents/skills/create-pr/SKILL.md), Slack 제보·양식은 [send-slack-report](.agents/skills/send-slack-report/SKILL.md)를 따릅니다.

## Working Principle

- 시스템·권한 정책을 준수하는 범위에서 사용자의 명시적 요청을 우선합니다. 서비스 레포지토리의 구체적인 기술 규칙은 범용 스킬의 권고보다 우선합니다.
- 기존 코드와 문서로 판단할 수 있는 구현 세부사항은 합리적으로 결정하고 진행합니다. 제품 정책·API 계약·변경 범위에 영향을 주는 불확실성만 질문하며, 답변과 무관하게 진행 가능한 작업은 계속합니다.
- 지침 때문에 확인을 요청하거나 작업을 중단할 때는 해당 파일의 경로 또는 링크와 정확한 문구, 적용 이유를 알립니다. 명시적인 요구사항과 에이전트의 해석을 구분하고, 이미 승인된 작업은 같은 이유로 다시 확인하지 않습니다.
- 레포지토리에 없는 제품 정책, 이벤트 이름, 로그 필드, API 계약은 추측하지 않습니다.
- 실제 secret, 로컬 전용 파일, 사용자 입력 원문, 프롬프트 전문, 채팅 원문은 문서나 예시에 넣지 않습니다.

## Documentation Guidelines

- Spec을 작성하거나 수정하기 전에 제품 Spec 작성 가이드 전체를 반드시 읽고, 문체와 표 구성, 문서 참조 규칙을 적용합니다. ([제품 Spec 작성 가이드](docs/REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md))
- 관련 문서의 해당 절을 전체로 읽습니다. 요구사항·동작 계약은 Spec, 현재 구현 구조는 Design, 중요한 결정의 이유는 ADR에 기록합니다. 중복 본문 대신 링크를 사용합니다.
- 제품 동작·분석 기준을 바꿀 때 관련 Spec을 확인하고, 계약 변경을 먼저 반영합니다. 구현 변경 시 영향받는 문서와 검증 항목을 같은 작업에서 갱신하며, 미래 구조를 현재 Design에 먼저 반영하지 않습니다. 계약·예외·보안·실패·복구 조건을 보존하며, 코드만으로 제품 정책의 승인 여부나 과거 결정 이유를 추정하지 않습니다.
- 일정, 진행 상태, 우선순위와 미결 사항은 Jira, 구현 계획과 검증 결과는 구현 저장소의 계획 문서와 PR에서 관리합니다. 현재 계약과 구조를 설명하는 문서에 작업 이력을 섞지 않습니다.
- 기존 문서 유형의 형식과 명명 규칙을 따릅니다. 코드에서 확인할 수 있는 목록은 원본 링크를 우선하며, 중복된 문서나 목록을 만들지 않습니다. `AGENTS.md`·`CLAUDE.md`는 간결한 작업 지침으로 작성합니다.
- 확정된 ADR의 ID·본문과 과거 근거를 보존합니다. 결정 변경은 해당 ADR의 기록 규칙에 따라 후속 기록에 대체하는 결정 ID와 적용 범위를 명시합니다.
- 파일이나 절을 이동·삭제·통합하거나 제목을 바꾸면 하네스와 관련 구현 저장소의 참조도 갱신합니다. 변경 후 링크·앵커·목차·ID 중복과 ADR 보존 여부를 확인하고 `git diff --check`를 실행합니다.
