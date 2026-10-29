# 플랫폼 기반

특정 기능에 속하지 않는 기술 규칙을 관리한다. 제품 요구사항, 화면과 기능별 데이터는 해당 도메인에서 정의한다.

<br>

### 기술 경계

| 기반 | 범위 |
|---|---|
| [공통 클라이언트 계약](CLIENT-CONTRACT.md) | 공통 전송, 오류와 시각 해석 |
| [WEB](WEB/AGENTS.md) | API 생성, 컴포넌트, 서버 상태, 뷰어, 관측과 검증 |
| [ANDROID](ANDROID/AGENTS.md) | 모듈 의존, MVI, 상태 수명, 요청 취소, 관측과 빌드 |
| [BACKEND](BACKEND/AGENTS.md) | 공통 요청 경계, 메트릭과 런타임 설정 |
| [AI](AI/AGENTS.md) | 공통 모델 호출과 SDK 어댑터 경계 |

앱 셸, 테마와 외부 앱 진입은 [공통 사용자 경험](../experience/AGENTS.md), 환경과 배포는 [operations](../operations/AGENTS.md), 작성 기준과 용어는 [reference](../reference/AGENTS.md)에서 확인한다.
