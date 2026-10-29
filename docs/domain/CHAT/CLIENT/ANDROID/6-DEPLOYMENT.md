# 6 CHAT Android 배포 조건

<br>

### 6-1 공유 링크 origin

공유 URL은 데이터 계층의 `webBaseUrl`을 사용한다. 운영 API와 운영 웹 origin을 맞춘다. 현재 디버그 빌드는 dev API와 운영 웹 origin 조합이라 dev에서 발급한 공유본을 운영 웹에서 찾지 못할 수 있다. 이 환경의 열람 실패를 공유 발급 실패로 기록하지 않으며 실제 같은 환경의 발급과 열람을 구분해 검증한다. ([5-1 검증](5-1-VERIFICATION.md))
