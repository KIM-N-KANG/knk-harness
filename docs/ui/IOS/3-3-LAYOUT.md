# 3-3 화면 배치: iOS

기준: [공통 표현](../3-3-LAYOUT.md), [iOS 흐름](3-2-INTERACTION-FLOWS.md).

<br>

### 3-3-1 셸, 헤더와 실행 화면

탭 바, 내비게이션 바, 시트와 알림창은 시스템 모양(Liquid Glass, iOS 26부터 쓰는 반투명 시스템 재질)을 따른다. 그 안의 앱 내용은 [디자인 토큰](#3-3-7-디자인-토큰)으로 그린다. ([I-034](DECISIONS.md#i-034))

| 요소 | 표현 |
|---|---|
| 탭 바 | 시스템 탭 바. 홈, 채팅, 제작, 탐색, 마이 순서와 24pt 아이콘 및 라벨. 선택은 filled 아이콘과 text 색, 비선택은 outline 아이콘과 시스템 기본 색. 시스템이 그리는 선택 표시는 그대로 둠 |
| 탭 루트 헤더 | 시스템 내비게이션 바, 큰 제목 없음. 왼쪽에 홈은 높이 24pt 로고, 나머지 탭은 제목(titleLarge 한 줄). 오른쪽 버튼은 각 도메인 |
| 하위 화면 헤더 | 시스템 뒤로 버튼과 가운데 제목(bodyLargeStrong 한 줄, 넘치면 말줄임). 오른쪽 요소는 각 도메인. 스토리 상세와 채팅방은 화면이 헤더를 정함 |
| 시스템 강조색 | textBrand. 알림창 버튼과 시스템 글자 버튼에 적용. 탭 바 선택만 text |
| 화면 여백 | 좌우 gutter 16pt. 탭 바 위 목록의 끝은 그 목록의 행 간격, 탭 바가 없는 전체 화면의 끝은 screenBottom 32pt |
| 안전 영역 | 배경과 전체 폭 이미지는 화면 끝까지, 글자와 조작 요소는 안전 영역 안. 하단 고정 동작은 홈 표시기 위, 키보드가 열리면 키보드 위. 도메인이 키보드가 열린 동안 하단 동작을 숨기도록 정한 화면은 도메인을 따름 |
| 실행 화면 | 시스템 모양을 따르는 surface 바탕 가운데에 brand 색 64pt 로고 심벌 하나. 글자와 로딩 표시 없음. 앱 안 시작 화면의 첫 프레임과 같은 위치와 크기라 바뀔 때 심벌이 움직이지 않음 ([I-050](DECISIONS.md#i-050)) |

앱 안 시작 화면의 로딩 연출과 실패 표시는 ACCOUNT 화면 배치를 따른다. ([ACCOUNT iOS 3-3](../../spec/ACCOUNT/CLIENT/IOS/3-3-LAYOUT.md#3-3-1-공통-화면의-ios-표현))

<br>

### 3-3-2 조작과 공용 컴포넌트

| 항목 | 표현 |
|---|---|
| 터치 영역 | 44pt 이상. 보이는 크기가 더 작은 조작(controlSmall 32pt, controlTiny 28pt, 입력과 칩 40pt)은 보이는 크기를 유지하고 터치 영역만 넓힘. 인접 조작의 터치 영역은 겹치지 않음 ([I-048](DECISIONS.md#i-048)) |
| 눌림 | 사용자 정의 버튼 스타일이 눌린 동안 overlayPressed를 요소 모양과 터치 영역 전체에 덮음. 카드, 행, 메뉴 항목, 글자 버튼과 아이콘 버튼 |
| 채움 버튼 눌림 | 덮개 대신 배경만 교체. 주 버튼 backgroundBrandBold, 파괴 버튼 backgroundDangerBoldPressed, 중립 버튼 backgroundNeutralPressed |
| 눌림 표시 없음 | 라디오, 체크박스, 행 전체 토글, 밑줄 탭, 이미지 뷰어 닫기 영역. 선택 표시가 반응을 맡음. 탭 바는 시스템 반응 |
| 금지 | 색 변화 외의 눌림 애니메이션(축소, 튕김) |
| 길게 누르기 | 옵션 시트를 여는 카드와 행. 인식 순간 햅틱 한 번, 더보기와 같은 옵션 시트 표시 |

| 컴포넌트 | 값 |
|---|---|
| 주 버튼 | 배경 brand, 글자 textInverse와 labelLarge, control 모서리, 세로 compact 8pt와 가로 component 12pt 여백. 흰 글자 대비 3.15로 AA 미달이지만 웹과 같은 값 유지 |
| 파괴 버튼 | 주 버튼 모양에 배경 backgroundDangerBold |
| 중립 버튼 | 배경 backgroundNeutral, 글자 text, border 1pt 경계. 실패 자리의 다시 시도와 보조 동작 |
| 글자 버튼 | 배경 없음, labelLarge, control 모서리. 닫기는 textSubtle, 진입과 재시도는 textBrand. 처리 중 textDisabled |
| 아이콘 버튼 | 배경 없음. 콘텐츠 안 32pt 이하 버튼은 menuItem 모서리, 옆 버튼과 짝인 큰 버튼은 control 모서리 |
| 비활성 | 배경 backgroundDisabled, 글자 textDisabled. 색만으로 전하지 않고 상태 문구를 함께 둠 |
| 텍스트 필드 | 배경 surfaceRaised, border 1pt, bodyMedium, control 모서리, 세로 controlVertical 10pt와 가로 controlHorizontal 14pt, 최소 높이 input 40pt. 포커스는 경계만 borderInput, 오류는 borderDanger와 아래 textDanger 및 bodySmall 문구 |
| 카드 | 배경 surface, border 1pt, card 모서리, 안쪽 component 12pt. 제목 titleMedium, 본문 bodyMedium, 메타 bodySmall과 textSubtle |
| 배지 | 배경 backgroundBrandSubtle, 글자 textBrand와 bodySmall, pill 모서리, 세로 hairline 2pt와 가로 compact 8pt |
| 메뉴 행 | 왼쪽 아이콘 20pt, 아이콘과 라벨 사이 12pt, 오른쪽 이동 아이콘 16pt, 최소 높이 48pt |
| 체크박스 | 20pt 정사각, checkbox 모서리. 기본 surface 채움과 border 2pt, 선택은 brand 채움과 textInverse 16pt 체크. 줄 전체가 토글과 이름을 맡음 |
| 밑줄 탭 | 선택 라벨 text, 비선택 textSubtle, 탭 폭의 text 1.5pt 표시선. 브랜드 색 없음 |

backgroundBrandBold는 눌림에만 쓰고 성공 상태에 새 초록을 만들지 않는다. 그림자로 층을 만들지 않고 표면 색과 경계선으로 구분한다. 떠 있는 판이 같은 밝기의 바탕과 겹치는 셀렉트 메뉴, 툴팁과 비용 안내 판만 selectMenuElevation 4pt 그림자를 쓴다.

<br>

### 3-3-3 시트, 알림창과 덮개

| 요소 | 표현 |
|---|---|
| 시트 컨테이너 | 시스템 시트의 바탕, 모서리, 끌기 표시와 전환. 내용은 토큰 |
| 높이 | 단계 하나. 내용 높이에 맞추고 화면을 넘으면 큰 단계에서 본문만 스크롤. 중간 높이에 멈추는 단계 없음 ([I-047](DECISIONS.md#i-047)) |
| 안쪽 여백 | 좌우와 아래 gutter 16pt. 아래는 홈 표시기 위 |
| 닫기 버튼 | 주 동작 버튼이 있을 때만 그 아래 compact 8pt에 전체 폭 글자 버튼 “닫기”(높이 48pt, textSubtle). 주 동작이 없는 시트는 끌어내리기와 바깥 탭으로만 닫음 |
| 잠금 | 처리 중에는 끌어내리기와 바깥 탭 닫기를 막고 끌기 표시 유지. 처음부터 끌어 닫을 수 없는 시트(필수 동의)는 끌기 표시 없음. 끌 때 시스템이 보이는 반동은 허용 |
| 시트 위 화면 | 다음 시트나 알림창은 앞 시트가 닫힌 뒤 표시. 시트 위 문서 창은 전체 화면 덮개 |
| 옵션 시트 | 머리글(종류 bodyMedium과 textSubtle, 제목 titleLarge 한 줄) 아래 gutter 16pt에 옵션 행. 행은 아이콘 20pt, 아이콘과 라벨 사이 12pt, 최소 높이 48pt, 가로 compact 8pt, menuItem 모서리, 라벨 bodyLarge. 파괴 항목은 textDanger로 맨 아래, 진행 중 항목은 오른쪽 20pt 스피너와 탭 차단. 닫기 버튼 없음 |
| 확인 알림창 | 시스템 알림창. 제목과 설명은 도메인 문구. 머무르는 쪽 버튼 “닫기”는 취소 역할, 무언가를 잃는 확인은 파괴 역할 |
| 이미지 뷰어 | 전체 화면 덮개, 바탕 imageViewerScrim, 닫기 아이콘 textInverse, 상태 바 글자 밝게. 원본 비율로 그림과 배경을 구분. 핀치 1배에서 5배, 이동, 두 번 탭으로 2.5배 전환. 닫기 버튼과 배경 탭으로 닫고 그림 위 탭으로 닫지 않음. 배경 탭은 떼는 즉시 닫고 두 번째 탭 대기는 그림 위 탭에만 적용 |

<br>

### 3-3-4 공통 화면 상태

| 상태 | 표현 |
|---|---|
| 최초 로딩 | 300ms 안에 끝나면 아무것도 띄우지 않고 넘으면 그 화면의 로딩 골격. 끝나면 즉시 내용, 최소 표시 시간 없음 |
| 로딩 골격 | 바탕 border. 한 화면의 조각이 함께 불투명도 1과 0.5 사이를 한 방향 700ms로 오감. 동작 줄이기에서는 불투명도 1로 멈춤 |
| 최초 로드 실패 | 화면 안 실패 자리. 도메인의 실패 문구와 중립 버튼 “다시 시도”를 남은 영역 가운데에 둠 |
| 일시 실패 | 기존 내용 유지와 토스트 |
| 빈 상태 | 정상 조회가 성공하고 결과가 없을 때만. 문구와 배치는 도메인 |
| 요청 버튼 | 처리 중 비활성, 문구 자리 가운데 스피너. 버튼 크기와 접근 가능한 이름 유지 |
| 진행 표시 | 시스템 진행 표시에 progressIndicator 색. 300ms 안에 끝나면 띄우지 않음 |
| 당겨서 새로고침 | 시스템 당김 표시자. 목록이 그려진 상태에만 두고 골격, 실패와 빈 상태에는 없음. 응답이 빨라도 표시자를 최소 300ms 유지하고 기존 내용은 응답까지 유지 |

토스트는 시스템에 없으므로 앱이 그리는 오버레이로 표시한다. 문구와 표시 조건은 각 도메인이 정한다. ([I-035](DECISIONS.md#i-035), [I-046](DECISIONS.md#i-046))

| 토스트 | 표현 |
|---|---|
| 위치 | 화면 아래 가운데, 좌우 gutter 16pt 안쪽. 탭 바나 키보드가 있으면 그 위, 없으면 하단 안전 영역 위 16pt |
| 모양 | 바탕 text, 글자 surface와 bodyMedium. control 모서리, 세로 controlVertical 10pt와 가로 controlHorizontal 14pt 여백. 줄 수 제한과 그림자 없음 |
| 표시 시간 | 짧은 표시 2초, 긴 표시 3.5초. 어느 쪽인지는 문구를 정한 도메인이 정함 |
| 겹침 | 한 번에 하나. 새 토스트가 지금 토스트를 바로 대체 |
| 범위 | 앱 전체의 맨 위 층. 시트와 전체 화면 덮개 위에도 보이고 화면 이동과 루트 교체 뒤에도 표시 시간 동안 남음 |
| 조작 | 누를 수 없고 아래 화면의 터치를 막지 않음 |
| 전환 | 나타날 때 elementEnterMillis 200ms, 사라질 때 elementExitMillis 150ms 페이드. 동작 줄이기에서도 페이드만 사용 |

<br>

### 3-3-5 글자와 아이콘

번들 글꼴 Pretendard(400, 500, 700)와 MaruBuri(400, 700)를 쓰고 각 글자 토큰을 [기준 텍스트 스타일](#3-3-7-디자인-토큰)에 연동해 Dynamic Type(iOS의 시스템 글자 크기 설정)으로 키운다. 한 줄의 높이는 토큰의 행간을 크기로 나눈 비율에 현재 크기를 곱한 값이고 읽는 본문 두 역할의 자간은 현재 크기의 -2%다. ([I-039](DECISIONS.md#i-039), [I-051](DECISIONS.md#i-051))

| 규칙 | 조건 |
|---|---|
| 서체 | MaruBuri는 bodyReading과 bodyReadingSmall에만. 버튼, 라벨과 제목에 쓰지 않음 |
| 굵기 | 400, 500, 700만. 번들에 없는 600을 요구하지 않음 |
| 기본 | 화면 기본 글자 스타일 bodyMedium, 기본 색 text. 앱 내용에 시스템 글꼴과 시스템 기본 강조색이 새지 않음 |
| 큰 글자 | 고정 높이 대신 최소 높이. 가로 배치가 넘치면 줄을 바꾸거나 세로로 쌓음 |
| 숫자 | 고정폭 숫자는 도메인이 정한 자리(이프 잔액과 내역 금액 등)에만 |

아이콘은 원본 SVG를 Asset Catalog(앱에 묶는 리소스 목록)에 템플릿 렌더링(쓰는 쪽 색으로 칠하는 방식)으로 둔다. 크기는 iconTiny 12pt, iconSmall 16pt, icon 20pt, 탭 바 tabIcon 24pt이며 하단 탭은 filled와 outline 쌍을 둔다. SF Symbols(Apple의 시스템 아이콘 모음)는 시스템 뒤로 버튼처럼 시스템 UI 안에서만 쓴다. 이프 마크는 이미지로 두고 옆 글자 크기에 맞춰 함께 커진다. 원본 SVG 출처가 확인되지 않은 아이콘의 확보 방법은 미정이다. ([I-038](DECISIONS.md#i-038))

<br>

### 3-3-6 접근성

VoiceOver(iOS 화면 낭독기)와 Accessibility Inspector로 아래 규칙을 확인한다.

| 대상 | 규칙 |
|---|---|
| 아이콘만 있는 버튼 | 접근 가능한 이름 필수. 문구는 도메인 |
| 라벨이 있는 아이콘 | 장식으로 숨겨 이름을 두 번 읽지 않음 |
| 숫자 묶음 | 아이콘과 값을 한 요소로 묶어 “턴 15회”처럼 한 문장으로 읽힘 |
| 선택 상태 | 색과 모양 두 가지로 표시하고 VoiceOver에는 선택 상태 전달 |
| 탭 바 | 시스템이 이름, 위치와 선택을 읽음. 앱이 이름이나 상태를 덧붙이지 않음 |
| 헤더 | 탭 루트와 하위 화면 제목은 머리글. 홈 로고는 머리글 “홈” |
| 선택 행 | 행 전체가 한 요소이고 라벨과 상태를 한 번 읽음 |
| 요청 버튼 | 처리 중에도 이름 유지, 비활성 상태 전달 |
| 로딩 골격과 장식 | 골격 조각, 마스코트와 장식 이미지는 탐색 대상에서 제외 |
| 토스트 | 나타날 때 문구를 한 번 알림. 포커스를 옮기지 않음 |
| 시트와 알림창 | 열리면 안쪽으로 포커스, 닫히면 연 요소로 복귀. 열린 동안 아래 화면은 탐색 대상 아님 |

<br>

### 3-3-7 디자인 토큰

화면은 `ManyakTheme`의 토큰으로만 값을 읽고 팔레트 값을 화면 코드에 적지 않는다. 토큰 값의 기준은 `ManyakDesignSystem`의 토큰 파일이며 첫 값의 출처는 [IOS 기반 결정 기록](../../platform/CLIENT/IOS/DECISIONS.md)의 I-020을 따른다. 이 문서의 길이 단위는 pt이고 글자 크기는 Dynamic Type 기본 크기에서의 값이다. ([I-034](DECISIONS.md#i-034))

| 글자 토큰 | 기준 텍스트 스타일 |
|---|---|
| labelTiny | caption2 |
| labelSmall, bodySmall | caption |
| labelLarge, bodyMedium, bodyMediumStrong, bodyReadingSmall | footnote |
| bodyLarge, bodyLargeStrong, bodyReading | callout |
| titleMedium, titleMediumStrong | body |
| titleLarge | title3 |
| headlineSmall | title2 |

화면 전환과 탭 전환은 시스템 기본이라 전환 시간 토큰을 쓰지 않는다. ([I-040](DECISIONS.md#i-040))
