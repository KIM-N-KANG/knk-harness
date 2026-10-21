# 6-5 AI 평가 구현

### 6-5-1 공통 실행 구조

구현 위치는 `manyak-ai/evaluation/storyline/`이다.

| 항목 | 구현 |
|---|---|
| 진입점 | `train.py`에서 실행 모드, 호출 한도와 configuration 설정 <br> `eval.py`에서 데이터 검사, 생성, 채점과 저장 실행 |
| 호출 클라이언트 | `evaluation/common/judge.py`로 평가 모델 호출 <br> `evaluation/common/request_audit.py`로 공급자 요청 기록 |
| 실행 제어 | 기본 실행과 `--plan`은 모델 호출 없이 계획 확인 <br> `--check-data`는 데이터 검사, `--confirm-live`는 실제 호출 |
| 실행 식별 | `--run-id`로 실행 구분 <br> 파일 잠금으로 동일 실행의 중복 실행 차단 |
| 저장과 복구 | 결과와 백업을 저장하고 유효한 최신 저장본으로 복구 <br> 복구 불가 또는 같은 저장 순번의 내용 충돌 시 새 호출 없이 중단 |
| 재개 | 같은 실행 ID로 성공 결과를 재사용하고 미완료 대상만 실행 <br> 입력, 프롬프트와 평가 조건이 달라지면 재개 거부 |
| 평가 기준 | 호출 구성, 집계와 채택 기준 적용. ([6-4-1 스토리라인 생성](6-4-AI-EVALUATION-METHOD.md#6-4-1-스토리라인-생성)) |

<br>

### 6-5-2 스토리라인 평가 모델 개선

| 항목 | 구현 |
|---|---|
| 자동 실행 | `--mode judge --auto`로 기준선 준비, 후보 생성과 평가 반복 <br> `--max-cycles`, `--total-calls`로 실행 한도 지정 |
| 개별 실행 | `--improve`로 후보 생성 <br> `--mode judge`로 기준선과 저장된 후보 평가 |
| 기준선 | `eval-prompt/`의 최신 정식 버전 사용 <br> `runs/judge/baseline-<버전>/`의 완료된 채점 재사용 |
| 후보 생성 | 오케스트레이션 AI에 train 피드백과 `program.md`의 개선 지침 전달 <br> 응답과 변경 이유 저장 후 `<criteria>` 밖의 변경 검사 |
| 실험 저장 | 후보 내용의 해시로 실험 ID 생성 <br> `runs/judge/<실험ID>/`에 후보, train/test 채점과 판정 저장 |
| 진행 복구 | `runs/judge/loops/<루프ID>/`에 사이클, 단계와 호출 사용량 저장 <br> 재개 시 성공한 후보 생성과 채점을 반복하지 않고 누적 호출 한도 유지 |
| 버전 저장 | 채택한 후보를 `eval-prompt/`의 새 버전으로 저장하고 종료 <br> 기존 버전 보존, 채택 후보의 측정값을 새 버전 기준선으로 저장 |

<br>

### 6-5-3 스토리라인 그리드 서치

| 항목 | 구현 |
|---|---|
| 실행 설정 | `--mode grid`로 실행 <br> `train.py`의 `CONFIGURATIONS`에 모델, 추론 강도와 생성 프롬프트 경로 지정 |
| 생성 입력 | `--inputs`로 입력 폴더 지정 <br> 생략 시 `datasets/generation/<split>/` 사용 |
| 생성 | configuration과 입력을 순차 순회하며 운영의 `generate_storylines` 호출 <br> 운영 입력 검증, 프롬프트 조립과 출력 복구 코드 재사용 |
| 채점 | 생성에 성공한 후보를 채점하고 완료된 회차 재사용 <br> 현재 구현은 후보 세트 1개씩 순차 채점하며, 6-4의 호출당 2세트와 동시 호출 설정은 미반영 |
| 호출 한도 | `--max-calls`로 실행당 상한 지정 <br> 생성, 생성 복구와 채점 호출 포함 |
| 결과 저장 | `runs/grid/<실행ID>/`에 입력, 프롬프트, 실행 설정과 `grid.json` 저장 <br> `summary.json`에 configuration별 점수, 생성 시간과 추정 비용 집계 <br> `results.tsv`에 실행 상태 기록 |
| 백업 | `runs/grid/.backups/<실행ID>/`에 실행 기록과 결과 사본 저장 |
