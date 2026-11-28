# NOTIFICATION iOS 클라이언트

공통: [CLIENT](../AGENTS.md).

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항: iOS |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성: iOS |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름: iOS |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: iOS |
| [4-1-CONTRACT.md](4-1-CONTRACT.md) | 4-1 연동 계약: iOS |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 컴포넌트 구조: iOS |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 상태 관리: iOS |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: iOS |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: iOS |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 배포: iOS |
| [DECISIONS.md](DECISIONS.md) | NOTIFICATION iOS 결정 기록 |

<br>

### 2 코드 위치

iOS 저장소 `manyak-ios`는 생성 전이다. 아래는 이 세트를 구현할 계획 모듈이며 파일 링크를 두지 않는다.

| 계획 모듈 | 맡는 범위 |
|---|---|
| `ManyakNotification` | Firebase Messaging, 토큰 등록, 권한, 알림 센터 위임 객체, 알림함, 알림 설정과 광고 동의, 세션 종료 알림 정리 |
| `ManyakNotice` | 공지 목록과 상세, 기기 읽음 기록과 안 읽음 판정 |
| 앱 타깃 `Manyak` | Firebase 초기화, APNs 등록 요청, 위임 객체 지정, 권한 요청 순서, 서버 토큰 삭제와 정리 항목 등록, 헤더 종과 마이 배지 조립 |
| `ManyakNavigation` | 푸시와 알림함 deepLink 해석 |
| `ManyakCreate` | 검수 결과 대기 화면 관찰 구현 |

앱 열기 스킴은 [I-030](../../../../ui/IOS/DECISIONS.md#i-030), 외부 진입의 탭과 보류는 [I-043](../../../../ui/IOS/DECISIONS.md#i-043)과 [I-044](../../../../ui/IOS/DECISIONS.md#i-044)에 있다.

<br>

### 3 작성과 검증

- 공지의 기기 읽음과 회원 알림의 서버 읽음을 구분한다.
- 수신 동의, OS 권한과 회원 인증을 같은 상태로 합치지 않는다.
- 서버가 iOS를 받기 전의 계약 값과 페이로드 형식을 만들어 넣지 않는다.
- 링크, 앵커, ID 중복과 단계 순서를 확인하고 `git diff --check`를 실행한다.
- 명세의 작성과 검토를 서브에이전트에 맡기지 않는다.
