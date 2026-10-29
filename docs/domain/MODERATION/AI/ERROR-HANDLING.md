# 오류 처리

<br>

### 오류별 처리

| 오류 조건 | 처리 | 최종 출력 |
|---|---|---|
| 요청 필수값 누락, UUID나 필드 타입 오류 | 모델 호출 전 종료 | HTTP 422 |
| 이미지 접근 불가, 허용되지 않은 주소, 다운로드 시간 초과 | 해당 이미지 제외<br>정상 이미지가 남으면 검수 계속 | `IMAGE_DOWNLOAD_FAILED` |
| 이미지가 아닌 파일, 미지원 형식, 장당 용량 초과 | 해당 이미지 제외<br>정상 이미지가 남으면 검수 계속 | `IMAGE_INVALID` |
| 이미지 전체 전송 용량 초과 | 진행 중 다운로드 중단, 관련 이미지 전체를 오류로 처리<br>모델 호출 생략 | `IMAGE_INVALID` |
| 조립한 모델 요청의 용량 초과 | 모델 호출 생략 | 이미지가 있으면 `IMAGE_INVALID`<br>이미지가 없으면 `MODEL_CALL_FAILED` |
| 첨부 이미지 모두 준비 실패 | 모델 호출 생략 | 수집한 이미지 오류 |
| 모델이 이미지를 판독하지 못함 | 위반과 구분, 대체 호출 없음 | `IMAGE_UNREADABLE` |
| 모델 호출, 호출 중 설정 또는 응답 검사 실패 | 남은 시간 안에서 대체 모델 1회 호출 | 복구 실패 시 `MODEL_CALL_FAILED` |
| 요청 취소 | 상위로 전파 | 정상 검수 결과로 변환하지 않음 |
| 예상하지 못한 내부 예외 | 상위로 전파 | HTTP 500 |

<br>

### 재시도와 시간 한도

| 대상 | 한도 |
|---|---|
| 모델 호출 | 기본 1회, 실패 시 대체 모델 최대 1회 |
| SDK 재시도, 이미지 다운로드 재시도 | 없음 |
| 대체 호출 제외 | 정상 반려, 이미지 판독 불가 |
| 이미지 준비 | 기본 30초, 미완료 다운로드 취소 |
| 모델 호출 1회 | 기본 60초와 요청의 남은 시간 중 짧은 값 |
| 요청 전체 | 기본 150초, 남은 시간이 없으면 추가 호출 없이 종료 |

<br>

### 실패 출력

| 상태 | 출력 |
|---|---|
| HTTP 200, 검수 실패 | `decision="REJECTED"`, `error_code`에 원인 기록<br>확인한 위반은 `issues`, 이미지별 오류는 `image_errors`에 보존 |
| HTTP 422 | `detail` 배열의 `type`, `loc`, `msg`<br>입력 원문과 검증 문맥 제외 |
| HTTP 500 | 공통 JSON 형식 보장 없음 |

| 대표 오류 선택 | 기준 |
|---|---|
| 이미지 오류가 있음 | `IMAGE_INVALID` → `IMAGE_UNREADABLE` → `IMAGE_DOWNLOAD_FAILED` 순으로 선택 |
| 이미지 오류 없이 모델 검수 실패 | `MODEL_CALL_FAILED` |
| 일부 내용만 검수 완료 | 위반 목록은 보존하되 이미지 오류가 하나라도 있으면 승인하지 않음 |

<details>
<summary><b>실패 응답 예시</b></summary>

<br>

**1) 모델 검수 실패**

```json
{
  "decision": "REJECTED",
  "issues": [],
  "error_code": "MODEL_CALL_FAILED",
  "image_errors": []
}
```

<br>

**2) 이미지 준비 실패**

```json
{
  "decision": "REJECTED",
  "issues": [],
  "error_code": "IMAGE_DOWNLOAD_FAILED",
  "image_errors": [
    {
      "path": "thumbnailUrl",
      "error_code": "IMAGE_DOWNLOAD_FAILED"
    }
  ]
}
```

</details>

<br>

### 전달 실패

| 상황 | 처리 |
|---|---|
| 결과 응답 전달 실패 | 결과 보관과 재전송 없음 |
| 동일 제출본 식별자로 재요청 | 요청마다 별도 검수, 이전 결과 재사용과 중복 제거 없음 |
