# AI 평가 구현

채팅 AI의 평가 방법을 실행하는 프로그램의 구조와 동작을 정한다.

<br>

### 채팅 응답 생성

6-4-1의 평가 방법을 6-3-1의 configuration별로 실행하고 결과를 기록한다. 평가 프로그램은 운영 코드를 그대로 호출하며, 진입점만 평가 CLI로 분리한다. ([채팅 응답 생성](AI-ALIGNMENT.md#채팅-응답-생성), [채팅 응답 생성](AI-EVALUATION-METHOD.md#채팅-응답-생성))

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    BE["<b>백엔드 요청</b>"] --> RT["<b>API 라우터</b>"]
    CLI["<b>평가 CLI</b><br/>실행 설정, test 또는 train"] --> CS["<b>configuration별 실행</b>"]
    RT --> SH
    CS --> SH
    subgraph SH["공유 운영 코드 src"]
        AS["<b>메시지 조립</b>"] --> LL["<b>모델 호출</b>"] --> PA["<b>본문 정리</b>"]
    end
    SH --> OUT["<b>응답 전달</b><br/>배포함"]
    SH --> RG["<b>재생성 최대 3회</b><br/>오류, 빈 본문, 잘림 시"]
    RG --> JD["<b>평가 모델별 채점</b><br/>Astra 3회, Fable 2회"]
    JD --> RN["<b>runs 저장</b><br/>배포하지 않음"]
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    classDef code fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
    class OUT,RN data
    class LL,JD task
    class BE,RT,CLI,CS,AS,PA,RG code
```

<br>

**1. 위치와 배포**

| 항목 | 내용 |
|---|---|
| 평가 코드 | `manyak-ai/evaluation/` |
| 배포 | 배포 이미지에 포함하지 않음<br>Dockerfile은 `src`와 `prompt`만 복사 |
| 평가 데이터 | `evaluation/datasets/train/`, `evaluation/datasets/test/`<br>Git 제외 |
| 실행 결과 | `evaluation/runs/`<br>Git 제외 |
| 평가 모델 프롬프트 | `evaluation/` 안에 고정본으로 보관<br>버전과 해시를 결과에 기록 |

<br>

**2. CLI 명령**

| 명령 | 동작 | 모델 호출 |
|---|---|---|
| `.venv/bin/python evaluation/train.py --plan` | configuration 목록과 예상 생성 비용 출력<br>채점 호출 수는 Astra 3회 기준으로만 표시, 전체 실행 시 Fable 2회분 추가 | 없음 |
| `.venv/bin/python evaluation/train.py` | 입력과 생성 설정 검사 | 없음 |
| `.venv/bin/python evaluation/train.py --confirm-live` | 응답 생성 | 있음 |
| `bash evaluation/run.sh --confirm-live` | 생성 후 Astra와 Fable 채점을 병렬 실행하고 평가 모델별 보고서 생성<br>승인 인자가 없으면 오류로 종료 | 있음 |
| `.venv/bin/python evaluation/eval.py --run <실행 ID> --judge <astra 또는 fable> --confirm-live` | 저장한 응답 채점 | 있음 |
| `.venv/bin/python evaluation/report.py --run <실행 ID> --judge <astra 또는 fable>` | 저장한 집계로 HTML 보고서 생성 | 없음 |

<br>

**3. 실행 설정**

| 항목 | 내용 |
|---|---|
| 설정 위치 | 생성은 `evaluation/train.py` 상단 상수, 채점은 `evaluation/eval.py`의 평가 모델 설정 |
| 실행 ID | 생성 설정의 실행 ID 사용<br>채점과 보고서는 `--run`으로 선택 |
| 모델 | 6-3-1의 기반 모델 중 실행할 목록 |
| 추론 강도 | `none`, `low`, `medium`, `high` 중 실행할 목록 |
| 프롬프트 | 실행할 프롬프트 버전 목록 |
| 데이터셋 | train 또는 test 데이터셋 이름 |
| configuration 생성 | 모델, 추론 강도와 프롬프트 버전의 모든 configuration<br>모델이 지원하지 않는 추론 강도는 제외 |

<br>

**4. 운영 코드 공유**

| 단계 | 호출할 운영 코드 |
|---|---|
| 메시지 조립 | `src/services/chat_assembler.py` |
| 본문 생성과 화자 정리 | `src/services/chat_llm.py` |
| 모델 호출 | `src/services/llm/` |

- 평가용으로 운영 코드를 복사하거나 다시 만들지 않는다.
- 모델과 추론 강도는 호출 설정 값으로만 바꾼다.
- 프롬프트 버전은 `prompt/`에서 사용할 템플릿 경로를 선택해 적용한다.
- 선택지와 이미지 호출은 실행하지 않는다.

<br>

**5. 실행 관리**

| 항목 | 처리 |
|---|---|
| 한도 | 생성 설정에 동시 호출 수, 전체 호출 수, 전체 시간과 호출당 제한 시간 지정<br>전체 호출 수나 시간 한도에 도달하면 추가 생성을 중단하고 완료된 응답까지 채점 |
| 재개 | 같은 실행 ID로 다시 실행하면 완료된 생성과 채점 결과를 재사용 |
| 설정 검사 | 모델, 추론 강도, 프롬프트 목록, configuration 목록, 데이터셋 이름과 해시, 생성 프롬프트 해시를 비교해 다르면 재개 거부<br>재시도 횟수, 호출 수, 시간과 동시 호출 한도의 변경은 검사하지 않음 |
| 재생성 | 생성 오류, 빈 본문이나 잘림 종료면 최초 호출 이후 최대 3회 재생성 |

<br>

**6. 채점**

| 항목 | 내용 |
|---|---|
| 채점 설정 | 6-4-1의 평가 모델, 평가 모델 프롬프트와 반복 횟수 사용 |
| 호출 경로 | Astra는 Codex CLI, Fable은 Claude CLI 사용<br>채점 1회마다 별도 세션으로 호출 |
| 채점 입력 | 생성한 답변을 붙인 N턴 대화의 `sample_id`, `prologue`, `turns` |
| 출력 검사 | `results` 배열의 결과 1개를 검사<br>입력과 같은 `sample_id`, 0~100 정수 `score`, 비어 있지 않은 `reason`, 0 이상 정수 `turn_number`를 담은 `evidence` 목록 필수 |
| 채점 실패 | 오류나 무효 출력은 새 세션에서 1회 재시도 |
| 분리 | 생성과 채점을 별도 단계로 실행하고 실패를 각각 기록 |

<br>

**7. 기록**

| 항목 | 처리 |
|---|---|
| 저장 위치 | `evaluation/runs/<실행 ID>/<configuration ID>/` |
| 생성 결과 | 입력별 생성 답변, 요청과 응답 모델 이름, 추론 강도, 프롬프트 버전 |
| 채점 결과 | 평가 모델별 각 회차의 점수, 이유와 근거 턴 번호<br>Astra 3회, Fable 2회의 평균 |
| configuration 상태 | 6-4-1의 실패 기준에 따라 configuration별 평가 완료 또는 실패 상태 기록 ([채팅 응답 생성](AI-EVALUATION-METHOD.md#채팅-응답-생성)) |
| 호출 기록 | 실패한 최초 호출과 재생성을 포함해 호출별 시간과 비용을 각각 기록<br>입력별 전체 소요 시간과 합산 비용도 기록 |
| 요약 | configuration별 채팅 재미 점수, 턴당 본문 생성 비용, 본문 생성 시간 p95, 재생성 횟수와 실패 입력 수 |
| TTFT | 생성 시 호출별 첫 본문 도착 시간 저장<br>길이별 재측정과 공급자 로그 복구 결과는 별도 취합<br>평균, short, mid, long은 기본 TSV와 HTML 보고서에 자동 집계하지 않음 |
| 버전 | 실행 ID, `manyak-ai` 커밋, 데이터셋 이름과 입력 해시, 평가 모델 프롬프트 버전과 해시 |
