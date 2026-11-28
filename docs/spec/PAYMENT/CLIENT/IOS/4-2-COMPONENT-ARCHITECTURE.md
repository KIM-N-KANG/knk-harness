# 4-2 컴포넌트 구조: iOS

<br>

### 4-2-1 책임과 의존 방향

| 구성 | 책임 |
|---|---|
| `ManyakCredit` | 출석과 내역 API, 정책과 체험 저장소 구현, 이프 충전 화면과 Store. 출석, 내역, 정책, 체험 포트를 구현 |
| `ManyakCommon` | 정책, 체험, 출석과 내역 조회 포트, 내역 줄 entity. 부족 시트와 내역의 공용 절차, 내역 줄 문구, 출석 결과와 새로고침 실패 문구 |
| `ManyakDesignSystem` | 이프 마크와 수치, 잔액 카드와 내역 버튼, 부족 시트와 그 문구, 내역 행과 목록 상태 표현 |
| `ManyakChat`, `ManyakCreate` | 동작별 적용가와 잔액 선검사, 입력 보존, 부족 상태와 분석 이벤트 |
| 앱 타깃 `Manyak` | 시작 때 정책 조회, 회원 체험 조회, 공용 값 전달과 충전 목적지 조립. 무료 충전 탭의 친구 초대 줄은 `ManyakMy`의 줄을 넘김. 체험 저장소를 정리 등록 배열에 등록 |
| `ManyakNavigation` | 처음 내역 탭을 열지 나타내는 라우트 값과 푸시 경로의 `tab` 해석 |

충전 화면과 부족 시트는 같은 출석 구현을, 충전 내역 탭과 채팅 메뉴는 같은 내역 구현을 쓴다. `ManyakChat`과 `ManyakCreate`는 `ManyakCredit`과 `ManyakMy`를 참조하지 않는다. 공용 절차는 상태 변경을 호출 Store에 전달하고 별도 Store를 만들지 않는다. 어느 타깃도 StoreKit을 링크하지 않고 상품 목록과 웹 충전 주문 API를 부르지 않는다. ([공통 4-1](../4-1-CONTRACT.md), [IOS 기반 1-2](../../../../platform/CLIENT/IOS/1-COMPONENT-ARCHITECTURE.md#1-2-모듈과-허용-의존))
