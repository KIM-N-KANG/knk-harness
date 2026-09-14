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

작업과 관련된 문서만 선택합니다. 웹·Android의 사용자 계약은 공통 Spec과 해당 플랫폼 Spec을 함께 확인합니다. 내부 구조는 Design, 선택 이유는 ADR에서 확인합니다.

| 작업 상황 | 먼저 확인할 문서 |
| --- | --- |
| 용어·한영 표기·네이밍 규칙 | [용어집](docs/spec/0-glossary.md) |
| 서비스 배경·타겟 사용자·MVP 범위 | [서비스 배경](docs/spec/1-background.md) |
| 화면·기능별 사용자 요구 | [유저 스토리](docs/spec/2-user-stories.md) |

| 영역 | Spec — 계약 | Design — 현재 구조 | ADR — 결정 근거 |
| --- | --- | --- | --- |
| 공통 클라이언트 | [공통](docs/spec/3-1-client-spec.md) | 플랫폼별 Design 참조 | [공통](docs/adr/1-1-client-adr.md) |
| 웹 | [웹](docs/spec/3-2-web-spec.md) | [웹](docs/design/1-1-web-design.md) | [웹](docs/adr/1-2-web-adr.md) |
| Android | [Android](docs/spec/3-3-android-spec.md) | [Android](docs/design/1-2-android-design.md) · [모듈·의존 규칙](docs/design/1-2-android-design.md#1-2-2-모듈과-소유권) | [Android](docs/adr/1-3-android-adr.md) |
| 백엔드 | [백엔드](docs/spec/4-backend-server-spec.md) | [백엔드](docs/design/2-backend-server-design.md) | [백엔드](docs/adr/2-backend-server-adr.md) |
| AI | [AI](docs/spec/5-ai-server-spec.md) | [AI](docs/design/3-ai-server-design.md) | [AI](docs/adr/3-ai-server-adr.md) |

| 작업 상황 | 확인할 곳 |
| --- | --- |
| 분석 이벤트·지표·관측·릴리스 검수 | [분석](docs/spec/6-analytics.md) |
| 배포·인프라·CI/CD·검수·롤백 | [배포 Design](docs/design/4-deployment.md) |
| QA 작업 전 지침·검증 방법 | [웹 QA 지침](docs/qa/AGENTS.md) · [Android 검증 방법](docs/design/1-2-android-design.md#1-2-9-검증-방법) |
| Phase·목표·범위·백로그 | [로드맵](docs/planning/roadmap.md) |
| 작업 담당·상세 일정·진행 | Jira |

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

- 관련 문서의 해당 절을 전체로 읽습니다. 요구사항·동작 계약은 Spec, 현재 구현 구조는 Design, 중요한 결정의 이유는 ADR에 기록합니다. 중복 본문 대신 링크를 사용합니다.
- 제품 동작·분석 기준을 바꿀 때 관련 Spec을 확인하고, 구현 변경 시 영향받는 문서와 검증 항목을 같은 작업에서 갱신합니다. 계약·예외·보안·실패·복구 조건을 보존하며, 코드만으로 제품 정책의 승인 여부나 과거 결정 이유를 추정하지 않습니다.
- 일정·진행 상태·미결 사항은 Jira, Phase는 roadmap, 구현 계획과 검증 결과는 기존 계획 문서·PR에서 관리합니다. 현재 계약과 구조를 설명하는 문서에 작업 이력을 섞지 않습니다.
- 기존 문서 유형의 형식과 명명 규칙을 따릅니다. 코드에서 확인할 수 있는 목록은 원본 링크를 우선하며, 중복된 문서나 목록을 만들지 않습니다. `AGENTS.md`·`CLAUDE.md`는 간결한 작업 지침으로 작성합니다.
- 확정된 ADR의 ID·본문과 과거 근거를 보존합니다. 결정 변경은 해당 ADR의 기록 규칙에 따라 후속 기록에 대체하는 결정 ID와 적용 범위를 명시합니다.
- 파일이나 절을 이동·삭제·통합하거나 제목을 바꾸면 하네스와 관련 구현 저장소의 참조도 갱신합니다. 변경 후 링크·앵커·목차·ID 중복과 ADR 보존 여부를 확인하고 `git diff --check`를 실행합니다.
