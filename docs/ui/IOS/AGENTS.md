# 공통 UI IOS

네트워크, 공통 상태와 검증 도구는 [IOS 기반](../../platform/CLIENT/IOS/AGENTS.md)에 둔다.

<br>

### 1 문서 역할

| 문서 | 내용 |
|---|---|
| [2-2-REQUIREMENTS.md](2-2-REQUIREMENTS.md) | 2-2 요구사항: iOS |
| [3-1-INFORMATION-ARCHITECTURE.md](3-1-INFORMATION-ARCHITECTURE.md) | 3-1 화면 구성: iOS |
| [3-2-INTERACTION-FLOWS.md](3-2-INTERACTION-FLOWS.md) | 3-2 화면 흐름: iOS |
| [3-3-LAYOUT.md](3-3-LAYOUT.md) | 3-3 화면 배치: iOS |
| [4-4-EXECUTION.md](4-4-EXECUTION.md) | 4-4 실행: iOS |
| [5-1-VERIFICATION.md](5-1-VERIFICATION.md) | 5-1 검증: iOS |
| [DECISIONS.md](DECISIONS.md) | IOS 결정 기록 |

<br>

### 2 코드 위치

iOS 저장소 `manyak-ios`는 생성 전이다. 아래는 이 세트를 구현할 계획 모듈이며 파일 링크를 두지 않는다.

| 계획 모듈 | 맡는 범위 |
|---|---|
| 앱 타깃 `Manyak` | 세션 상태별 루트 교체, 탭 셸과 탭별 스택을 가진 라우터, 외부 진입 보류와 소비, URL 스킴 등록과 실행 화면, 토스트 표시 층, 테마 적용 |
| `ManyakNavigation` | 라우트 값, 하단 탭 표시 규칙, 앱 열기 링크와 푸시 경로 해석 |
| `ManyakDesignSystem` | `ManyakTheme` 토큰, 글꼴과 아이콘, 눌림 버튼 스타일, 공용 컴포넌트, 옵션 시트 내용, 로딩 골격, 로드 실패 자리, 토스트 컴포넌트 |
| `ManyakCommon` | 테마 선택 값과 기기 귀속 저장 |
| `ManyakMy` | 마이 화면 섹션의 테마 변경 메뉴 |

공통 실행과 검증 도구의 확인 항목은 [플랫폼 검증](../../platform/CLIENT/IOS/4-VERIFICATION.md)을 함께 확인한다.
