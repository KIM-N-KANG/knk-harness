# MODERATION AI 안내

게시물 검수 AI의 배경과 요구사항, 설계와 계약, 구현과 평가, 운영 순서로 읽는다. 도메인의 다른 세트와 입력 및 결과 경계를 함께 확인한다.

### 문서

| 문서 | 내용 |
|---|---|
| [BACKGROUND.md](BACKGROUND.md) | 1. 배경 |
| [USER-STORY.md](USER-STORY.md) | 유저 스토리 |
| [OPERATION-REQUIREMENTS.md](OPERATION-REQUIREMENTS.md) | 운영 요구사항 |
| [TASK-DEFINITION.md](TASK-DEFINITION.md) | 3. 태스크 정의 |
| [COGNITIVE-ARCHITECTURE.md](COGNITIVE-ARCHITECTURE.md) | 인지 구조 설계 |
| [SOFTWARE-ARCHITECTURE.md](SOFTWARE-ARCHITECTURE.md) | 소프트웨어 구조 설계 |
| [CONTRACT.md](CONTRACT.md) | 5. 계약 |
| [AI-EXECUTION.md](AI-EXECUTION.md) | AI 실행 |
| [SOFTWARE-IMPLEMENTATION.md](SOFTWARE-IMPLEMENTATION.md) | 소프트웨어 구현 |
| [AI-ALIGNMENT.md](AI-ALIGNMENT.md) | AI 정렬 |
| [AI-EVALUATION-METHOD.md](AI-EVALUATION-METHOD.md) | AI 평가 방법 |
| [AI-EVALUATION-IMPLEMENTATION.md](AI-EVALUATION-IMPLEMENTATION.md) | AI 평가 구현 |
| [AI-PERFORMANCE-REPORT.md](AI-PERFORMANCE-REPORT.md) | AI 성능 보고 |
| [ERROR-HANDLING.md](ERROR-HANDLING.md) | 오류 처리 |
| [TEST-CASES.md](TEST-CASES.md) | 테스트 케이스 |
| [OBSERVABILITY.md](OBSERVABILITY.md) | 관측 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 배포 |
| [DECISIONS.md](DECISIONS.md) | DECISIONS.md |

### 작업 규칙

[제품 작성 가이드](../../../reference/PRODUCT-SPEC-WRITING-GUIDE.md)와 [AI 작성 가이드](../../../reference/AI-SPEC-WRITING-GUIDE.md)를 따른다. 제품 명세는 `docs/domain/`의 AI 세트와 `docs/reference/`에서 확인하며 과거 통합 문서를 현재 계약의 근거로 사용하지 않는다. 문서의 작성과 검토를 서브에이전트에 맡기지 않는다.
