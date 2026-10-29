# ANDROID 플랫폼 기반

여러 도메인이 사용하는 컴포넌트, 데이터 상태, 실행, 관측과 빌드 규칙을 관리한다. 사용자 기능은 [도메인 목록](../../domain/AGENTS.md)에서 선택하고 앱 셸과 진입은 [공통 사용자 경험 ANDROID](../../experience/ANDROID/AGENTS.md)에서 확인한다.

<br>

### 문서 역할

| 문서 | 내용 |
|---|---|
| [COMPONENT-ARCHITECTURE.md](COMPONENT-ARCHITECTURE.md) | Android 공용 구성 |
| [STATE-MANAGEMENT.md](STATE-MANAGEMENT.md) | Android 공용 상태 관리 |
| [EXECUTION.md](EXECUTION.md) | Android 기반 실행 |
| [VERIFICATION.md](VERIFICATION.md) | Android 기반 검증 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Android 공용 배포 |
| [DECISIONS.md](DECISIONS.md) | ANDROID 결정 기록 |

공통 전송 계약은 [공통 연동 계약](../CLIENT-CONTRACT.md), 공통 배포 절차는 [운영 문서](../../operations/AGENTS.md)를 따른다. 위 표의 계약, 구현, 검증과 배포 순서로 읽으며 사용자 목표를 새로 정의하지 않는다.

<br>

### 코드 위치

- [gradle/libs.versions.toml](../../../../manyak-android/gradle/libs.versions.toml)
- [app/build.gradle.kts](../../../../manyak-android/app/build.gradle.kts)
- [gradle/wrapper/gradle-wrapper.properties](../../../../manyak-android/gradle/wrapper/gradle-wrapper.properties)
- [DESIGN.md](../../../../manyak-android/DESIGN.md#컴포넌트)
- [analytics/src/main/java/app/manyak/analytics/entity/AnalyticsEvent.kt](../../../../manyak-android/analytics/src/main/java/app/manyak/analytics/entity/AnalyticsEvent.kt)
- [AGENTS.md](../../../../manyak-android/AGENTS.md)

모듈 목록과 실제 의존은 [settings](../../../../manyak-android/settings.gradle.kts)와 [Android 지침](../../../../manyak-android/AGENTS.md)을 확인한다. app은 유일한 Application, common은 Android Library, build-logic은 별도 included build다. entity/domain/data/presentation은 필요한 모듈 내부 패키지다. 공용 포트의 구현 소유자는 ChatStarter=chat, CreationProgressAccess=create, StoryDeletion=studio, AttendanceClaimer=my이며 SessionIdAccess는 app에서 관측에 연결한다. StoryReportController는 report가 소유하고 별도 공용 ViewModel이나 Singleton을 추가하지 않는다. CreditShortageController의 상태와 이벤트는 소비 ViewModel이 소유한다. 공유 CreditPolicy와 StorySummary 및 DTO는 common에 둔다.
