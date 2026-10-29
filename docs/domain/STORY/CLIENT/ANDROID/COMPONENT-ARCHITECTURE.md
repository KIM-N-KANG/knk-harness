# Android STORY 구성

기준: [공통 계약](../CONTRACT.md), [Android 화면](INFORMATION-ARCHITECTURE.md).

<br>

### 소유권

| 경계 | 책임 |
|---|---|
| home | 공개 목록과 필터, 커서 및 페이지 조회 |
| home/onboarding | 오리지널 선택, 가입 안내 기록과 채팅 시작 |
| studio | 제작 카드 조합, 서버 제출본 목록과 삭제 |
| create | 간편 제작의 입력과 생성, 초안 및 완성 요청 저장과 실행 |
| create/general | 일반 제작과 수정의 폼 entity, 순수 변환, API와 Room data, MVI 화면 |
| navigation | 초안 ID와 재개 여부, 제출본 및 스토리 ID를 담는 목적지 |
| app | 탭, 상세와 제작 진입 연결, 완료 목적지 및 온보딩 루트 교체 |
| common | 공유하는 초안 접근과 채팅 시작 계약, 오류 문구 |
| designsystem | 카드, 옵션 시트, 이미지 뷰어, 선택 테두리, 마스코트 재료와 순환 문구 |

ViewModel은 입력과 화면 상태 및 실행 수명을 소유하며 Composable 재구성에 도메인 조회와 복구를 연결하지 않는다. 제작 저장소는 ActivityRetained 수명이며 화면 destination의 STOP을 앱 백그라운드로 해석하지 않는다.

<br>

### 공용 조립

일반 제작과 간편 제작은 헤더, 저장 버튼, 접는 항목과 장르 검색을 함께 쓴다. 일반 제작의 방식 선택 일러스트와 분량 슬라이더는 해당 기능이 소유하고 두 번째 사용처 전에 designsystem으로 올리지 않는다.

폼은 로컬 안정 ID와 서버 ID를 구분한다. 순수 변환이 설정 글, 인물과 장르 및 baseline을 다루며 검수 경로는 제출 시점의 안정 ID로 연결한다. 이미지 업로더는 presign과 별도 무인증 업로드 클라이언트를 조립한다.

마스코트는 시간에서 자세를 계산하는 안무와 그리기 전용 Canvas로 분리한다. 공용 몸과 눈, 붓과 베레모 및 붓길 해석을 사용하고 studio는 완성 표지 장면만 소유한다. API와 폴링은 애니메이션이 소유하지 않는다.
