# 6 배포: 안드로이드

기준: [검증](5-1-VERIFICATION.md).

<br>

### 6-1 빌드와 호환

현재 기준은 minSdk 24, compileSdk와 targetSdk 37, 빌드 JDK 25와 JVM bytecode 11이다. AGP, Gradle 및 라이브러리의 정확한 버전은 구현 저장소의 빌드 설정을 따른다. OS API를 추가할 때 minSdk 호환과 lint를 확인한다.

release는 R8과 Crashlytics를 켜고 빌드마다 mapping 파일을 올린다. debug는 Crashlytics 수집을 끈다. 서명 설정은 앱에서 소유하며 공용 빌드 로직으로 옮기지 않는다. Application ID, 링크 진입, 저장 식별자와 백업 제외 호환을 유지한다.

CI, 배포와 되돌리기는 [Android 배포](../../operations/DEPLOYMENT.md#5-3-manyak-android-ci)를 따른다. 외부 로그인, 앱 링크와 스토어 이동은 실기기와 설치 버전을 명시해 검증한다.
