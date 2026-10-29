# 공용 ANDROID 클라이언트

단계마다 [공통](../AGENTS.md) 다음 이 플랫폼의 같은 단계 문서를 읽는다. 도메인 기능은 해당 CLIENT 세트가 기준이다.

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 Android 공용 요구사항 |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 Android 공용 화면 |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 Android 공용 이동 |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 Android 공용 표현 |
| [4-2-COMPONENT-ARCHITECTURE.md](4-2-COMPONENT-ARCHITECTURE.md) | 4-2 Android 공용 구성 |
| [4-3-STATE-MANAGEMENT.md](4-3-STATE-MANAGEMENT.md) | 4-3 Android 공용 상태 관리 |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 Android 공용 실행 |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 Android 공용 검증 |
| [6-DEPLOYMENT.md](6-DEPLOYMENT.md) | 6 Android 공용 배포 |
| [DECISIONS.md](DECISIONS.md) | 확정 결정과 적용 범위 이력 |

### 2 코드 위치

- [gradle/libs.versions.toml](../../../../manyak-android/gradle/libs.versions.toml)
- [app/build.gradle.kts](../../../../manyak-android/app/build.gradle.kts)
- [gradle/wrapper/gradle-wrapper.properties](../../../../manyak-android/gradle/wrapper/gradle-wrapper.properties)
- [DESIGN.md](../../../../manyak-android/DESIGN.md#컴포넌트)
- [analytics/src/main/java/app/manyak/analytics/entity/AnalyticsEvent.kt](../../../../manyak-android/analytics/src/main/java/app/manyak/analytics/entity/AnalyticsEvent.kt)
- [AGENTS.md](../../../../manyak-android/AGENTS.md)

모듈 목록과 실제 의존은 [settings](../../../../manyak-android/settings.gradle.kts)와 [Android 지침](../../../../manyak-android/AGENTS.md)을 확인한다. app은 유일한 Application, common은 Android Library, build-logic은 별도 included build다. entity/domain/data/presentation은 필요한 모듈 내부 패키지다. 공용 포트의 구현 소유자는 ChatStarter=chat, CreationProgressAccess=create, StoryDeletion=studio, AttendanceClaimer=my이며 SessionIdAccess는 app에서 관측에 연결한다. StoryReportController는 report가 소유하고 별도 공용 ViewModel이나 Singleton을 추가하지 않는다. CreditShortageController의 상태와 이벤트는 소비 ViewModel이 소유한다. 공유 CreditPolicy와 StorySummary 및 DTO는 common에 둔다.

### 3 작업 규칙

번호 문서에는 현재 계약과 구조를, 실행 결과는 PR 및 CI에 남긴다. 원문 QA의 과거 기대와 현재 계약이 다르면 차이를 명시한다. 문서 작성과 검토를 서브에이전트에 맡기지 않는다.
