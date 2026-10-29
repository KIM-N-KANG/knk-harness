# 공용 클라이언트

앱 전체 셸, 공용 UI, 네트워크와 플랫폼 기반을 다룬다. 도메인별 동작은 `docs/domain/<DOMAIN>/CLIENT/`의 공통 문서와 WEB 및 ANDROID가 기준이다.

### 1 읽는 순서

단계마다 공통 다음 플랫폼을 읽는다. [WEB](WEB/AGENTS.md), [ANDROID](ANDROID/AGENTS.md).

| 문서 | 내용 |
|---|---|
| [1-BACKGROUND.md](1-BACKGROUND.md) | 1 공용 클라이언트 배경 |
| [2-1-USER-STORY.md](2-1-USER-STORY.md) | 2-1 공용 클라이언트 유저 스토리 |
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 공용 클라이언트 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 공용 화면 구성 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 공용 화면 흐름 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 공용 화면 표현 |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 공용 클라이언트 연동 계약 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 공용 클라이언트 검증 |
| [DECISIONS.md](DECISIONS.md) | 문서 구조와 공통 결정 기록 |

### 2 작성과 검증

- 공용 사용자 목표는 CLIENT-US 형식으로 이 폴더의 2-1 문서에서 한 번 정의한다. 플랫폼은 같은 ID를 참조한다. 도메인 목표를 복제하지 않는다.
- 요구사항, 화면, 연동과 구현, 검증, 배포 순서를 지키고 후속 문서 탐색과 코드 위치는 안내 문서에 둔다.
- 공용 구조를 바꾸면 사용하는 도메인을 확인한다. 문서가 없는 플랫폼 지원과 수치를 추측하지 않는다.
- 명세의 작성과 검토를 서브에이전트에 맡기지 않는다.

작성 기준은 [클라이언트 작성 가이드](../REFERENCE/CLIENT-SPEC-WRITING-GUIDE.md), 관측은 [분석 기준](../REFERENCE/ANALYTICS.md), 배포는 [배포 Design](../design/4-deployment.md)을 따른다.
