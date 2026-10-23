# 6. 배포

이 문서는 ADMIN 도메인이 포함된 서버의 배포 단위와 의존 대상, 배포 경로, 이 도메인이 읽는 환경 변수와 시크릿, 배포 조건, 설정 변경, 적용과 복구 절차를 정한다.

서버 전체 배포 절차 중 ADMIN 도메인과 관련된 항목만 다룬다.

토큰 수명은 오류 처리에 있으며 관측 스택과 조회 도구는 관측에 있다. ([5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도)와 [5-4-1 관측 스택](5-4-OBSERVABILITY.md#5-4-1-관측-스택))

<br>

### 6-1 배포 단위와 의존성

배포 단위는 서버 컨테이너 하나다. ADMIN만 따로 배포하지 않는다. 관리자 페이지는 별도 저장소에서 Vercel에 배포하며 이 문서의 범위 밖이다. 이 도메인이 기동과 요청 처리에 쓰는 의존 대상은 다음과 같다.

| 의존 대상 | 내용 | ADMIN 도메인이 쓰는 것 |
|---|---|---|
| PostgreSQL | 기동 시 마이그레이션 적용 | 관리자 역할과 감사 로그 테이블<br>Amplitude 조회 값 테이블 |
| Google | 공개 키 집합 | 계정 도메인의 검증기 경유 |
| Secrets Manager | Terraform이 태스크 정의에 참조 주입 | 대칭키, Google client ID, Amplitude API 키와 시크릿 키 |
| Amplitude | Dashboard REST API | 분석 지표 |
| Google Cloud Storage | Play Console 일괄 보고서 버킷 | 설치 지표 |
| AWS CloudWatch, ECS | 서버 태스크 역할의 읽기 권한 | 인프라 지표 |
| Redis | 다른 도메인과 같은 인스턴스 | Amplitude 배치의 5분 슬롯 선점 |
| Data Prepper | 트레이스를 받아 OpenSearch에 적재 | 트레이스 전송 |

<br>

| 의존 대상 | 연결과 설정 실패 시 동작 |
|---|---|
| 대칭키 | 비어 있거나 32바이트 미만이면 기동 실패 |
| Google client ID | 비어 있으면 관리자 로그인 전부 거절<br>기동은 정상 |
| PostgreSQL | 연결할 수 없으면 기동 실패 |
| 관리자 역할 행 없음 | 기동은 정상<br>아무도 로그인할 수 없음 |
| 팀 계정 제외 목록 | 정수가 아닌 값이 있으면 기동 실패<br>빈 값이면 제외 없이 집계 |
| Amplitude 키 | 둘 중 하나라도 비면 분석 도구 지표는 저장 값만 응답하고 저장 값도 없으면 사용 불가<br>기동은 정상 |
| Amplitude | 연결할 수 없으면 분석 도구 지표의 새 날짜만 받지 못함<br>저장 값이 있는 날짜는 그대로 응답 |
| Play 서비스 계정 키 | 비면 설치 지표만 사용 불가<br>기동은 정상<br>키는 첫 보고서 조회 때 해석하므로 base64나 서비스 계정 JSON이 아니어도 기동은 정상이고 설치 지표만 사용 불가<br>그때 로그 `reason`은 HTTP 상태 없는 `http_error` |
| Google Cloud Storage | 연결할 수 없으면 설치 지표만 사용 불가<br>캐시가 있으면 캐시로 응답 |
| CloudWatch, ECS | 권한이 없거나 연결할 수 없으면 인프라 지표만 사용 불가<br>기동은 정상<br>그 범위의 캐시가 있으면 캐시로 응답 |
| 인프라 지표 설정 | 비어 있는 리소스 묶음은 응답에서 `null`<br>모두 비면 인프라 지표만 사용 불가<br>기동은 정상 |
| Redis | 연결할 수 없으면 Amplitude 배치와 백필만 건너뜀<br>화면 요청은 그대로 값을 받음 |
| Data Prepper | 추적을 켜고 주소가 비면 기동 실패<br>추적이 꺼지면 스팬을 만들되 전송하지 않음 |

<br>

### 6-2 배포 경로

테스트와 빌드를 마친 뒤 이미지를 게시하고 배포한다. `main` push는 같은 소스 트리의 `dev` 성공 실행이 있으면 테스트를 다시 실행하지 않는다. `dev`로 PR을 올리면 테스트와 빌드만 한다.

| 단계 | 개발 | 운영 |
|---|---|---|
| 자동 시작 | `dev` push | `main` push |
| 머지 규칙 | 기능 브랜치에서 `dev`로 squash | `release/vX.Y.Z`에서 `main`으로 merge commit |
| 이미지 태그 | 커밋 SHA 앞 7자리<br>환경 태그 `dev` | 커밋 SHA 앞 7자리<br>배포 시 `latest` 태그 지정<br>실패하면 이전 digest로 복원 |
| 상태 검사 | 배포 완료, 서버 컨테이너 정상, health `UP` | 동일 |

<br>

### 6-3 환경 변수와 시크릿

환경 변수가 설정 파일의 값보다 우선한다. 설정은 기동 시 읽으므로 변경 뒤 새 태스크를 시작해야 적용된다. 값은 Terraform이 태스크 정의에 주입하고 시크릿은 Secrets Manager에서 주입한다. 이 도메인이 읽는 설정만 적는다. 기본값이 "빈 값"이면 변수가 없어도 빈 문자열로 기동한다. "없음"이면 변수가 없을 때 기동에 실패한다.

<br>

**1. 대시보드**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_ADMIN_DASHBOARD_EXCLUDED_USER_IDS` | `1,2,3,4,5,10,11,206,207` | 주입 없음 | 콤마 구분 회원 내부 ID<br>대시보드 요약과 차트, DB 분석 지표 중 신규 가입자, 턴 도달률, 채팅 옵션 비중에서 제외하고 AI 비용에는 적용하지 않으며 기본값은 운영 Terraform `grafana/dashboards/service-stats.json`의 소비 활동 제외 목록과 같음<br>제작 세션 차트는 이 목록에서 `MANYAK_OFFICIAL_USER_PUBLIC_ID`의 회원을 뺀 나머지를 제외 |

관리자 토큰 수명과 대상 클레임 값, 분석 도구 지표의 오늘 값 유효 시간 10분과 확정일 기준(오늘에서 2일 이전), 분석 지표 호출 시간 한도 5초, 실패 쿨다운 60초, 캠페인 분석과 사용자, 전환, 기능 지표의 조회 시간 한도 10초와 갱신 시간 한도 60초, 태스크당 비용 예산(최근 5분 500)과 그 가운데 배치와 백필 몫(300), 분석 값 배치의 실행 간격 5분과 새벽 배치 시작 시각 KST 03:00, 초기 백필 시작일 2026-07-01, 배치 켜기 여부(기본 켬, 테스트 프로파일은 끔), 유입 소스 목록(`ig`, `th`와 `threads`, `dc`), 캠페인 목록(차수, 캠페인 값, 시작일, 종료일, 대상 스토리), AI 모델별 입력과 출력 백만 토큰당 원화 단가 표, 실시간 이미지 장당 원가(초기 48원), 설치 지표의 캐시 시간 1시간, 호출 시간 한도 10초, 실패 쿨다운 60초, 보고서 버킷 이름 `pubsite_prod_7346202752431827582`와 패키지 이름 `app.manyak`, 인프라 지표의 기간 상한 31일과 집계 간격 경계(2일, 7일, 63일), 캐시 60초, 호출 시간 한도 5초, 실패 쿨다운 60초, DB 테이블 크기의 캐시 5분과 개수 상한 100은 설정 파일의 고정값이다.

<br>

**2. 분석 지표와 설치 지표**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_AMPLITUDE_API_KEY` | 빈 값 | 개발과 운영 Secrets Manager `manyak/{env}/app` | 공통 분석 발행기와 같은 키<br>운영 프로젝트 하나뿐이라 개발 서버도 같은 값 |
| `MANYAK_AMPLITUDE_SECRET_KEY` | 빈 값 | 개발과 운영 Secrets Manager `manyak/{env}/app` | Dashboard REST API 기본 인증<br>태스크 정의에 새 시크릿 참조를 추가해야 주입됨 |
| `MANYAK_AMPLITUDE_TEAM_COHORT_ID` | 빈 값 | 개발과 운영 태스크 정의에 같은 값을 직접 기록 | 팀 계정 코호트 ID<br>분석 지표 세분화 조회의 세그먼트 `userdata_cohort` 제외 조건에 사용<br>비어 있으면 제외 없이 조회 |
| `MANYAK_AMPLITUDE_DASHBOARD_BASE_URL` | `https://amplitude.com` | 주입 없음 | US 데이터 센터 |
| `MANYAK_PLAY_STATS_SA_KEY_BASE64` | 빈 값 | 운영 Secrets Manager `manyak/prod/app`만<br>개발은 주입 없음 | Play 보고서 읽기 전용 서비스 계정 키 JSON의 base64<br>태스크 정의에 새 시크릿 참조를 추가해야 주입됨<br>개발 서버는 설치 지표가 사용 불가 |

<br>

**3. 인프라 지표**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_ADMIN_INFRA_ECS_CLUSTER` | 빈 값 | 운영 태스크 정의에 Terraform이 기록 | ECS 클러스터 이름<br>운영 `manyak-prod` |
| `MANYAK_ADMIN_INFRA_ECS_SERVICES` | 빈 값 | 같음 | 콤마 구분의 `표시 키=서비스 이름` 쌍이며 이 순서로 응답<br>운영 `server=manyak-prod,ai=manyak-prod-ai,notification=manyak-prod-notification` |
| `MANYAK_ADMIN_INFRA_ALB` | 빈 값 | 같음 | ALB의 ARN 접미사 `app/manyak-prod-alb/{ID}`<br>Terraform의 `arn_suffix`를 그대로 씀 |
| `MANYAK_ADMIN_INFRA_RDS_INSTANCE` | 빈 값 | 같음 | RDS 인스턴스 식별자<br>운영 `manyak-prod-pg` |
| `MANYAK_ADMIN_INFRA_REDIS_NODES` | 빈 값 | 같음 | 콤마 구분 캐시 클러스터 ID이며 이 순서로 응답<br>운영은 복제 그룹 `manyak-prod-redis-rg`의 구성원 `manyak-prod-redis-rg-001,manyak-prod-redis-rg-002` |
| `MANYAK_ADMIN_INFRA_OPENSEARCH_DOMAIN` | 빈 값 | 같음 | OpenSearch 도메인 이름<br>운영 `manyak-logs`(dev state가 소유하는 공유 도메인) |
| `MANYAK_ADMIN_INFRA_AWS_ACCOUNT_ID` | 빈 값 | 같음 | OpenSearch 지표의 `ClientId` 차원<br>비면 OpenSearch 묶음만 `null` |

- 개발 태스크 정의에는 주입하지 않는다. 개발 서버의 인프라 지표는 사용 불가다.
- 리전은 태스크의 AWS SDK 기본 리전(`ap-northeast-2`)을 쓴다.

**4. 다른 도메인이 관리하는 값**

| 이름 | ADMIN이 쓰는 곳 |
|---|---|
| `MANYAK_AUTH_JWT_SECRET` | 관리자 토큰 서명과 검증<br>바꾸면 발급된 관리자 토큰이 전부 무효 |
| `MANYAK_GOOGLE_CLIENT_IDS` | 관리자 로그인의 신원 증명 대상 검증<br>관리자 페이지의 Google client ID가 목록에 있어야 함 |
| `MANYAK_OFFICIAL_USER_PUBLIC_ID` | 스토리 목록의 `original` 범위 판정<br>제작 세션 차트의 제외 목록 보정<br>비어 있으면 모든 스토리가 `user` |

<br>

**5. 관측**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_TRACING_ENABLED` | `false` | 운영 Terraform 변수 | |
| `MANYAK_OTLP_TRACES_ENDPOINT` | 빈 값 | 추적을 켠 운영 환경에 Data Prepper 내부 주소 주입 | 추적을 켜면 필수 |
| `MANYAK_OTLP_METRICS_ENABLED` | `false` | 운영 Terraform 변수<br>전송 URL과 인증 헤더는 Secrets Manager | Grafana Cloud로 전송 |
| `SENTRY_DSN` | 빈 값 | 개발과 운영 Secrets Manager | |

<br>

### 6-4 배포 조건

| 확인 항목 | 기준 | 자동 여부와 한계 |
|---|---|---|
| 관리자 페이지 client ID | 관리자 페이지가 쓰는 Google client ID가 서버의 허용 목록에 포함 | 수동 검토 |
| 관리자 역할 | 운영 DB에 관리자 역할 행이 있어야 첫 로그인이 가능 | 수동 확인<br>서버는 역할 행 유무를 검사하지 않음 |
| Amplitude 시크릿 | 두 시크릿 JSON에 키 두 개가 있고 태스크 정의가 참조 | 수동 검토<br>운영 Terraform apply가 서버 릴리스보다 먼저 |
| Play 서비스 계정 키 | 운영 시크릿 JSON에 키가 있고 태스크 정의가 참조<br>서비스 계정에 보고서 버킷 읽기 권한 | 수동 검토<br>운영 Terraform apply가 서버 릴리스보다 먼저 |
| 인프라 지표 권한과 설정 | 운영 서버 태스크 역할에 `cloudwatch:GetMetricData`와 세 서비스에 한정한 `ecs:DescribeServices`<br>운영 태스크 정의에 인프라 지표 환경 변수 | 수동 검토<br>`manyak-terraform`의 운영 apply가 필요하고 서버 릴리스와 순서가 바뀌어도 기동은 정상이며 인프라 지표만 사용 불가 |
| 팀 계정 코호트 | 분석 도구에 팀 계정 코호트가 있고 ID가 설정값과 같음 | 수동 확인 |
| 와이어 계약 변경 | 관리자 API 응답이 바뀌면 관리자 페이지와 함께 배포<br>분석 도구 지표의 `pendingDates`와 늘어난 기간 상한은 관리자 페이지가 준비 중 표시와 재요청을 함께 배포 | 수동 검토 |
| 분석 지표 정의 변경 | 조회 조건을 바꾸면 매개변수 해시가 바뀌어 지난 날짜를 처음부터 다시 받음<br>긴 범위는 여러 5분에 걸쳐 채워짐 | 수동 검토 |
| 관리자 경로 추가 | 회귀 테스트가 새 경로를 자동 수집하는지 테스트 결과에서 확인 | CI 자동 |
| 마이그레이션 | 기동 시 실행하므로 새 마이그레이션은 해당 코드보다 먼저 적용<br>재실행해도 같은 결과<br>Amplitude 조회 값 테이블은 서버 저장소의 다음 마이그레이션 번호 | 기동 시 자동 적용<br>마이그레이션 경로 변경 PR은 `tbls lint`와 `dbdoc/` 비교를 CI에서 자동 실행 |
| 코드 테스트 | 전체 테스트 통과 | CI 자동 |
| 컨테이너 기동 | 컨테이너 헬스체크와 `/actuator/health` `UP` | CI 자동 |

<br>

### 6-5 설정 변경

| 변경 대상 | 변경 위치와 적용 | 확인 조건 |
|---|---|---|
| 관리자 역할 부여와 회수 | 운영 DB에서 역할 행 추가 또는 삭제<br>다음 요청부터 반영<br>재배포 없음 | 회수된 계정의 관리자 요청이 권한 없음으로 거절됨<br>감사 로그 조회 응답의 `admin.isAdmin` |
| 관리자 토큰 수명 | 설정 파일 변경 후 재빌드 | 로그인 응답의 `expiresIn` |
| 팀 계정 제외 목록 | 환경 변수 변경 후 새 태스크 시작 | 대시보드 요약의 회원 수 변화 |
| 팀 계정 코호트 구성원 | 분석 도구에서 코호트 편집<br>오늘과 어제 값은 다음 갱신부터 반영<br>확정한 지난 날짜는 반영되지 않아 필요하면 분석 지표 행을 지움 | 분석 지표의 활성 사용자 수 변화 |
| 캠페인 목록 | 설정 파일 변경 후 재빌드와 배포 | 캠페인 목록 응답 |
| AI 모델 단가와 실시간 이미지 장당 원가 | 설정 파일 변경 후 재빌드와 배포 | AI 비용 응답의 `unpricedModels`가 비어 있고 `chatImageUnitCostKrw`가 바꾼 값 |
| 초기 백필 시작일, 배치 몫 | 설정 파일 변경 후 재빌드와 배포 | `admin_analytics_backfill`의 `remaining_days`와 `cost` |
| 저장된 분석 값 다시 받기 | 운영 DB의 `admin_analytics_daily_values` 또는 `admin_analytics_range_values`에서 해당 `metric`과 날짜의 행 삭제<br>재배포 없음 | 다음 요청의 `admin_analytics_refreshed`에서 그 날짜를 받음 |
| Amplitude 키 교체 | Secrets Manager 값 변경 후 새 태스크 시작 | 분석 지표 응답 성공 |
| Play 서비스 계정 키 교체 | Secrets Manager 값 변경 후 새 태스크 시작 | 설치 지표 응답 성공 |
| 대칭키 | Secrets Manager 값 변경 후 새 태스크 시작 | 앱과 관리자 토큰이 모두 무효가 되어 재로그인 |
| 추적과 지표 전송 | 운영 Terraform 변수 변경 후 apply | |

<br>

### 6-6 적용과 복구

**1. 적용 순서**

| 순서 | 작업 | 확인 항목 |
|---|---|---|
| 1 | 설정과 역할 확인 | Google client ID 허용 목록, 관리자 역할 행, 마이그레이션 순서 |
| 2 | 동반 배포 확인 | 관리자 페이지와 함께 배포해야 하는지와 순서 |
| 3 | 배포 실행 | |
| 4 | 적용 결과 확인 | 배포 후 확인 항목 |

<br>

**2. 진행 중인 요청**

| 상황 | 처리와 한계 |
|---|---|
| 롤링 교체 중 관리자 토큰 | 대칭키에만 의존하므로 태스크 교체와 무관 |
| 롤링 교체 중 변경 요청 | 변경과 감사 로그가 한 트랜잭션이라 끊기면 둘 다 남지 않음 |
| 개발 stop-then-start | 교체 중 모든 요청 실패<br>데이터 컨테이너 재시작 |

<br>

**3. 복구**

자동 복구가 실행돼도 서비스가 정상으로 돌아오지 않았을 수 있으므로 실제 서버 상태를 확인한다.

| 상황 | 복구 방식 | 한계와 확인 사항 |
|---|---|---|
| 새 태스크 헬스체크 실패 | 직전 배포로 자동 복귀 | 환경 태그가 실패한 이미지를 가리킬 수 있으므로 다음 재배포 전에 태그 확인 |
| 배포는 정상이나 동작 오류 | revert 커밋 릴리스 또는 이전 이미지를 환경 태그로 다시 태깅한 뒤 새 배포 | health 기반 자동 복구는 관리자 로그인 실패를 탐지하지 않음 |
| 관리자 계정 탈취 의심 | 운영 DB에서 역할 행 삭제 | 다음 요청부터 거절<br>이미 한 변경은 감사 로그로 확인하고 각 도메인의 되돌리기 규칙을 따름 |
| 마이그레이션 적용 후 되돌리기 | 적용된 마이그레이션은 되돌리지 않음 | 새 테이블은 구버전 코드와 호환 |
| 설정 오류 | 잘못된 값을 이전 값으로 복구 후 새 태스크 시작 | 이미지 태그 복원만으로 설정은 복원되지 않음 |
| 잘못 저장된 분석 값 | 해당 행 삭제 | 확정 행도 지우면 다음 요청에서 다시 받음<br>구버전 코드로 되돌려도 테이블은 남고 쓰이지 않음 |

<br>

### 6-7 배포 후 확인

| 확인 항목 | 자료 | 기준 |
|---|---|---|
| 기동 | 해당 배포 ID의 태스크 상태, 헬스체크 `/actuator/health`, 스모크 테스트 | 의도한 이미지로 기동<br>`UP` |
| 관리자 로그인 | 로그 `admin_login_succeeded`<br>`admin_login_rejected` | 역할 있는 계정이 로그인됨 |
| 권한 판정 | 로그 `admin_access_denied` | 급증하지 않음 |
| 대시보드 | 대시보드 요약과 차트 응답 | 모든 지표가 채워지고 분포 차트가 8개 |
| 목록 | 스토리, 채팅, 회원, 결제 목록 첫 페이지 | 성공 응답과 `totalElements` |
| 분석 지표 | 기본 범위의 분석 지표 응답 | 성공 응답과 `daily` 30개, `pendingDates` 빈 배열<br>사용 불가면 `admin_analytics_fetch_failed`의 `reason`<br>배포 전에 받은 지난 날짜는 다시 받지 않음(`admin_analytics_refreshed`의 `fetched_days`가 오늘과 어제 이하) |
| 캠페인 분석 | 캠페인 목록과 기본값의 추이 응답 | 성공 응답과 `campaign`이 목록의 진행 중 항목<br>`budget_exceeded`가 반복되면 호출 묶음 재검토 |
| 사용자, 전환, 기능 지표 | 기본 범위의 사용자 활동, 전환 퍼널 하나, 기능 사용 응답과 DB 지표 응답 | 성공 응답 |
| 분석 값 배치 | 첫 배포 뒤 몇 시간의 `admin_analytics_backfill`<br>다음 날 KST 03:00 이후 로그 | `backfill`의 `remaining_days`가 줄다가 `done`<br>`nightly`가 그날 `done`<br>한 5분 슬롯에 실행 로그가 하나뿐 |
| 설치 지표 | 설치 지표 응답 | 성공 응답과 `asOf`가 오늘에서 며칠 안<br>사용 불가면 `admin_play_stats_fetch_failed`의 `reason` |
| 인프라 지표 | 기본 범위의 인프라 지표와 DB 테이블 크기 응답 | 성공 응답과 `ecs.services` 3개의 `runningTasks` 1 이상, 모든 묶음이 `null` 아님<br>사용 불가면 `admin_infra_metrics_fetch_failed`의 `reason` |
| 감사 로그 | 운영 작업 1건 뒤 감사 로그 조회 | 해당 행이 보임 |

<br>

### 6-8 배포 실패 진단

| 실패 상황 | 확인할 자료와 위치 | 원인별 조치 |
|---|---|---|
| 기동 중 설정 검증 실패 | 시작 로그의 예외 메시지 | 대칭키 길이와 추적 주소 누락 중 해당 값 수정 후 새 태스크 시작 |
| 관리자 로그인이 전부 인증 실패 | 요청 로그<br>Google client ID 시크릿 | 관리자 페이지의 client ID가 허용 목록에 없으면 추가 후 새 태스크 시작 |
| 관리자 로그인이 전부 권한 없음 | 로그 `admin_login_rejected`의 `reason` | `no_role`이면 운영 DB의 역할 행 확인<br>`no_member`면 그 Google 계정으로 앱에 먼저 가입 |
| 모든 관리자 요청이 인증 실패 | 요청 로그<br>관리자 페이지의 쿠키 만료 | 토큰 만료면 재로그인<br>대칭키 변경이면 재로그인 안내 |
| 변경 API가 전부 서버 오류 | Sentry<br>감사 로그 테이블 존재 여부 | 마이그레이션 적용 확인 |
| 백필이 끝나지 않음 | `admin_analytics_backfill`의 `result`, `reason` | `budget_share`만 반복되면 화면 요청이 예산을 먼저 쓰는 중이라 대기<br>`claim_failed`면 Redis 연결<br>`no_credentials`면 Amplitude 시크릿 |
| 분석 지표가 계속 사용 불가 | `admin_analytics_fetch_failed`의 `reason`과 `endpoint` | `no_credentials`면 시크릿 JSON과 태스크 정의 참조<br>`http_error`에 인증 실패 상태면 키 값<br>`rate_limited`면 쿨다운 뒤 자동 재호출이므로 대기<br>`budget_exceeded`면 같은 5분에 갱신한 엔드포인트가 많은 것이므로 대기하고, 한 엔드포인트만 반복되면 그 엔드포인트의 조회 구성과 기간 상한 재검토 |
| 설치 지표가 계속 사용 불가 | `admin_play_stats_fetch_failed`의 `reason`과 `status` | `no_credentials`면 운영 시크릿 JSON과 태스크 정의 참조<br>`http_error`에 권한 거부 상태면 서비스 계정의 버킷 읽기 권한<br>`http_error`에 상태가 없으면 키의 base64와 JSON 형식, 그다음 저장소 연결<br>`no_reports`면 Play Console의 보고서 생성 여부와 패키지 이름<br>`parse_error`면 보고서 형식 변경 |
| 인프라 지표가 계속 사용 불가 | `admin_infra_metrics_fetch_failed`의 `reason`, `service`, `error_code` | `not_configured`면 운영 태스크 정의의 인프라 지표 환경 변수<br>`access_denied`면 서버 태스크 역할의 정책과 `service`의 권한<br>`throttled`면 60초 뒤 다시 시도<br>`incomplete`면 `error_code`를 보고 60초 뒤 다시 시도하며 `Forbidden`이면 태스크 역할 정책<br>`timeout`이나 `aws_error`면 NAT 경로와 AWS 상태 |
| 인프라 지표의 한 묶음만 비어 있음 | 응답에서 `null`인 묶음 | 그 묶음의 환경 변수, OpenSearch는 계정 ID까지 |
