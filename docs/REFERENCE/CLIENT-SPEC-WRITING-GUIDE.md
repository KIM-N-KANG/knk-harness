# 클라이언트 Spec 작성 가이드

하나의 도메인에 필요한 웹 또는 Android 명세의 파일 구성과 각 파일이 정하는 것을 적는다. WEB 세트와 ANDROID 세트가 같은 구성을 쓴다. 문장, 파일명과 제목 번호는 [제품 Spec 작성 가이드](PRODUCT-SPEC-WRITING-GUIDE.md)를 따른다. 아래 항목은 해당 도메인의 실제 결정으로 채우며 해당 없는 파일은 만들지 않는다.

<br>

## 1. 개요

클라이언트 명세는 화면에 어떤 정보를 어떻게 배치하고, 그 화면이 시간순으로 어떻게 이어지며, 백엔드와 무엇을 주고받는지를 정한다. 요구사항과 정보 구조를 먼저 정하고, 그 위에 컴포넌트와 상태를 설계한 뒤, 백엔드 계약과 데이터 연동으로 넘어간다.

와이어프레임은 이미지가 아니라 HTML로 둔다. 구현에 필요한 것은 그림이 아니라 간격, 글자, 배치이고, 이미지는 그것을 전달하지 못한다. 정적인 와이어프레임과 별개로 사용자가 시간순으로 어떤 화면을 거치는지도 정한다.

<br>

## 2. 파일 구조

```text
1-1-BACKGROUND.md
1-2-REQUIREMENTS.md
2-1-INFORMATION-ARCHITECTURE.md
2-2-LAYOUT.md
2-3-UI-DESIGN-SYSTEM.md
2-4-COMPONENT-ARCHITECTURE.md
2-5-STATE-MANAGEMENT.md
2-6-DESIGN-DECISIONS.md
3-1-CONTRACT.md
3-2-DATA-INTEGRATION.md
3-3-COMPOSITION-WIRING.md
3-4-INTERACTION-FLOWS.md
4-1-ERROR-HANDLING.md
4-2-QUALITY.md
5-1-VERIFICATION.md
5-2-DEPLOYMENT.md
CLAUDE.md
DECISIONS.md
```

`1`은 배경과 요구사항, `2`는 화면과 구조 설계, `3`은 백엔드 연동과 흐름, `4`는 품질, `5`는 검증과 배포다.

| 파일 | 정하는 것 |
|---|---|
| `1-1-BACKGROUND.md` | 이 도메인의 화면이 왜 필요한지. 도메인 배경, 대상 사용자, 이 세트에서 쓰는 용어 |
| `1-2-REQUIREMENTS.md` | 이 플랫폼의 요구사항. 지원 범위, 반응형과 기기 조건, 접근성과 성능 목표를 측정 가능한 값으로 |
| `2-1-INFORMATION-ARCHITECTURE.md` | 화면 목록과 각 화면에 어떤 정보를 어떤 우선순위로 보여 주는지 |
| `2-2-LAYOUT.md` | 화면별 배치. 와이어프레임은 HTML로 두고 간격, 글자, 배치 값을 코드로 전달한다 |
| `2-3-UI-DESIGN-SYSTEM.md` | 디자인 토큰, 색과 글꼴, 공용 UI 요소와 사용 규칙 |
| `2-4-COMPONENT-ARCHITECTURE.md` | 컴포넌트 경계와 책임, 재사용 단위, 플랫폼 모듈 구조 |
| `2-5-STATE-MANAGEMENT.md` | 화면 상태와 서버 상태의 구분, 저장 위치, 수명과 복원 |
| `2-6-DESIGN-DECISIONS.md` | 현재 적용 중인 설계 결정과 근거. 이력은 `DECISIONS.md`에 둔다 |
| `3-1-CONTRACT.md` | 백엔드와 주고받는 계약. 기준은 해당 도메인 BACKEND 세트의 `4-2`이며 여기서는 이 플랫폼이 쓰는 범위와 차이만 적는다 |
| `3-2-DATA-INTEGRATION.md` | 데이터를 어떻게 받아 어디에 두고 어떻게 갱신하는지. 캐시, 낙관적 갱신, 스트리밍 수신 |
| `3-3-COMPOSITION-WIRING.md` | 화면, 컴포넌트, 상태, 데이터 계층을 어떻게 이어 붙이는지 |
| `3-4-INTERACTION-FLOWS.md` | 사용자가 시간순으로 거치는 화면 흐름과 분기. 와이어프레임과 별개로 정한다 |
| `4-1-ERROR-HANDLING.md` | 오류별 표시, 재시도, 복귀 경로. 오류 처리를 여기 한곳에 모은다 |
| `4-2-QUALITY.md` | 접근성, 인증 상태 처리, 성능, 분석 이벤트 |
| `5-1-VERIFICATION.md` | 테스트 항목, 실행 명령과 통과 증거, 린트. 항목이 있는 것과 실행해 통과한 것을 구분한다 |
| `5-2-DEPLOYMENT.md` | 빌드와 배포 경로, 환경 변수, 배포 조건, 되돌리기 |
| `CLAUDE.md` | 문서의 역할, 읽는 순서, 작업별 참조, 명세와 코드의 대응. 명세 본문을 복사하지 않는다 |
| `DECISIONS.md` | 결정의 날짜, 배경, 채택한 선택, 대안, 영향과 재검토 조건 |

<br>

## 3. 작성 기준

- 웹과 Android가 공유하는 계약과 규칙은 한 세트에서 정하고 다른 세트는 참조한다. 두 세트에 같은 내용을 복사하지 않는다.
- 계약의 기준은 BACKEND 세트다. 클라이언트 세트에서 계약을 새로 정하지 않는다.
- 검증은 `5-1`에 둔다. 테스트 통과와 린트 같은 검증 항목을 모아 리뷰 자동화에 연결한다.
- 화면과 값은 코드와 디자인 원본에서 확인한 것만 적는다. 미정, 비적용, 미구현을 구분한다.
- 명세의 작성, 수정과 검토를 서브에이전트에 맡기지 않는다.
