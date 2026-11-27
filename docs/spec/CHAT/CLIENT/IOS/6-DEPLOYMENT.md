# 6 배포: iOS

<br>

### 6-1 공유 링크 origin

공유 URL은 빌드 구성의 웹 주소로 `{웹 주소}/share/{shareId}`를 만든다. Release는 운영 API와 운영 웹 주소를 쓴다. Debug는 dev API와 기본 웹 주소 `https://manyak.app` 조합이라 dev에서 발급한 공유본을 운영 웹에서 찾지 못할 수 있다. 이 환경의 열람 실패를 공유 발급 실패로 기록하지 않으며 같은 환경의 발급과 열람을 구분해 검증한다. ([IOS 기반 빌드와 환경](../../../../platform/CLIENT/IOS/5-DEPLOYMENT.md#5-1-빌드와-환경), [5-1 검증](5-1-VERIFICATION.md))
