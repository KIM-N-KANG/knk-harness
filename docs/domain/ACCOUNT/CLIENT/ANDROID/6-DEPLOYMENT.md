# 6 ACCOUNT Android 인증 배포 조건

<br>

### 6-1 공급자 설정

Google은 서버 Web client ID의 `aud`와 Android `azp` allowlist를, Kakao는 환경별 같은 앱의 Native key `aud`와 debug, upload, Play Signing 키 해시를 맞춘다. 필수 설정 누락은 명확한 실패로 처리한다.

공용 빌드, 서명과 배포 절차는 배포 문서와 앱 지침에서 확인한다. ([배포](../../../../design/4-deployment.md), [Android AGENTS](../../../../../../manyak-android/AGENTS.md))
