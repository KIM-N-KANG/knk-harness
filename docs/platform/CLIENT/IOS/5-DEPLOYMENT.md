# 5 배포: iOS

기준: [검증](4-VERIFICATION.md).

<br>

### 5-1 빌드와 환경

현재 기준은 최소 배포 대상 iOS 26, Xcode 27 이상과 Swift 6 언어 모드다. 대상 기기와 화면 방향은 [공통 UI IOS 요구사항](../../../ui/IOS/2-2-REQUIREMENTS.md)을 따른다. 번들 ID는 `app.manyak`이며 바꾸지 않는다. 로컬 패키지가 최소 플랫폼으로 iOS 26을 선언하려면 패키지 도구 버전(`swift-tools-version`)이 6.2 이상이어야 한다(Xcode 27.2에서 확인, 2026-11-28). 라이브러리의 정확한 버전은 구현 저장소의 `Package.resolved`를 따른다.

| 설정 | Debug | Release |
|---|---|---|
| 서버 주소 | `https://dev-api.manyak.app/api/v1/`. 커밋하지 않는 xcconfig로 로컬 서버 덮어쓰기 가능 | `https://api.manyak.app/api/v1/` 고정 |
| 웹 주소 | `https://manyak.app`. 커밋하지 않는 xcconfig로 덮어쓰기 가능 | `https://manyak.app` |
| 평문 통신 | 로컬 주소에만 App Transport Security 예외 | 예외 없음 |
| 제공자와 분석 키 | Debug용 Google iOS 클라이언트 ID와 서버 클라이언트 ID, Kakao 네이티브 앱 키, Amplitude 키 | Release용 같은 네 값 |
| Crashlytics | 수집 끔 | 수집 켬. Archive마다 dSYM 업로드 |
| 포맷과 린트 | 빌드에서 swift-format 검사와 SwiftLint 실행. 위반 시 빌드 실패 | 같음 |

| 값 | 저장과 주입 |
|---|---|
| 공용 빌드 설정과 버전 | 커밋하는 공용 xcconfig |
| 제공자와 분석 키 | 커밋하지 않는 비밀값 xcconfig. 예시 파일만 커밋. 값이 없어도 빌드는 성공하고 해당 기능만 실행 시 실패 |
| Google과 Kakao URL 스킴 | 비밀값 xcconfig의 값을 빌드 설정으로 `Info.plist`에 주입 |
| Firebase 설정 | `GoogleService-Info.plist`를 커밋. 환경 구분 없는 Firebase 프로젝트 하나 ([I-021](DECISIONS.md#i-021)) |
| APNs 인증 키 | Firebase 콘솔에 등록. 저장소와 문서에 두지 않음 |

키 값과 실제 경로는 문서와 저장소에 적지 않는다. 오픈소스 고지 목록의 생성 방식은 미정이며 대상은 Swift Package Manager 의존성과 번들 글꼴 두 종의 OFL이다. 앱 개인정보 라벨과 개인정보 매니페스트(`PrivacyInfo.xcprivacy`)의 내용은 미정이며 대상은 Amplitude와 Crashlytics가 보내는 데이터, UserDefaults처럼 사용 이유 신고가 필요한 API다.

<br>

### 5-2 CI

| 항목 | 내용 |
|---|---|
| 실행 계기 | `dev`, `main` 대상 PR과 push |
| 러너 | GitHub Actions macOS 러너. Xcode 27 이상 선택 |
| 단계 | swift-format 검사, SwiftLint, iOS 시뮬레이터 단위 테스트, 시뮬레이터용 Debug 빌드 |
| 판정 | 한 단계라도 실패하면 실패 |
| 제외 | XCUITest, Release Archive, 서명과 업로드 |
| 비밀값 | 두지 않음. 비밀값 xcconfig 없이 빌드 |

러너 이미지의 Xcode 27 제공 여부는 확인하지 않았다(2026-11-26 기준). ([I-013](DECISIONS.md#i-013))

<br>

### 5-3 버전과 서명

| 항목 | 규칙 |
|---|---|
| 마케팅 버전 | `CFBundleShortVersionString`. 1.0.0부터 시작하고 Android 버전과 별개. 버그 수정은 patch, 기능 추가는 minor |
| 빌드 번호 | `CFBundleVersion`. App Store Connect에 올릴 때마다 1 증가, 재사용 금지. 심사 반려 뒤 같은 내용을 다시 올릴 때도 올림 |
| 정의 위치 | 두 값 모두 공용 xcconfig 한 곳 |
| 서명 | 릴리스 담당자의 Mac에서 수동. CI에 인증서, 프로비저닝 프로파일과 App Store Connect 키를 두지 않음 |
| 서명 방식 | 미정(Xcode 자동 서명 사용 여부, 인증서 보관과 복구) |

<br>

### 5-4 출시

```mermaid
flowchart TD
    A["origin/dev에서 release 브랜치 생성"] --> B["버전 커밋"]
    B --> C["main 릴리스 PR과 dev 버전 동기화 PR"]
    C --> D["main 병합 커밋에서 Release Archive"]
    D --> E["App Store Connect 업로드와 dSYM 확인"]
    E --> F["TestFlight 내부 테스터 실기기 검수"]
    F --> G{"검수 통과"}
    G -->|아니오| X["수정 후 새 빌드 번호로 다시 검증"]
    G -->|예| H["같은 빌드를 외부 테스터에 배포"]
    H --> I["같은 빌드로 App Store 심사 제출"]
    I --> J{"심사 결과"}
    J -->|반려| X
    J -->|승인| K["단계적 출시와 중단 기준 관찰"]
```

1. `release/v{버전}` 브랜치를 `origin/dev`에서 만들고 공용 xcconfig의 마케팅 버전과 빌드 번호만 커밋한다.
2. 같은 브랜치로 `main` 릴리스 PR과 `dev` 버전 동기화 PR을 낸다.
3. `main` 병합 뒤 그 커밋에서 Release로 Archive한다. Archive 전에 비밀값 xcconfig의 Release 값 네 개가 채워졌는지 확인한다.
4. App Store Connect에 올리고 같은 빌드의 dSYM이 Crashlytics에 올라갔는지 확인한다.
5. TestFlight 내부 테스터로 실기기에서 로그인과 핵심 흐름을 완주한다.
6. 통과하면 같은 빌드를 외부 테스터에 배포하고 같은 빌드로 App Store 심사에 제출한다. 단계마다 다시 빌드하지 않는다.
7. 승인 뒤 App Store Connect의 단계적 출시로 시작하고 [중단 기준](../../../operations/DEPLOYMENT.md#9-3-android-단계적-출시와-중단-기준)을 iOS 앱 버전별로 관찰한다. 기준을 충족하면 단계적 출시를 멈추고 수정판을 준비한다.

외부 테스터 배포와 App Store 제출은 Apple 심사를 거친다. 단계적 출시의 단계별 비율과 기간은 App Store Connect가 정하며 이번 작성에서 다시 확인하지 않았다. 앱은 로그인이 필수이므로 심사용 계정의 준비 방식은 미정이다. 외부 로그인의 앱 전환, 앱 열기 링크와 푸시는 실기기와 설치 빌드를 명시해 검증한다. ([I-014](DECISIONS.md#i-014), [I-015](DECISIONS.md#i-015), [I-023](DECISIONS.md#i-023))
