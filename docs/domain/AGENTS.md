# 제품 도메인

제품 계약은 도메인과 제공자 세트별로 관리한다. 공용 클라이언트 기반과 용어, 서비스 배경 및 분석 기준은 공용 문서에서 확인한다.

<br>

### 1 도메인과 세트

| 도메인 | BACKEND 계약 | AI 계약 | CLIENT |
|---|---|---|---|
| [ACCOUNT](ACCOUNT/AGENTS.md) | [BACKEND](ACCOUNT/BACKEND/4-2-CONTRACT.md) | 해당 없음 | [CLIENT](ACCOUNT/CLIENT/AGENTS.md) |
| [PAYMENT](PAYMENT/AGENTS.md) | [BACKEND](PAYMENT/BACKEND/4-2-CONTRACT.md) | 해당 없음 | [CLIENT](PAYMENT/CLIENT/AGENTS.md) |
| [CHAT](CHAT/AGENTS.md) | [BACKEND](CHAT/BACKEND/4-2-CONTRACT.md) | [AI](CHAT/AI/5-CONTRACT.md) | [CLIENT](CHAT/CLIENT/AGENTS.md) |
| [STORY](STORY/AGENTS.md) | [BACKEND](STORY/BACKEND/4-2-CONTRACT.md) | [AI](STORY/AI/5-CONTRACT.md) | [CLIENT](STORY/CLIENT/AGENTS.md) |
| [MODERATION](MODERATION/AGENTS.md) | [BACKEND](MODERATION/BACKEND/4-2-CONTRACT.md) | [AI](MODERATION/AI/5-CONTRACT.md) | [CLIENT](MODERATION/CLIENT/AGENTS.md) |
| [NOTIFICATION](NOTIFICATION/AGENTS.md) | [BACKEND](NOTIFICATION/BACKEND/4-2-CONTRACT.md) | 해당 없음 | [CLIENT](NOTIFICATION/CLIENT/AGENTS.md) |

<br>

### 2 문서 역할과 읽는 순서

각 세트의 안내에서 배경과 요구사항, 설계와 계약, 구현과 검증 및 배포 순서로 읽는다. CLIENT는 같은 단계에서 공통 다음 WEB 또는 ANDROID를 읽는다. 제공자 계약과 소비자 구현을 중복 정의하지 않는다.

| 공용 내용 | 위치 |
|---|---|
| 앱 셸과 플랫폼 기반 | [공용 클라이언트](../client/AGENTS.md) |
| 용어와 표기 | [용어집](../REFERENCE/GLOSSARY.md) |
| 서비스와 사용자 | [서비스 배경](../REFERENCE/SERVICE-BACKGROUND.md) |
| 이벤트와 관측 | [분석 기준](../REFERENCE/ANALYTICS.md) |
| 서비스 공용 인터페이스 | [공용 연동](../REFERENCE/SERVICE-INTERFACES.md) |
| 공용 배포와 인프라 | [배포 Design](../design/4-deployment.md) |

현재 문서에 이전 절 번호 기반 유저 스토리를 다시 정의하지 않는다. 과거 계획과 이동 대응은 Git 이력 및 이관 PR 근거, 작업 진행과 우선순위는 Jira에서 관리한다.
