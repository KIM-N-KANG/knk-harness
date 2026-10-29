# 5-1 PAYMENT 웹 검증

자동화 열은 기존 테스트 연결이며 이번 실행 결과가 아니다. 실제 결제창과 기기 복귀는 목킹 검증과 구분한다.

<br>

### 5-1-1 요구사항 대응

| 케이스 | 유저 스토리 | 상위 요구 |
|---|---|---|
| MY-MENU-10, MY-MENU-21, MY-CREDITS-01~03 | PAYMENT-US-001 | [충전 진입](2-2-REQUIREMENTS.md#2-2-1-충전과-체험) |
| MY-CREDITS-17~23 | PAYMENT-US-002 | [보상](../2-2-REQUIREMENTS.md#2-2-4-보상과-내역) |
| MY-CREDITS-04~16, MY-CREDITS-24, MY-CREDITS-37~38 | PAYMENT-US-006 | [내역](../2-2-REQUIREMENTS.md#2-2-4-보상과-내역) |
| MY-CREDITS-25~36, MY-CREDITS-39~43 | PAYMENT-US-007 | [구매와 적립 확인](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인) |
| 채팅과 제작의 비용 및 부족 케이스 | PAYMENT-US-003, PAYMENT-US-004, PAYMENT-US-005 | [비용](../2-2-REQUIREMENTS.md#2-2-2-잔액과-비용), [부족과 입력 보존](../2-2-REQUIREMENTS.md#2-2-5-이프-부족과-입력-보존) |

<br>

### 5-1-2 충전과 내역 케이스

| ID | P | 사전조건 | 절차 | 기대 결과 | 자동화 | 근거 |
|---|---|---|---|---|---|---|
| MY-MENU-10   | P1  | 회원                                              | 이프 카드 확인       | "내 이프" + 잔액(천 단위 콤마) 표시. 조회 중에는 스켈레톤                                                             | ◐ e2e `visual/my-visual`(잔액 표시만)          | PAYMENT-US-001, [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-MENU-21 | P1 | 회원 | 이프 카드 확인 | 잔액 오른쪽에 강조색 버튼 "충전" 하나만 표시(출석 체크·내역 버튼은 없음). 탭하면 `/my/credits`로 이동 | ✅ e2e `my/credits`·`visual/my-visual` | [공통 화면 표현](../3-3-LAYOUT.md), KNK-1092 |
| MY-CREDITS-01 | P0 | 게스트 | 경로 직접 진입 | `/login`으로 replace 이동 | ✅ e2e `my/credits` | [웹 접근 조건](../../../../spec/3-2-web-spec.md#라우팅-테이블) |
| MY-CREDITS-02 | P0 | 회원 | 마이 이프 카드 "충전" 탭 | `/my/credits`로 이동. 뒤로가기 헤더 "이프 충전" 표시, 하단 탭 없음. 진입 기본 탭은 구매 | ✅ e2e `my/credits` | [공통 화면 표현](../3-3-LAYOUT.md), [웹 경로](../../../../spec/3-2-web-spec.md#라우팅-테이블) |
| MY-CREDITS-03 | P1 | 회원 | 최상단 잔액 상자 확인 | 중립 배경 상자에 "내 이프" 라벨이 위, 잔액이 그 아래 오른쪽에 한 단계 큰 글자·천 단위 콤마로 표시. 값은 진입마다 다시 읽은 `creditBalance`이며 내역 합산이 아님 | ✅ e2e `my/credits` | [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-04 | P0 | 회원, 내역 여러 건 | 내역 탭에서 목록 확인 | 최신순 목록. 한 줄은 사유 라벨·대상 스토리·날짜와 오른쪽 금액이고, 획득은 `+`·소모/소멸은 `-`에 절대값·천 단위 콤마. 줄 위아래 여백은 8px | ✅ e2e `my/credits` | [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-05  | P1  | 소모·사용 취소 행의 `title`이 null         | 항목 확인                  | 제목 줄에 "삭제된 스토리" 표시. 보상·소멸 행은 제목 줄 자체를 그리지 않음                                                                        | ✅ e2e `my/credits`           | [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-06  | P1  | `expiresAt`이 있는 획득·소멸 행            | 날짜 줄 확인               | `YYYY-MM-DD · YYYY-MM-DD 만료` 표시. 소멸 행의 만료일은 `expiresAt`이며 `createdAt`을 만료일로 읽지 않음                                          | ✅ e2e `my/credits`           | [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-24  | P1  | KST 자정~오전 9시에 적립된 행(예: `createdAt: 2026-09-01T15:10:00Z`) | 날짜 줄 확인 | 발생일·만료일 모두 KST 기준 날짜(`2026-09-02 · 2026-10-02 만료`). UTC 문자열을 그대로 잘라 하루 전으로 표시하지 않음 | ✅ 단위 — 웹 `lib/format-date`·`my/credits/utils/credit-transaction-display`, 앱 `DisplayDateTest` | §3-1-7 날짜 표시 기준 |
| MY-CREDITS-07 | P1 | 첫 조회 중 | 진입 직후·내역 탭 전환 직후 관찰 | 잔액 상자와 내역 목록 자리에 각각 골격 표시 | 수동 | [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-08 | P1 | 내역 0건 | 내역 탭 진입 | "아직 이프 내역이 없어요" 표시 | ✅ e2e `my/credits` | [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-09 | P0 | 첫 조회가 5xx·네트워크 오류 | 내역 탭 진입 | 목록 자리에 "이프 내역을 불러오지 못했어요"와 "다시 시도하기". 탭하면 다시 조회해 목록 표시하고, 조회 중에는 버튼이 "다시 시도 중..." 비활성 | ✅ e2e `my/credits` | [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-10 | P0 | `nextCursor`가 있는 목록 | 목록 끝까지 스크롤 | 받은 `nextCursor`를 그대로 실어 다음 페이지를 요청하고 아래에 이어 붙임. "더 보기" 버튼 없음 | ✅ e2e `my/credits` | [공통 화면 표현](../3-3-LAYOUT.md), [웹 커서 목록](4-4-EXECUTION.md#4-4-1-정책과-체험-내역) |
| MY-CREDITS-11 | P1 | 다음 페이지 조회가 실패 | 목록 끝까지 스크롤 | 이미 그린 목록을 지우지 않고 목록 아래 재시도 버튼만 표시하며 자동 재요청을 멈춤. 탭하면 다음 페이지를 이어 붙임 | ✅ e2e `my/credits`(실제 마지막 내역 로딩 후 스크롤) | [공통 화면 표현](../3-3-LAYOUT.md), [웹 커서 목록](4-4-EXECUTION.md#4-4-1-정책과-체험-내역), KNK-1207 |
| MY-CREDITS-12 | P2 | 서버가 라벨 없는 `reason`을 내려줌 | 항목 확인 | 그 줄만 "이프 변동"으로 그리고 나머지 목록은 그대로 표시 | 수동 | [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-13 | P2 | `/my`에서 진입 | 뒤로가기 헤더 탭 | `/my`로 복귀 | 수동 | [웹 헤더](../../../../design/1-1-web-design.md#상단-헤더하단-네비게이션) |
| MY-CREDITS-14 | P1 | 내역 탭을 한 번 보고 `/my`로 돌아온 상태 | "충전" → 내역 탭으로 다시 진입 | 남겨 둔 목록을 그대로 쓰지 않고 첫 페이지부터 다시 조회(스크롤 위치도 목록 맨 위). 그사이 발생한 내역이 바로 보임. 탭을 무료 충전으로 옮겼다 돌아와도 같음(비활성 탭은 언마운트) | ✅ e2e `my/credits` | [웹 커서 목록](4-4-EXECUTION.md#4-4-1-정책과-체험-내역), KNK-1083 |
| MY-CREDITS-15 | P1 | 회원 | 탭 줄 확인 | "구매"·"무료 충전"·"내역" 세 탭을 밑줄 탭으로 표시하고 `tab` 쿼리 없이 진입하면 구매가 선택됨. 탭을 바꿔도 URL은 `/my/credits` 그대로 | ✅ e2e `my/credits` | [공통 화면 표현](../3-3-LAYOUT.md), KNK-1092·1297 |
| MY-CREDITS-16 | P1 | 회원, 내역이 한 화면을 넘김 | 내역 탭에서 아래로 스크롤 | 잔액 상자와 탭 줄은 제자리에 남고 탭 패널만 스크롤됨 | ◐ e2e `visual/my-visual`(정적 상태만) | [공통 화면 표현](../3-3-LAYOUT.md), KNK-1092 |
| MY-CREDITS-17 | P1 | 회원 | 무료 충전 탭 확인 | 중립 배경 상자에 "매일 출석하고 / 매일 N 이프 받으세요" 두 줄 제목(N은 `GET /credits/policies`의 `attendanceReward`), 그 아래 가로 전폭 강조색 "출석 하기" 버튼, 버튼 아래 오른쪽 정렬 보조 문구 2줄("매일 오전 00시에 초기화돼요" → "보상으로 받은 이프는 적립일로부터 30일 동안 사용할 수 있어요") 순으로 표시 | ✅ e2e `my/credits`·`visual/my-visual` | [공통 화면 표현](../3-3-LAYOUT.md), §3-1-7 이프 정책 수치 표시, KNK-1092·1095 |
| MY-CREDITS-18 | P1 | 회원, 오늘 미출석(`attendedToday: false`) | "출석 하기" 버튼 탭 | "출석 체크 보상으로 {amount} 이프를 받았어요" 토스트 + 잔액 상자 자동 갱신(me 재조회) + 버튼이 "출석 완료" 비활성으로 전환 | ✅ e2e `my/credits` | PAYMENT-US-002 (구 MY-MENU-11) |
| MY-CREDITS-19 | P2 | 회원, 오늘 출석 완료(`attendedToday: true`) | 무료 충전 탭 진입 | 진입 시부터 "출석 완료" 비활성 버튼 표시(중복 적립 불가) | ✅ e2e `my/credits` | PAYMENT-US-002, [공통 화면 표현](../3-3-LAYOUT.md)|
| MY-CREDITS-20 | P2 | 출석 요청이 200 `rewarded: false`(서버 중복 판정) | "출석 하기" 탭 | "오늘은 이미 출석 체크했어요" 안내 토스트. 적립 없음 | 수동 | 구현(`use-claim-attendance`) (구 MY-MENU-13) |
| MY-CREDITS-21 | P2 | 출석 API가 5xx·네트워크 오류로 실패 | "출석 하기" 탭 | "출석 체크에 실패했어요" 토스트. 버튼은 다시 활성화되어 재시도 가능. 요청 중에는 문구 자리에 "출석 체크 중" 스피너 + 비활성 | 수동 | §3-1-7 이프·초대 (구 MY-MENU-14) |
| MY-CREDITS-22 | P1 | 회원 | 무료 충전 탭의 친구 초대 줄 탭 | 출석 상자 32px 아래에 마이와 같은 친구 초대 줄(라벨 + 강조색 "하고 N 이프 받기") 표시. 탭하면 `/my/invite`로 이동 | ✅ e2e `my/credits` | [공통 화면 표현](../3-3-LAYOUT.md), KNK-1092·1095 |
| MY-CREDITS-23 | P1 | 회원, 서버 `GET /credits/policies`의 `attendanceReward`가 평소와 다른 값(예: 운영 700이 아닌 dev의 350) | 무료 충전 탭 진입 | 출석 제목이 서버 값을 그대로 표시(배포 없이 따라감). 조회 실패·응답 전에는 수치 자리에 `000`을 쉬머와 함께 그리고 문구 골격은 유지 | ✅ e2e `my/credits` | §3-1-7 이프 정책 수치 표시, KNK-1095 |
| MY-CREDITS-25 | P0 | 회원 | 구매 탭 확인 | `GET /credits/products` 순서대로 한 줄씩 표시. 왼쪽 "N 이프"(기본), 오른쪽 강조색 "N원"(웹 가격) 버튼. 보너스가 있는 상품만 기본 아래 강조색·굵은 "+N 이프". 줄 사이 구분선 없이 16px 간격. 앱 가격은 노출하지 않음. 목록 아래 "구매한 이프는 적립일로부터 5년 동안 사용할 수 있어요" | ✅ e2e `my/credits`·`visual/my-visual` | §3-1-7 유료 충전, [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1297 |
| MY-CREDITS-26 | P0 | 회원 | 가격 버튼 탭 | `POST /users/me/credits/orders`에 그 상품의 `productId`를 실어 보내고 201의 `paymentUrl`로 전체 이동. 요청 중에는 누른 버튼에 스피너, 모든 가격 버튼 비활성 | ✅ e2e `my/credits` | [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1297 |
| MY-CREDITS-27 | P1 | 주문 생성이 4xx·5xx·네트워크 오류 | 가격 버튼 탭 | 이동하지 않고 "결제를 시작하지 못했어요" 토스트. 버튼은 다시 활성화되어 재시도 가능 | ✅ e2e `my/credits` | §3-1-7 유료 충전, KNK-1297 |
| MY-CREDITS-28 | P1 | 상품 조회가 5xx·네트워크 오류 | 구매 탭 진입 | 목록 자리에 "충전 상품을 불러오지 못했어요"와 "다시 시도하기". 탭하면 다시 조회해 목록 표시. 조회 중에는 줄 골격 표시 | ✅ e2e `my/credits` | §3-1-7 유료 충전, KNK-1297 |
| MY-CREDITS-29 | P0 | 결제창 이동 전 남긴 대기 주문이 있고 주문이 `PENDING`→`COMPLETED` | 결제창에서 복귀 화면을 거쳐 `/my/credits`로 복귀 | 잔액 아래 "결제 확인" 카드에 스피너 + "결제를 확인하고 있어요"(2초 간격 조회). `COMPLETED`가 되면 "N 이프가 충전됐어요"(N은 `totalCredits`)로 바뀌고 잔액 상자가 `GET /auth/me` 재조회 값으로 갱신. `COMPLETED` 확정 시점에 대기 주문 기록이 삭제되고 카드는 남음. 닫기(X)로 카드가 사라짐 | ✅ e2e `my/credits` | §3-1-7 결제 결과, [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1297, KNK-1314 |
| MY-CREDITS-30 | P1 | 대기 주문 조회가 404 | 복귀 | "확인할 수 없는 주문이에요" + 닫기. 다시 확인 버튼 없음 | ✅ e2e `my/credits` | §3-1-7 결제 결과, KNK-1297 |
| MY-CREDITS-31 | P1 | 대기 주문 조회가 5xx·네트워크 오류 | 복귀 | "결제 확인에 실패했어요"와 "다시 확인". 자동 재조회는 멈추고, 탭하면 처음부터 다시 폴링 | ✅ e2e `my/credits` | §3-1-7 결제 결과, KNK-1297 |
| MY-CREDITS-32 | P2 | 주문이 30회(약 60초) 조회 후에도 `PENDING` | 복귀 후 대기 | "아직 결제 확인이 안 됐어요"와 "다시 확인" 표시, 자동 조회 중단 | ✅ 단위 — 웹 `my/credits/utils/credit-order-confirmation` | §3-1-7 결제 결과, KNK-1297 |
| MY-CREDITS-33 | P2 | 대기 주문 없음 또는 24시간 지난 기록 | `/my/credits` 진입 | 확인 카드를 그리지 않음 | ✅ e2e `my/credits`(없음)·단위 `pending-credit-order-storage`(만료) | [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1297 |
| MY-CREDITS-34 | P0 | 대기 주문이 `REFUNDED`(또는 `COMPLETED`·404)로 확정돼 카드가 표시된 상태 | 닫기 없이 새로고침 또는 재진입 | 확인 카드를 다시 그리지 않고 주문 재조회도 없음. 확인 중·60초 초과·조회 오류 상태는 기록이 남아 재진입 시 다시 확인 | ✅ e2e `my/credits` | [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1314 |
| MY-CREDITS-35 | P1 | 가격 버튼 탭으로 주문 생성 성공 후 결제창으로 이동 | 브라우저 뒤로가기로 문서가 bfcache 복원(`pageshow` persisted) | 가격 버튼의 스피너·비활성이 풀려 다시 주문 가능 | ✅ e2e `my/credits`(이벤트 직접 발생) | [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1314 |
| MY-CREDITS-37 | P1 | 무료 충전 탭 | 탭 내용을 아래로 당겼다 놓기 | STORY-LIST-30과 같은 표시자로 프로필(잔액·출석 여부)과 정책 수치를 다시 조회 | 수동 | 웹 Spec 화면 전환 규칙, KNK-1355 |
| MY-CREDITS-38 | P1 | 내역 탭, 목록이 맨 위 | 목록을 아래로 당겼다 놓기 | 같은 표시자로 내역을 첫 페이지부터 다시 조회하고 응답 전까지 기존 줄 유지. 구매 탭에는 당김 없음 | 수동 | 웹 Spec 화면 전환 규칙, KNK-1355 |
| MY-CREDITS-39 | P0 | 회원, 마이 → "충전"으로 진입 | 가격 버튼 → 결제창 → 결제 완료 화면의 이동 버튼으로 복귀 → 뒤로가기(앱 바·기기) | 복귀 화면(`/my/credits/return`)이 결제 전 충전 화면까지 되감아 `/my/credits`에 결제 확인 카드가 뜸. 뒤로가기는 결제창이 아니라 `/my`로 감 | ✅ e2e `my/credits` | [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1558 |
| MY-CREDITS-40 | P2 | 되감을 기록 없음(다른 탭에서 결제, 기록 삭제) | `/my/credits/return` 진입 | 되감지 않고 `/my/credits`로 바꿔 끼움 | ✅ e2e `my/credits`·단위 `payment-return-history`(상한·손상 기록) | [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1558 |
| MY-CREDITS-41 | P1 | 그로블 상품 설정의 이동·진입 페이지가 `/my/credits/return` | iOS Safari·Android Chrome·인앱 브라우저 실기기에서 실제 결제 후 복귀, 결제 완료 화면 닫기로도 복귀 | MY-CREDITS-39와 같은 결과. 결제창에서 결제 없이 뒤로 돌아온 뒤 다시 결제해도 같음 | 수동 | [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1558 |
| MY-CREDITS-42 | P1 | 회원, 알림·주소로 `/my/credits` 바로 진입(아래 기록 없음) | 뒤로가기 헤더 탭 | `/my`로 교체 이동. 결제 복귀 되감기 뒤(MY-CREDITS-39)에는 그대로 결제 전 화면으로 뒤로가기 | ✅ e2e `my/credits` | 웹 Spec 화면 전환 규칙, KNK-1613 |
| MY-CREDITS-43 | P1 | 회원 | `/my/credits?tab=history&utm_source=push`, `?tab=free`, `?tab=purchase`, `?tab=모르는값`으로 진입 | 각각 내역, 무료 충전, 구매, 구매 탭이 처음 선택됨. 주소에서 `tab`만 지워지고 `utm_source` 등 다른 쿼리는 남음. 그 뒤 구매 탭에서 결제하고 되감겨 와도 쿼리 탭으로 바뀌지 않음 | ◐ e2e `my/credits`(history, free) | [웹 화면 전환](../../../../spec/3-2-web-spec.md#화면-전환-규칙), KNK-1842 |
| MY-CREDITS-36 | P1 | 대기 주문 기록이 있는 회원 | 로그아웃·세션 만료 로그아웃·회원 탈퇴 | 대기 주문 기록 삭제. 같은 기기의 다음 계정에 이전 계정의 확인 카드가 뜨지 않음 | ✅ e2e `my/session-expiry`(만료)·수동(로그아웃·탈퇴) | [웹 유료 충전](2-2-REQUIREMENTS.md#2-2-2-구매와-적립-확인), KNK-1314 |

실제 결제와 기기 복귀는 MY-CREDITS-41로 검증한다. 채팅과 제작에서 시작한 부족 안내는 해당 동작의 검증과 함께 확인한다. ([채팅 한도](../../../../qa/chats.md#chat-limit--회원-이프체험-표시), [제작 검증](../../../../qa/stories.md))
