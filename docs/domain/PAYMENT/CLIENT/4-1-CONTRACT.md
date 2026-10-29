# 4-1 PAYMENT 연동 계약

<br>

### 4-1-1 서버 계약과 사용처

| 작업 | 기준 계약 | 클라이언트 책임 |
|---|---|---|
| 잔액과 출석 여부 | [ACCOUNT 세션 조회](../../ACCOUNT/BACKEND/4-2-CONTRACT.md#4-2-5-세션-조회) | `creditBalance`, `attendedToday`로 표시. 내역과 분리 |
| 정책 | [정책값 조회](../BACKEND/4-2-CONTRACT.md#4-2-3-정책값-조회) | 운영 수치 표시, 미수신 자리표시 |
| 체험 | [체험 사용량 조회](../BACKEND/4-2-CONTRACT.md#4-2-4-체험-사용량-조회) | 한도와 사용량 계산, 회원 및 게스트 격리 |
| 출석 | [출석 보상](../BACKEND/4-2-CONTRACT.md#4-2-6-출석-보상) | 지급과 이미 출석한 결과 구분, 회원 정보 재조회 |
| 내역 | [이용내역 조회](../BACKEND/4-2-CONTRACT.md#4-2-7-이용내역-조회) | 서버 순서와 커서 유지, 사유 라벨과 날짜 변환 |
| 웹 상품과 주문 | [상품 목록](../BACKEND/4-2-CONTRACT.md#4-2-2-상품-목록-조회), [주문 생성](../BACKEND/4-2-CONTRACT.md#4-2-8-웹-충전-주문-생성), [주문 조회](../BACKEND/4-2-CONTRACT.md#4-2-9-주문-조회) | 웹 가격, 결제 이동과 적립 확인 |
| 채팅 가격 | [CHAT 모델 목록](../../CHAT/BACKEND/4-2-CONTRACT.md#4-2-14-모델-목록) | CHAT의 모델별 적용가 사용 |

<br>

### 4-1-2 정책과 체험 해석

| 값 | 해석 |
|---|---|
| `signupReward`, `inviteReward`, `attendanceReward` | 각 보상 표시. 토스트와 공유는 해당 시점 값 사용 |
| `inviteMonthlyCap` | 초대자 보상의 월 적립 횟수. 금액 상한이 아님 |
| `storyCreationCost` | 간편 제작 체험 소진 뒤 적용하는 정가 |
| `chatImageCost` | 실시간 이미지 정가. 체험과 조합하는 계산은 CHAT |
| `chatTurnCost` | 기존 호환 필드. 모델별 가격의 기준으로 사용하지 않음 |
| `used`, `limit` | `limit - used`가 잔여. `limit: null`은 무제한 |
| 회원 `chatTurn` | `LITE` 턴에만 적용. 모델별 계산은 CHAT |
| `rewarded: true` | 이번 출석 지급. `amount`로 결과 안내 |
| `rewarded: false` | 이미 출석한 성공. 추가 적립 없이 완료 처리 |

<br>

### 4-1-3 내역 변환과 오류

| 입력 | 처리 |
|---|---|
| `type` | `EARN`은 양수 표시, `SPEND`와 `EXPIRE`는 음수 표시. 수치는 `abs(amount)` |
| `reason` | 앞 단계의 라벨로 변환. 알 수 없는 값은 일반 변동 |
| `createdAt` | 발생일. KST로 변환 |
| `expiresAt` | 획득의 만료 예정일 또는 소멸된 로트의 실제 만료일. 없으면 생략 |
| `nextCursor` | 다음 요청에 그대로 전달. 파싱하거나 재구성하지 않음 |
| 출석 오류 | 실패 안내 후 재시도. 지급으로 표시하지 않음 |
| 내역 오류 | 첫 페이지와 다음 페이지 실패를 구분 |
| 소모의 402 | 유료 동작의 회원 상태와 화면 위치에 따라 부족 시트, 로그인 안내, 제작 실패 안내로 변환 |

라벨과 문구는 화면 표현에서 정한다. ([3-3-2 내역](3-3-LAYOUT.md#3-3-2-내역), [2-2-5 부족 결과](2-2-REQUIREMENTS.md#2-2-5-이프-부족과-입력-보존))
