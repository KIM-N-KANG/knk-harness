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

- 제품 문서는 `docs/spec/`, `docs/design/`, `docs/adr/`에 둡니다. 배경 문서도 `docs/spec/`에 포함합니다. 숫자 접두어는 폴더별로 독립적으로 관리하며, 다른 폴더의 마지막 번호를 이어받지 않습니다.
- 클라이언트는 Spec에서 `3-1` 공통·`3-2` 웹·`3-3` Android, Design에서 `1-1` 웹·`1-2` Android, ADR에서 `1-1` 공통·`1-2` 웹·`1-3` Android를 사용합니다. Android 모듈 구조는 Android Design에 통합하며 없는 역할의 파일을 번호를 채우려고 만들지 않습니다.

| 작업 상황 | 먼저 확인할 문서 |
| --- | --- |
| 도메인 용어 정의, 한↔영 표기, 계층별 네이밍 컨벤션 확인 | `docs/spec/0-glossary.md` |
| 서비스 배경, 타겟 사용자, MVP 범위 확인 | `docs/spec/1-background.md` |
| 화면·기능별 사용자 요구(유저 스토리) 확인 | `docs/spec/2-user-stories.md` |
| 클라이언트 공통 화면, 상태, 사용자 흐름, API 사용 계약 확인 | `docs/spec/3-1-client-spec.md` |
| 공통 클라이언트 결정의 맥락·선택·이유 확인 | `docs/adr/1-1-client-adr.md` |
| 웹 전용 사용자 계약·라우팅·브라우저 지원 확인 | `docs/spec/3-2-web-spec.md` |
| 웹 BFF·토큰 세션·저장·렌더 구조 확인 | `docs/design/1-1-web-design.md` |
| 웹 기술 결정의 맥락·선택·이유 확인 | `docs/adr/1-2-web-adr.md` |
| Android 사용자 계약·플랫폼 차이 확인 | `docs/spec/3-3-android-spec.md` |
| Android 기술 스택·상태·인증·내비게이션 구조 확인 | `docs/design/1-2-android-design.md` |
| Android 기술 결정의 맥락·선택·이유 확인 | `docs/adr/1-3-android-adr.md` |
| Android 모듈 소유권·내부 계층·의존 규칙 확인 | [Android Design §1-2-2](docs/design/1-2-android-design.md#1-2-2-모듈과-소유권) |
| 백엔드 API, 데이터 모델, 오류 처리, 운영 기준 확인 | `docs/spec/4-backend-server-spec.md` |
| 백엔드 모듈·저장소·동시성·운영 배선 확인 | `docs/design/2-backend-server-design.md` |
| 백엔드 결정의 맥락·선택·근거 확인 | `docs/adr/2-backend-server-adr.md` |
| AI 호출 계층·모델·프롬프트·관측 설정 확인 | `docs/design/3-ai-server-design.md` |
| AI 기능·입출력·실패 계약·평가 시스템 확인 | `docs/spec/5-ai-server-spec.md` |
| AI 설계의 배경·대안·선택 근거 확인 | `docs/adr/3-ai-server-adr.md` |
| 분석 이벤트, 핵심 지표, 관측 구현, 릴리스 검수 기준 확인 | `docs/spec/6-analytics.md` |
| 운영·개발·통합 배포, 인프라, CI/CD, 검수·롤백 기준 확인 | `docs/design/4-deployment.md` |
| Phase별 개발 로드맵, 마일스톤, 스프린트 일정, 백로그 확인 | `docs/planning/roadmap.md` |
| 클라이언트 계약 승인·적용, 플랫폼별 구현·검증 근거·Jira·계획 연결 확인 | `docs/planning/client-tracking.md` |
| 제품 문서 재구성의 적용 범위·남은 분리·검증/복구 확인 | `docs/planning/product-document-reorganization.md` |
| Pull Request 생성 시 영역별 PR 템플릿 확인 | `docs/templates/pull-request/` |
| 에러 제보·기능 요청을 슬랙으로 보낼 때 메시지 구조 확인 | `docs/templates/slack-report.md` |

## Agent Skills

- 브랜치 생성, 커밋, PR 생성 등 팀 워크플로 스킬은 `.agents/skills/`에 있습니다. 스킬을 자동 로드하지 않는 에이전트는 해당 작업 전에 관련 `SKILL.md`를 직접 확인합니다.

## Working Principle

- 시스템·권한 정책을 준수하는 범위에서 사용자의 명시적 요청을 우선합니다. 서비스 레포지토리의 구체적인 기술 규칙은 범용 스킬의 권고보다 우선합니다.
- 기존 코드와 문서로 판단할 수 있는 구현 세부사항은 합리적으로 결정하고 진행합니다. 제품 정책·API 계약·변경 범위에 영향을 주는 불확실성만 질문하며, 답변과 무관하게 진행 가능한 작업은 계속합니다.
- 지침 때문에 확인을 요청하거나 작업을 중단할 때는 해당 파일의 경로 또는 링크와 정확한 문구, 적용 이유를 알립니다. 명시적인 요구사항과 에이전트의 해석을 구분하고, 이미 승인된 작업은 같은 이유로 다시 확인하지 않습니다.
- 레포지토리에 없는 제품 정책, 이벤트 이름, 로그 필드, API 계약은 추측하지 않습니다.
- 제품 동작이나 분석 기준을 바꾸는 작업은 관련 `docs/spec/` 문서를 함께 확인합니다.
- 실제 secret, 로컬 전용 파일, 사용자 입력 원문, 프롬프트 전문, 채팅 원문은 문서나 예시에 넣지 않습니다.


## 클라이언트 문서 갱신

- 관련 절을 전체로 읽고 검색은 보조로 사용합니다. 공통 사용자 계약은 공통 spec, 플랫폼 고유 계약·예외는 해당 spec, 현재 내부 구조는 design, 중요한 선택 이유는 영역별 adr 한 파일에 씁니다. 동일 본문을 복사하지 않고 링크합니다.
- spec에는 Phase·구현/미구현 표시·Jira·작업 순서·역사적 결정 이유를 넣지 않습니다. 승인된 계약은 규범으로 쓰고 코드와의 차이는 `docs/planning/client-tracking.md`에 남깁니다. 관측된 코드만으로 제품 정책을 승인하거나 과거 이유를 추정하지 않습니다.
- 새 기능은 목표·미결 사항 확인 → 계약·적용 범위 승인 → 필요 시 ADR → 구현 저장소의 기능 계획 → 구현과 현재 spec/design 동기화 → QA·검증·배포 근거 연결 순서로 진행합니다. 미래 구조를 현재 design에 먼저 덮어쓰지 않습니다.
- 계획은 웹의 `docs/superpowers/plans/`, Android의 `docs/plans/`를 재사용합니다. 목표·승인된 변경 범위·변경 순서·검증/복구·결과 링크만 두며 완료 후 당시 실행 기록으로 보관합니다. 일정·작업 진행은 Jira, Phase는 roadmap, 문서·증거 연결은 client-tracking이 소유합니다.
- spec의 최소 구성은 범위·입력/동작/상태·예외·수용 기준, design은 책임 경계·데이터/요청 흐름·상태 수명·실패/복구입니다. 스펙과 ADR은 기존 문서의 형식을 유지하며 상단에 실제 본문과 일치하는 목차, 읽는 순서, 문서 정보 표(버전·작성일·수정일·대상·작성 목적)를 둡니다. 플랫폼 스펙에는 기준 코드, 플랫폼 ADR에는 대상 저장소를 연결합니다. ADR의 문서 작성일·수정일은 개별 결정일과 구분하고 기존 결정 ID·본문은 보존합니다. 이력은 추적 문서로 연결합니다. ADR은 [공통 기록 규칙](docs/adr/1-1-client-adr.md#기록-규칙), 추적은 해당 문서의 최소 행을 따릅니다. 새 문서 유형은 실제 책임이 추가될 때만 만듭니다.
- 문서를 이동하면 README·AGENTS/CLAUDE·계획·QA·제품 문서의 링크와 절 참조를 같은 작업에서 갱신합니다. ADR의 확정 본문과 과거 근거 링크는 보존하고 변경 결정에서 대체 ID·범위를 연결합니다.
