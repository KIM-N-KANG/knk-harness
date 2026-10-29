# AI 플랫폼 기반

공통 모델 호출은 플랫폼에서, 요청별 프롬프트와 모델 선택, 재시도 및 시간 제한은 도메인 AI 세트에서 정의한다.

<br>

### 1 공통 기반과 기능별 계약

| 범위 | 기준 |
|---|---|
| 공통 통로와 SDK 어댑터 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 스토리라인, 컴파일과 인물 이미지 | [STORY 실행](../../domain/STORY/AI/6-1-AI-EXECUTION.md), [구현](../../domain/STORY/AI/6-2-SOFTWARE-IMPLEMENTATION.md) |
| 본문, 선택지, 판정과 실시간 이미지 | [CHAT 실행](../../domain/CHAT/AI/6-1-AI-EXECUTION.md), [구현](../../domain/CHAT/AI/6-2-SOFTWARE-IMPLEMENTATION.md) |
| 게시물 검수 | [MODERATION 실행](../../domain/MODERATION/AI/6-1-AI-EXECUTION.md), [구현](../../domain/MODERATION/AI/6-2-SOFTWARE-IMPLEMENTATION.md) |
| 관측과 실패 격리 | [STORY](../../domain/STORY/AI/7-3-OBSERVABILITY.md), [CHAT](../../domain/CHAT/AI/7-3-OBSERVABILITY.md), [MODERATION](../../domain/MODERATION/AI/7-3-OBSERVABILITY.md) |
| 모델 설정과 호환성 | [STORY 배포](../../domain/STORY/AI/7-4-DEPLOYMENT.md), [CHAT 배포](../../domain/CHAT/AI/7-4-DEPLOYMENT.md), [MODERATION 배포](../../domain/MODERATION/AI/7-4-DEPLOYMENT.md) |
| 환경과 배포 | [공용 배포](../../operations/DEPLOYMENT.md) |
| 기존 D와 A 결정 원문 | [AI 결정 기록](../../reference/decisions/AI.md) |

<br>

### 2 코드 위치

[AI 지침](../../../../manyak-ai/AGENTS.md), [모델 등록부](../../../../manyak-ai/src/services/llm/registry.py), [설정](../../../../manyak-ai/src/core/config.py), [프롬프트](../../../../manyak-ai/prompt)에서 구현을 대조한다. 과거 통합 Design의 모델 값과 구현 상태를 현재 운영값으로 사용하지 않는다.
