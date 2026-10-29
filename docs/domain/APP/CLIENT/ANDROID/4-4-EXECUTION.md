# 4-4 Android 앱 진입

기준: [앱 링크 흐름](3-2-INTERACTION-FLOWS.md).

<br>

### 4-4-1 전용 앱 링크

VIEW와 BROWSABLE 전용 스킴 `manyak://manyak.app{path}`를 앱 진입으로 해석한다. 같은 경로의 https 주소로 변환해 허용된 목적지를 판정한다. 푸시 extra가 있으면 푸시를 먼저 읽고 앱 링크는 수신자 비교 없이 회원과 프로필 확인 뒤 소비한다. 일반 https를 받는 App Links로 확장하지 않는다.
