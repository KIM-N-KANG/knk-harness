# 6. 배포

이 문서는 ADMIN 도메인이 포함된 서버의 배포 단위와 의존 대상, 배포 경로, 이 도메인이 읽는 환경 변수와 시크릿, 배포 조건, 설정 변경, 적용과 복구 절차를 정한다.

서버 전체 배포 절차 중 ADMIN 도메인과 관련된 항목만 다룬다.

토큰 수명은 오류 처리에 있으며 관측 스택과 조회 도구는 관측에 있다. ([5-3-5 재시도와 시간 한도](5-3-ERROR-HANDLING.md#5-3-5-재시도와-시간-한도)와 [5-4-1 관측 스택](5-4-OBSERVABILITY.md#5-4-1-관측-스택))

<br>

### 6-1 배포 단위와 의존성

배포 단위는 서버 컨테이너 하나다. ADMIN만 따로 배포하지 않는다. 관리자 페이지는 별도 저장소에서 Vercel에 배포하며 이 문서의 범위 밖이다. 이 도메인이 기동과 요청 처리에 쓰는 의존 대상은 다음과 같다.

| 의존 대상 | 내용 | ADMIN 도메인이 쓰는 것 |
|---|---|---|
| PostgreSQL | 기동 시 마이그레이션 적용 | 관리자 역할과 감사 로그 테이블 |
| Google | 공개 키 집합 | 계정 도메인의 검증기 경유 |
| Secrets Manager | Terraform이 태스크 정의에 참조 주입 | 대칭키, Google client ID, Amplitude API 키와 시크릿 키 |
| Amplitude | Dashboard REST API | 분석 지표 |
| Google Cloud Storage | Play Console 일괄 보고서 버킷 | 설치 지표 |
| Data Prepper | 트레이스를 받아 OpenSearch에 적재 | 트레이스 전송 |

<br>

| 의존 대상 | 연결과 설정 실패 시 동작 |
|---|---|
| 대칭키 | 비어 있거나 32바이트 미만이면 기동 실패 |
| Google client ID | 비어 있으면 관리자 로그인 전부 거절<br>기동은 정상 |
| PostgreSQL | 연결할 수 없으면 기동 실패 |
| 관리자 역할 행 없음 | 기동은 정상<br>아무도 로그인할 수 없음 |
| 팀 계정 제외 목록 | 정수가 아닌 값이 있으면 기동 실패<br>빈 값이면 제외 없이 집계 |
| Amplitude 키 | 둘 중 하나라도 비면 분석 지표만 사용 불가<br>기동은 정상 |
| Amplitude | 연결할 수 없으면 분석 지표만 사용 불가<br>캐시가 있으면 캐시로 응답 |
| Play 서비스 계정 키 | 비면 설치 지표만 사용 불가<br>기동은 정상<br>base64가 아니거나 JSON이 아니면 기동 실패 |
| Google Cloud Storage | 연결할 수 없으면 설치 지표만 사용 불가<br>캐시가 있으면 캐시로 응답 |
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
| `MANYAK_ADMIN_DASHBOARD_EXCLUDED_USER_IDS` | `1,2,3,4,5,10,11,206,207` | 주입 없음 | 콤마 구분 회원 내부 ID<br>대시보드 요약과 차트에서만 제외하며 기본값은 운영 Terraform `grafana/dashboards/service-stats.json`의 소비 활동 제외 목록과 같음<br>제작 세션 차트는 이 목록에서 `MANYAK_OFFICIAL_USER_PUBLIC_ID`의 회원을 뺀 나머지를 제외 |

관리자 토큰 수명과 대상 클레임 값, 분석 지표의 캐시 시간 10분, 호출 시간 한도 5초, 실패 쿨다운 60초, 캠페인 분석의 캐시 시간 10분, 조회 시간 한도 10초, 비용 예산 5분 1,000, 유입 소스 목록(`ig`, `th`와 `threads`, `dc`), 설치 지표의 캐시 시간 1시간, 호출 시간 한도 10초, 실패 쿨다운 60초, 보고서 버킷 이름 `pubsite_prod_7346202752431827582`와 패키지 이름 `app.manyak`은 설정 파일의 고정값이다.

<br>

**2. 분석 지표와 설치 지표**

| 이름 | 기본값 | 주입 출처 | 비고 |
|---|---|---|---|
| `MANYAK_AMPLITUDE_API_KEY` | 빈 값 | 개발과 운영 Secrets Manager `manyak/{env}/app` | 공통 분석 발행기와 같은 키<br>운영 프로젝트 하나뿐이라 개발 서버도 같은 값 |
| `MANYAK_AMPLITUDE_SECRET_KEY` | 빈 값 | 개발과 운영 Secrets Manager `manyak/{env}/app` | Dashboard REST API 기본 인증<br>태스크 정의에 새 시크릿 참조를 추가해야 주입됨 |
| `MANYAK_AMPLITUDE_TEAM_COHORT_ID` | 빈 값 | 개발과 운영 태스크 정의에 같은 값을 직접 기록 | 팀 계정 코호트 ID<br>사용자 수 조회의 세그먼트 `userdata_cohort` 제외 조건에 사용<br>비어 있으면 제외 없이 조회 |
| `MANYAK_AMPLITUDE_DASHBOARD_BASE_URL` | `https://amplitude.com` | 주입 없음 | US 데이터 센터 |
| `MANYAK_ADMIN_CAMPAIGN_DEFAULT` | `KR_META_WEB_ACTIVATION_COLD_202610` | 개발과 운영 태스크 정의에 직접 기록 | 캠페인 분석의 기본 캠페인 값<br>비어 있으면 쿼리 `campaign` 필수 |
| `MANYAK_ADMIN_CAMPAIGN_STORY_ID` | 빈 값 | 개발과 운영 태스크 정의에 직접 기록 | 상세 진입 퍼널의 기본 대상 스토리 공개 식별자<br>비어 있으면 그 퍼널은 `null` |
| `MANYAK_PLAY_STATS_SA_KEY_BASE64` | 빈 값 | 운영 Secrets Manager `manyak/prod/app`만<br>개발은 주입 없음 | Play 보고서 읽기 전용 서비스 계정 키 JSON의 base64<br>태스크 정의에 새 시크릿 참조를 추가해야 주입됨<br>개발 서버는 설치 지표가 사용 불가 |

<br>

**3. 다른 도메인이 관리하는 값**

| 이름 | ADMIN이 쓰는 곳 |
|---|---|
| `MANYAK_AUTH_JWT_SECRET` | 관리자 토큰 서명과 검증<br>바꾸면 발급된 관리자 토큰이 전부 무효 |
| `MANYAK_GOOGLE_CLIENT_IDS` | 관리자 로그인의 신원 증명 대상 검증<br>관리자 페이지의 Google client ID가 목록에 있어야 함 |
| `MANYAK_OFFICIAL_USER_PUBLIC_ID` | 스토리 목록의 `original` 범위 판정<br>제작 세션 차트의 제외 목록 보정<br>비어 있으면 모든 스토리가 `user` |

<br>

**4. 관측**

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
| 팀 계정 코호트 | 분석 도구에 팀 계정 코호트가 있고 ID가 설정값과 같음 | 수동 확인 |
| 와이어 계약 변경 | 관리자 API 응답이 바뀌면 관리자 페이지와 함께 배포 | 수동 검토 |
| 관리자 경로 추가 | 회귀 테스트가 새 경로를 자동 수집하는지 테스트 결과에서 확인 | CI 자동 |
| 마이그레이션 | 기동 시 실행하므로 새 마이그레이션은 해당 코드보다 먼저 적용<br>재실행해도 같은 결과 | 기동 시 자동 적용<br>마이그레이션 경로 변경 PR은 `tbls lint`와 `dbdoc/` 비교를 CI에서 자동 실행 |
| 코드 테스트 | 전체 테스트 통과 | CI 자동 |
| 컨테이너 기동 | 컨테이너 헬스체크와 `/actuator/health` `UP` | CI 자동 |

<br>

### 6-5 설정 변경

| 변경 대상 | 변경 위치와 적용 | 확인 조건 |
|---|---|---|
| 관리자 역할 부여와 회수 | 운영 DB에서 역할 행 추가 또는 삭제<br>다음 요청부터 반영<br>재배포 없음 | 회수된 계정의 관리자 요청이 권한 없음으로 거절됨<br>감사 로그 조회 응답의 `admin.isAdmin` |
| 관리자 토큰 수명 | 설정 파일 변경 후 재빌드 | 로그인 응답의 `expiresIn` |
| 팀 계정 제외 목록 | 환경 변수 변경 후 새 태스크 시작 | 대시보드 요약의 회원 수 변화 |
| 팀 계정 코호트 구성원 | 분석 도구에서 코호트 편집<br>다음 캐시 갱신부터 반영 | 분석 지표의 활성 사용자 수 변화 |
| 기본 캠페인과 대상 스토리 | 환경 변수 변경 후 새 태스크 시작 | 캠페인 분석 응답의 `campaign`과 `storyId` |
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

<br>

### 6-7 배포 후 확인

| 확인 항목 | 자료 | 기준 |
|---|---|---|
| 기동 | 해당 배포 ID의 태스크 상태, 헬스체크 `/actuator/health`, 스모크 테스트 | 의도한 이미지로 기동<br>`UP` |
| 관리자 로그인 | 로그 `admin_login_succeeded`<br>`admin_login_rejected` | 역할 있는 계정이 로그인됨 |
| 권한 판정 | 로그 `admin_access_denied` | 급증하지 않음 |
| 대시보드 | 대시보드 요약과 차트 응답 | 모든 지표가 채워지고 분포 차트가 8개 |
| 목록 | 스토리, 채팅, 회원, 결제 목록 첫 페이지 | 성공 응답과 `totalElements` |
| 분석 지표 | 기본 범위의 분석 지표 응답 | 성공 응답과 `daily` 30개<br>사용 불가면 `admin_analytics_fetch_failed`의 `reason` |
| 캠페인 분석 | 기본값의 추이와 퍼널 응답 | 성공 응답과 `campaign`이 설정값<br>`budget_exceeded`가 반복되면 호출 묶음 재검토 |
| 설치 지표 | 설치 지표 응답 | 성공 응답과 `asOf`가 오늘에서 며칠 안<br>사용 불가면 `admin_play_stats_fetch_failed`의 `reason` |
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
| 분석 지표가 계속 사용 불가 | `admin_analytics_fetch_failed`의 `reason` | `no_credentials`면 시크릿 JSON과 태스크 정의 참조<br>`http_error`에 인증 실패 상태면 키 값<br>`rate_limited`면 쿨다운 뒤 자동 재호출이므로 대기 |
| 설치 지표가 계속 사용 불가 | `admin_play_stats_fetch_failed`의 `reason`과 객체 이름 | `no_credentials`면 운영 시크릿 JSON과 태스크 정의 참조<br>`http_error`에 권한 거부 상태면 서비스 계정의 버킷 읽기 권한<br>`not_found`면 Play Console의 보고서 생성 여부와 패키지 이름<br>`parse_error`면 보고서 형식 변경 |
