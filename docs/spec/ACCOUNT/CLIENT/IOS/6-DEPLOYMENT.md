# 6 배포: iOS

<br>

### 6-1 공급자 설정

| 제공자 | 설정 |
|---|---|
| Google | 서버 Web client ID와 별도로 번들 ID `app.manyak`의 iOS 클라이언트 ID 발급. SDK에 iOS 클라이언트 ID와 서버 클라이언트 ID를 함께 설정해 ID 토큰의 대상(`aud`)을 서버 클라이언트 ID로 받음. iOS 클라이언트 ID에서 만든 URL 스킴(Google 문서의 역순 클라이언트 ID) 등록 |
| Google 서버 허용 목록 | ID 토큰의 인가 대상(`azp`)에 iOS 클라이언트 ID가 실리면 서버 `MANYAK_GOOGLE_CLIENT_IDS`에 포함. 환경별 iOS 클라이언트 ID를 iOS 배포 전에 서버 설정에 추가 |
| Kakao | 환경별로 서버 허용 목록과 같은 카카오 앱에 iOS 플랫폼과 번들 ID 등록. 같은 앱의 네이티브 앱 키를 쓰므로 서버 허용 목록 변경 없음 |
| Kakao URL | 네이티브 앱 키로 만든 URL 스킴과 카카오톡 앱 열기 확인용 스킴 목록을 Kakao iOS SDK 문서 기준으로 `Info.plist`에 등록 |
| 누락 | 필수 설정 누락은 `ProviderNotConfigured`의 명확한 실패로 처리 |

키 값의 주입 경로와 Debug, Release 구분은 IOS 기반 빌드 설정을 따른다. 서버 허용 목록의 의미와 변경 절차는 ACCOUNT 백엔드 배포 문서에 있다. ([IOS 빌드와 환경](../../../../platform/CLIENT/IOS/5-DEPLOYMENT.md#5-1-빌드와-환경), [백엔드 환경 변수와 시크릿](../../BACKEND/6-DEPLOYMENT.md#6-3-환경-변수와-시크릿))

<br>

### 6-2 심사와 호환

| 항목 | 조건 |
|---|---|
| 로그인 서비스 | Sign in with Apple 없이 제출. App Store 심사 지침 4.8 반려 위험을 감수하고 반려되면 서버 `/auth/social/{provider}`의 `apple` 추가를 먼저 진행한 뒤 새 결정으로 추가 ([I-060](DECISIONS.md#i-060)) |
| 계정 삭제 | 앱 안 회원 탈퇴 화면이 계정 삭제를 제공. 심사 지침의 계정 삭제 조항 원문은 확인하지 않음 |
| 심사 계정 | 로그인 필수라 심사 전용 Google 계정을 제공. 자격 증명은 App Store Connect의 심사 정보에만 기록 ([IOS 출시](../../../../platform/CLIENT/IOS/5-DEPLOYMENT.md#5-4-출시)) |
| 저장 식별자 | Keychain 항목 식별자, 설치 표시 키와 저널 파일 이름은 출시 뒤 바꾸지 않음. 설치 표시 키를 바꾸면 모든 기존 설치가 재설치로 판정되어 로그아웃됨 |

공용 빌드, 서명과 출시 절차는 IOS 기반을 따른다. ([IOS 배포](../../../../platform/CLIENT/IOS/5-DEPLOYMENT.md))
