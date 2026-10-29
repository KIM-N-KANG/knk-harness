# MODERATION AI 안내

게시물 검수 AI의 배경과 요구사항, 설계와 계약, 구현과 평가, 운영 순서로 읽는다. 도메인의 다른 세트와 입력 및 결과 경계를 함께 확인한다.

### 1 문서

| 문서 | 내용 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 1. 배경 |
| [2-1-USER-STORY.md](2-1-USER-STORY.md) | 2-1 유저 스토리 |
| [2-2-OPERATION-REQUIREMENTS.md](2-2-OPERATION-REQUIREMENTS.md) | 2-2 운영 요구사항 |
| [3-TASK-DEFINITION.md](3-TASK-DEFINITION.md) | 3. 태스크 정의 |
| [4-1-DESIGN-COGNITIVE-ARCHITECTURE.md](4-1-DESIGN-COGNITIVE-ARCHITECTURE.md) | 4-1 인지 구조 설계 |
| [4-2-DESIGN-SOFTWARE-ARCHITECTURE.md](4-2-DESIGN-SOFTWARE-ARCHITECTURE.md) | 4-2 소프트웨어 구조 설계 |
| [5-CONTRACT.md](5-CONTRACT.md) | 5. 계약 |
| [6-1-AI-EXECUTION.md](6-1-AI-EXECUTION.md) | 6-1 AI 실행 |
| [6-2-SOFTWARE-IMPLEMENTATION.md](6-2-SOFTWARE-IMPLEMENTATION.md) | 6-2 소프트웨어 구현 |
| [6-3-AI-ALIGNMENT.md](6-3-AI-ALIGNMENT.md) | 6-3 AI 정렬 |
| [6-4-AI-EVALUATION-METHOD.md](6-4-AI-EVALUATION-METHOD.md) | 6-4 AI 평가 방법 |
| [6-5-AI-EVALUATION-IMPLEMENTATION.md](6-5-AI-EVALUATION-IMPLEMENTATION.md) | 6-5 AI 평가 구현 |
| [6-6-AI-PERFORMANCE-REPORT.md](6-6-AI-PERFORMANCE-REPORT.md) | 6-6 AI 성능 보고 |
| [7-1-ERROR-HANDLING.md](7-1-ERROR-HANDLING.md) | 7-1 오류 처리 |
| [7-2-TEST-CASES.md](7-2-TEST-CASES.md) | 7-2 테스트 케이스 |
| [7-3-OBSERVABILITY.md](7-3-OBSERVABILITY.md) | 7-3 관측 |
| [7-4-DEPLOYMENT.md](7-4-DEPLOYMENT.md) | 7-4 배포 |
| [DECISIONS.md](DECISIONS.md) | DECISIONS.md |

### 2 작업 규칙

[제품 작성 가이드](../../../REFERENCE/PRODUCT-SPEC-WRITING-GUIDE.md)와 [AI 작성 가이드](../../../REFERENCE/AI-SPEC-WRITING-GUIDE.md)를 따른다. 제품 명세는 `docs/domain/`의 AI 세트와 `docs/REFERENCE/`에서 확인하며 과거 통합 문서를 현재 계약의 근거로 사용하지 않는다. 문서의 작성과 검토를 서브에이전트에 맡기지 않는다.
