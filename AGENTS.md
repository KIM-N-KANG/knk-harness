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

| 작업 상황 | 먼저 확인할 문서 |
| --- | --- |
| 도메인 용어 정의, 한↔영 표기, 계층별 네이밍 컨벤션 확인 | `docs/product-specs/0-glossary.md` |
| 서비스 배경, 타겟 사용자, MVP 범위 확인 | `docs/product-specs/1-background.md` |
| 화면·기능별 사용자 요구(유저 스토리) 확인 | `docs/product-specs/2-user-stories.md` |
| 클라이언트 공통 화면, 상태, 사용자 흐름, API 사용 계약 확인 | `docs/product-specs/3-1-client.md` |
| 웹 라우팅, BFF 프록시·토큰 세션, 브라우저 지원, 웹 검수 기준 확인 | `docs/product-specs/3-2-web-app.md` |
| 안드로이드 앱(Jetpack Compose) 플랫폼 구현 기준 확인 | `docs/product-specs/3-3-android-app.md` |
| 안드로이드 모듈 소유권·내부 계층·의존 규칙 확인 | `docs/planning/android-module-architecture.md` (3-3에서 위임) |
| 백엔드 API, 데이터 모델, 오류 처리, 운영 기준 확인 | `docs/product-specs/4-backend.md` |
| AI 기능·입출력·실패 계약·평가 시스템 확인 | `docs/product-specs/5-1-ai-server-spec.md` |
| AI 설계의 배경·대안·선택 근거 확인 | `docs/product-specs/5-2-ai-server-ard.md` |
| 분석 이벤트, 핵심 지표, 관측 구현, 릴리스 검수 기준 확인 | `docs/product-specs/6-analytics.md` |
| 운영·개발·통합 배포, 인프라, CI/CD, 검수·롤백 기준 확인 | `docs/product-specs/7-deployment.md` |
| Phase별 개발 로드맵, 마일스톤, 스프린트 일정, 백로그 확인 | `docs/planning/roadmap.md` |
| Pull Request 생성 시 영역별 PR 템플릿 확인 | `docs/templates/pull-request/` |
| 에러 제보·기능 요청을 슬랙으로 보낼 때 메시지 구조 확인 | `docs/templates/slack-report.md` |

## Agent Skills

- 브랜치 생성, 커밋, PR 생성 등 팀 워크플로 스킬은 `.agents/skills/`에 있습니다. 스킬을 자동 로드하지 않는 에이전트는 해당 작업 전에 관련 `SKILL.md`를 직접 확인합니다.

## Working Principle

- 시스템·권한 정책을 준수하는 범위에서 사용자의 명시적 요청을 우선합니다. 서비스 레포지토리의 구체적인 기술 규칙은 범용 스킬의 권고보다 우선합니다.
- 기존 코드와 문서로 판단할 수 있는 구현 세부사항은 합리적으로 결정하고 진행합니다. 제품 정책·API 계약·변경 범위에 영향을 주는 불확실성만 질문하며, 답변과 무관하게 진행 가능한 작업은 계속합니다.
- 지침 때문에 확인을 요청하거나 작업을 중단할 때는 해당 파일의 경로 또는 링크와 정확한 문구, 적용 이유를 알립니다. 명시적인 요구사항과 에이전트의 해석을 구분하고, 이미 승인된 작업은 같은 이유로 다시 확인하지 않습니다.
- 레포지토리에 없는 제품 정책, 이벤트 이름, 로그 필드, API 계약은 추측하지 않습니다.
- 제품 동작이나 분석 기준을 바꾸는 작업은 관련 `docs/product-specs/` 문서를 함께 확인합니다.
- 실제 secret, 로컬 전용 파일, 사용자 입력 원문, 프롬프트 전문, 채팅 원문은 문서나 예시에 넣지 않습니다.
