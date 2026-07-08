# KNK Workspace LLM Working Harness

## Repository Context

- 제품·스펙 문서는 현재 레포지토리(`knk-harness/`)를 기준으로 확인합니다.
- 구현 맥락이 필요하면 현재 레포지토리만 보지 말고 다음 서비스 레포지토리를 함께 참조합니다.

| 영역 | 참조 경로 |
| --- | --- |
| 웹 프론트엔드 | `../manyak-web` |
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
| 프론트엔드 화면, 상태, 사용자 흐름, 검수 기준 확인 | `docs/product-specs/3-frontend.md` |
| 백엔드 API, 데이터 모델, 오류 처리, 운영 기준 확인 | `docs/product-specs/4-backend.md` |
| AI 기능, 요청·응답 계약, 프롬프트, 실패 처리 기준 확인 | `docs/product-specs/5-ai-server.md` |
| 분석 이벤트, 핵심 지표, 관측 구현, 릴리스 검수 기준 확인 | `docs/product-specs/6-analytics.md` |
| 운영·개발·통합 배포, 인프라, CI/CD, 검수·롤백 기준 확인 | `docs/product-specs/7-deployment.md` |
| Phase별 개발 로드맵, 마일스톤, 스프린트 일정, 백로그 확인 | `docs/planning/roadmap.md` |
| Pull Request 생성 시 영역별 PR 템플릿 확인 | `docs/templates/pull-request/` |

## Agent Skills

- 브랜치 생성, 커밋, PR 생성 등 팀 워크플로 스킬은 `.agents/skills/`에 있습니다. 스킬을 자동 로드하지 않는 에이전트는 해당 작업 전에 관련 `SKILL.md`를 직접 확인합니다.

## Working Principle

- 레포지토리에 없는 제품 정책, 이벤트 이름, 로그 필드, API 계약은 추측하지 않습니다.
- 제품 동작이나 분석 기준을 바꾸는 작업은 관련 `docs/product-specs/` 문서를 함께 확인합니다.
- 실제 secret, 로컬 전용 파일, 사용자 입력 원문, 프롬프트 전문, 채팅 원문은 문서나 예시에 넣지 않습니다.
