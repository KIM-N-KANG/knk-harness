# 4-2 컴포넌트 구조: iOS

기준: [연동 계약](../4-1-CONTRACT.md).

<br>

### 4-2-1 타깃과 의존

신고는 `ManyakReport` 타깃이 맡는다. `ManyakReport`는 `ManyakCommon`, `ManyakNetwork`, `ManyakDesignSystem`과 `ManyakAnalytics`에만 의존하고, 신고가 필요한 `ManyakStory`, `ManyakStudio`, `ManyakChat`만 `ManyakReport`에 의존한다. 기반 타깃에서 `ManyakReport`를 참조하지 않는다. ([IOS 기반 모듈과 허용 의존](../../../../platform/CLIENT/IOS/1-COMPONENT-ARCHITECTURE.md#1-2-모듈과-허용-의존))

| 구성 | 위치 | 책임 |
|---|---|---|
| 신고 상태 | `ManyakReport` Presentation의 값 타입 | 열림, 대상 storyId, 선택 사유, 상세, 전송 중 |
| `StoryReportController` | `ManyakReport` Presentation | 상태 전이, 신고 제출기에 제출 요청, 시트와 제출 시작의 분석 이벤트와 결과 Event. 상태를 따로 보관하지 않음 |
| 신고 시트 | `ManyakReport` Presentation의 SwiftUI 뷰 | 신고 상태와 Intent 콜백만 받아 시스템 시트 안의 내용을 그림. 전송 중 끌어내리기와 바깥 탭 닫기 잠금 ([I-161](DECISIONS.md#i-161)) |
| 신고 요청 | `ManyakReport` Data | reason enum 이름과 변환한 detail 전송, 201 본문 없는 성공 처리 |
| 문구 | `ManyakReport`의 String Catalog | 제목, 설명, 사유, 상세 라벨, 플레이스홀더, 버튼과 결과 토스트 |
| 소비 화면 Store | 스토리 상세, 제작 목록, 채팅 목록, 채팅방 | 자기 State에 신고 상태를 두고 컨트롤러로 전이. 결과를 토스트 Effect로 냄 |
| 신고 제출기 | `ManyakReport`의 앱 수명 객체 | 제출 요청을 화면 수명과 무관하게 끝까지 실행. 결과 토스트와 분석 이벤트를 내고 소비 화면 Store가 남아 있으면 결과를 전달 ([I-162](DECISIONS.md#i-162)) |
| 조립 | 앱 타깃 조립 객체 | 신고 요청 구현과 신고 제출기를 한 번 만들어 소비 타깃의 Store에 넘김 |

화면마다 전송, 분석과 잠금 절차를 복제하지 않는다. 신고 상태를 가진 별도의 공용 Store와 전역 싱글턴을 두지 않으며 앱 수명으로 두는 것은 신고 제출기뿐이다. 컨트롤러는 분석 `source`를 생성자로 받으며 스토리 상세는 `storyDetail`, 제작 목록은 `studio`, 채팅 목록은 `chatList`, 채팅방은 `chat`이다. ([분석 기준 앱 보강 이벤트](../../../../reference/ANALYTICS.md#4-2-15-안드로이드-앱-보강-이벤트-구현knk-1178))

옵션 시트나 채팅방 메뉴에서 신고하기를 누르면 그 시트가 닫힌 뒤 신고 시트를 연다. 신고 시트의 높이, 잠금과 끌기 표시는 공통 시트 규칙을 따른다. ([공통 UI IOS 탭과 화면 복귀](../../../../ui/IOS/3-2-INTERACTION-FLOWS.md#3-2-1-탭과-화면-복귀), [시트, 알림창과 덮개](../../../../ui/IOS/3-3-LAYOUT.md#3-3-3-시트-알림창과-덮개))
