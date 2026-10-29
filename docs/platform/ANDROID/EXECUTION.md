# Android 기반 실행

기준: [상태 관리](STATE-MANAGEMENT.md).

<br>

### 요청과 취소

비동기 작업은 명시적인 자식 코루틴과 요청별 single-flight로 중복을 막는다. CancellationException을 일반 오류로 삼키지 않는다. 재시도 책임은 한 계층에 두고 소셜 로그인과 계정 연동은 자동 반복하지 않는다. 공용 API 호출은 전송 오류를 도메인 오류로 바꾸며 사용자 문구는 presentation에서 정한다. 무거운 IO와 암복호화는 주입받은 dispatcher에서 실행한다.

Composable 재구성을 도메인 호출과 데이터 복구의 실행 계기로 삼지 않는다. 저장이 필요한 결과는 effect 소비에만 의존하지 않는다.

<br>

### 이미지 뷰어

이미지 뷰어는 Coil 원본 크기로 Fit 그림 영역을 계산하고 현재 확대와 이동을 역으로 적용해 탭을 판정한다. 원본 크기를 모르면 그림이 없는 것으로 본다. 화면이 URL과 닫기 콜백을 소유하고 이미지 요소는 URL 검사와 실패 처리 뒤 탭을 전달한다. 분석 이벤트는 화면 ViewModel에서 발화한다.

<br>

### 관측

Amplitude와 Firebase Crashlytics를 사용하며 Firebase Analytics는 사용하지 않는다. 첫 이벤트와 setOnce 사용자 속성 이전에 공용 device ID를 주입하고 같은 대기열로 처리한다. 로그인은 공개 사용자 ID를 연결하고 로그아웃은 세션 정리 순서에 맞춰 사용자 해제와 device ID 교체를 수행한다.

앱 시작에서 기기 DataStore의 install_referrer_reported가 없을 때만 Play Install Referrer를 읽는다. 성공은 귀속 속성과 완료 기록을 남긴다. 조회 실패와 연결 끊김은 다음 실행에서 재시도하며 FEATURE_NOT_SUPPORTED는 값 없이 완료한다. 완료 키는 device ID와 별개로 로그아웃 이후에도 유지한다.

화면 노출 guard는 구성 변경에 중복 발화를 막는다. reducer에는 관측 호출을 넣지 않으며 breadcrumb는 Amplitude 어댑터에서 한 번 연결한다. 지속 Crashlytics 키는 screen_name, 개별 식별자는 breadcrumb, 개별 오류는 request ID로 연결한다. 토큰, 입력 원문과 PII, 예상 4xx와 취소는 보고하지 않는다. ANR은 API 30 이상 Crashlytics와 이전 Android vitals의 범위를 구분한다.
