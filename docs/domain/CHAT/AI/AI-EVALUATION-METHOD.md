# AI 평가 방법

채팅 AI의 성능, 시간과 비용을 평가하는 데이터와 채점 방법을 정한다.

<br>

### 채팅 응답 생성

평가 데이터와 채점 장치는 `manyak-ai/evaluation/`에 있다. ([채팅 응답 생성](AI-EVALUATION-IMPLEMENTATION.md#채팅-응답-생성))

<br>

**1. 평가 범위**

| 항목 | 내용 |
|---|---|
| 평가 대상 | 고정한 프롬프트 버전에서 configuration(모델, 추론 강도)의 출력 |
| 평가 단위 | 채팅 1개의 마지막 AI 답변 1개 |
| 생성 입력 | 1~N−1턴 대화<br>N번째 사용자 입력<br>응답 직전의 생성 설정 |
| 실행 경로 | 기준 AI 레포의 프롬프트 조립, 모델 호출과 출력 파서를 그대로 사용<br>선택지와 이미지 호출 제외 |
| 생성 설정 | 프롬프트 버전, 모델과 추론 강도는 6-3-1의 configuration을 따름 |
| 채점 대상 | 생성한 답변을 붙인 N턴 대화 전체 |

<br>

**2. 데이터셋 샘플링**

| 제외 조건 |
|---|
| 일반 제작 스토리의 채팅 |
| 삭제된 채팅이나 스토리 |
| 제외 요청이 있는 채팅 |
| 1~2턴 채팅 |
| 평가 모델 개발에 쓴 채팅 |
| 개발자 채팅 |
| 엔딩에 도달한 채팅 |
| 스토리 태그에 성인·가학 태그가 있는 채팅 |
| 생성 입력이 남아 있지 않거나 손상된 레거시 채팅(보존 기한이 지난 채팅 포함) |
| 안전성 문제가 있는 채팅 |
| 서비스 취지에서 벗어난 입력(탈옥, 현실 정치 등)이 있는 채팅 |
| 마지막 사용자 입력이 대화를 끝내는 채팅 |

<br>

**3. 평가 데이터**

| 항목 | train | test |
|---|---|---|
| 용도 | 프롬프트를 고칠 때 사례 확인 | grid search와 configuration 비교의 점수 |
| 위치 | `evaluation/datasets/train/` | `evaluation/datasets/test/` |
| 규모 | test에 넣지 않은 운영 수집본<br>계속 추가 | 62개 |
| 사례 열람 | 허용 | 점수와 집계만 확인<br>사례 원문은 보지 않음 |
| 변경 | 추가 가능 | 고정<br>입력 해시로 변경 여부 검사<br>새로 뽑으면 새 버전으로 만들고 이전 버전 결과와 비교하지 않음 |

<details>
<summary><b>test 데이터셋 분포</b></summary>

<table>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "대화 길이 (%)"
    x-axis ["3~5턴", "6~19턴", "20턴 이상"]
    y-axis 0 --> 100
    bar [48, 29, 23]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 212, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "유저 (%)"
    x-axis ["게스트", "회원"]
    y-axis 0 --> 100
    bar [47, 53]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 212, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "스토리 종류 (%)"
    x-axis ["오리지널", "간편 제작"]
    y-axis 0 --> 100
    bar [37, 63]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 324, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "마지막 입력 길이 (%)"
    x-axis ["1~20자", "21~50자", "51~100자", "101자+"]
    y-axis 0 --> 100
    bar [11, 21, 56, 11]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "간편 제작 비율 · 대화 길이 (%)"
    x-axis ["3~5턴", "6~19턴", "20턴 이상"]
    y-axis 0 --> 100
    bar [67, 44, 79]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 180, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "장르 · 20턴 이상 (%)"
    x-axis ["로맨스", "탈출물", "로맨스 판타지", "학원", "기타"]
    y-axis 0 --> 100
    bar [21, 21, 14, 7, 36]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 228, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "대표 장르 (%)"
    x-axis ["로맨스", "탈출물", "현대 판타지", "로맨스 판타지", "군대 로맨스", "학원", "기타"]
    y-axis 0 --> 100
    bar [31, 26, 8, 6, 6, 3, 19]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 204, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "스토리 묶음 (%)"
    x-axis ["간편 제작", "0호선", "그건 반칙이지 말입니다", "나만 기억하는 멸망", "백룸: 미귀환", "대공님, 계약 위반입니다"]
    y-axis 0 --> 100
    bar [63, 24, 6, 3, 2, 2]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 방식 (%)"
    x-axis ["선택지", "직접 입력", "선택지 수정"]
    y-axis 0 --> 100
    bar [58, 40, 2]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 방식 · 3~5턴 (%)"
    x-axis ["선택지", "직접 입력", "선택지 수정"]
    y-axis 0 --> 100
    bar [33, 63, 3]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 212, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 방식 · 6~19턴 (%)"
    x-axis ["선택지", "직접 입력"]
    y-axis 0 --> 100
    bar [94, 6]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 212, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 방식 · 20턴 이상 (%)"
    x-axis ["선택지", "직접 입력"]
    y-axis 0 --> 100
    bar [64, 36]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 324, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 길이 · 직접 입력 (%)"
    x-axis ["1~20자", "21~50자", "51~100자", "101자+"]
    y-axis 0 --> 100
    bar [28, 28, 36, 8]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 268, "height": 240, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta
    title "입력 길이 · 선택지 (%)"
    x-axis ["21~50자", "51~100자", "101자+"]
    y-axis 0 --> 100
    bar [17, 69, 14]
```

</td>
</tr>
<tr>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 204, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "장르 · 3~5턴 (%)"
    x-axis ["로맨스", "탈출물", "현대 판타지", "로맨스 판타지", "군대 로맨스", "기타"]
    y-axis 0 --> 100
    bar [37, 13, 13, 7, 13, 17]
```

</td>
<td>

```mermaid
%%{init: {"theme": "base", "xyChart": {"width": 400, "height": 180, "titleFontSize": 13, "xAxis": {"labelFontSize": 12}, "yAxis": {"labelFontSize": 11, "showTitle": false}}, "themeVariables": {"xyChart": {"backgroundColor": "#FFFFFF", "titleColor": "#253C2C", "xAxisLabelColor": "#253C2C", "xAxisLineColor": "#9BA99E", "xAxisTickColor": "#9BA99E", "yAxisLabelColor": "#253C2C", "yAxisLineColor": "#9BA99E", "yAxisTickColor": "#9BA99E", "plotColorPalette": "#1F3A5F"}}}}%%
xychart-beta horizontal
    title "장르 · 6~19턴 (%)"
    x-axis ["로맨스", "탈출물", "현대 판타지", "학원", "기타"]
    y-axis 0 --> 100
    bar [28, 50, 6, 6, 11]
```

</td>
</tr>
</table>

</details>

<br>

**4. 평가 모델**

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    P["<b>평가 모델 프롬프트</b><br/>평가 기준과 채점 지시"] --- J["<b>평가 모델</b><br/>대화 한 개씩 독립 채점"]
    D["<b>채팅 한 개</b><br/>sample_id, prologue, turns<br/>생성한 마지막 답변을 포함한 N턴 대화"] --- J
    J --> O["<b>JSON 채점 결과 한 개</b><br/>results 배열<br/>sample_id: 사례 식별자<br/>score: 0~100점 정수<br/>reason: 채점 이유<br/>evidence: 근거 턴 번호 목록"]
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    class P,D,O data
    class J task
```

| 항목 | 내용 |
|---|---|
| 주 평가 모델 | `gpt-6-astra`, 추론 강도 `high`<br>답변당 독립 채점 3회 |
| 교차 확인 모델 | `claude-fable-5-1`, 추론 강도 `medium`<br>답변당 독립 채점 2회로 Astra와 순위 비교<br>평가 모델별 결과는 별도 집계 |
| 생성 모델과의 관계 | 생성 모델과 다른 모델 사용 |
| 평가 모델 프롬프트 | Astra용 v0.3 고정본<br>`evaluation/judge-prompt/astra-prompt.md`에 보관<br>Fable은 `evaluation/judge-prompt/fable-prompt.md` 사용 |
| 채점 질문 | 마지막 정상 AI 응답까지 읽은 사용자가 다음 행동이나 대사를 이어가고 싶은 정도<br>완결된 이야기는 처음부터 결말까지의 재미와 여운 |
| 채점 입력 | `sample_id`, `prologue`, `turns`<br>태그와 인물 정보는 전달하지 않음 |
| 출력 | JSON의 `results` 배열에 채점 결과 1개<br>`sample_id`, `score`(0~100점 정수), `reason`(채점 이유), `evidence`(근거 턴 번호 목록) |
| 호출 방식 | 대화 1개당 별도 호출<br>다른 답변과 점수는 전달하지 않음 |
| 개선 방식 | 사람 선호와의 일치율을 기준으로 평가 모델 프롬프트 개선 |
| 사람 평가와의 비교 | 사람이 두 채팅 중 고른 쪽에 더 높은 점수를 준 쌍의 비율<br>v0.2는 72쌍에서 6회 평균 70.4% (2026-09-07, `gpt-5.6-sol`, 추론 강도 `medium`) |

<br>

**평가 모델 개선과 검증**

사람이 더 이어가고 싶다고 고른 채팅에 높은 점수를 주도록 평가 모델 프롬프트를 개선한다. 모델 가중치는 학습하지 않는다.

```mermaid
%%{init: {"flowchart": {"curve": "basis", "htmlLabels": true, "nodeSpacing": 24, "rankSpacing": 48}}}%%
flowchart LR
    A["<b>사람 평가 데이터</b><br/>채팅 쌍과 선호 선택"] --- C["<b>평가 모델 실행</b><br/>채팅별 독립 채점"]
    B["<b>평가 모델 프롬프트</b>"] --- C
    C --> D["<b>일치율 비교</b><br/>사람 선호와 일치한 비율"]
    D -->|같거나 기존보다 낮음| E["<b>프롬프트 개선</b><br/>불일치 원인을 반영해 수정"]
    E --> C
    D -->|기존보다 높음| F["<b>개선한 프롬프트 유지</b>"]
    classDef data fill:#E8F2E8,stroke:#527A59,color:#182D1D
    classDef task fill:#F5D9C9,stroke:#B97450,color:#452B1D
    classDef check fill:#F4F6F4,stroke:#9BA99E,color:#253C2C
    class A,B,F data
    class C,E task
    class D check
```

| 항목 | 기준 |
| --- | --- |
| 사람 평가 | 채팅 두 편 중 더 이어가고 싶은 쪽을 선택 |
| 모델 입력 | 채팅 한 편씩 독립 채점<br>상대 채팅, 사람 선택과 선택 이유는 채점 모델에 전달하지 않음 |
| 일치율 | 사람이 고른 쪽에 더 높은 점수를 준 쌍 수 ÷ 전체 쌍 수<br>동점은 불일치 |
| 수정 범위 | 모델과 추론 강도를 고정하고 평가 모델 프롬프트 한 곳만 수정<br>특정 표본의 인물이나 장면을 외우는 문구 제외 |
| 비교 조건 | 입력, 사람 선택과 반복 횟수 고정<br>조건이 바뀌면 기준부터 다시 측정 |
| 채택 조건 | 후보 3회와 재평가 3회 모두 기준 평균 이상이며 6회 평균은 기준 평균 초과 |
| 기존 정답 유지 | 기준에서 3회 모두 맞힌 쌍을 후보의 첫 평가 또는 재평가에서 3회 모두 틀리면 탈락<br>6회 평균이 기준보다 10%p 이상 높으면 이 조건만 예외로 하고 해당 쌍 기록 |
| 재평가 예외 | 재평가 3회 중 한 회만 기준 미달이고 차이가 한 쌍 이내이면 추가 3회 평가를 한 번만 허용<br>추가 3회는 모두 기준 이상 |
| 최종 판단 | 사람이 쌍별 결과와 판단 근거 확인<br>일치율이 올라도 의도와 다른 근거로 맞혔으면 폐기 |
| 결과 기록 | 변경 이유, 프롬프트 버전, 평가 모델과 강도, 입력 해시, 반복별 일치율, 채택 여부 |

<br>

**5. 평가 지표**

채팅 응답 실패율과 본문 재생성률은 오프라인 평가에서 계산하지 않고 운영 기록으로 확인한다. ([운영 요구사항](OPERATION-REQUIREMENTS.md), [관측](OBSERVABILITY.md))

| 지표 | 계산 방법 | 2-2 목표 |
|---|---|---|
| 채팅 재미 점수 | 평가 모델별 반복 채점의 평균을 답변마다 구한 뒤 데이터셋 전체 입력의 평균 | 없음 |
| 턴당 본문 생성 비용 | 입력별 최초 호출과 재생성의 API 비용 `cost_usd`를 합산한 뒤 평균<br>캐시 미스 단가 적용, 입력 토큰 수가 모델별 기준을 초과하면 해당 요청 전체의 입력과 출력에 각각 할증 적용<br>호출 비용이 하나라도 미측정이면 해당 입력의 총비용은 평균에서 빼고 개수를 함께 기록 | 목표 $0.01 이하 <br> 상한 $0.03 |
| 본문 생성 시간 | 입력별 최초 호출과 재생성의 소요 시간을 합산한 값의 p95<br>동시 호출을 기다리는 대기 시간 제외 | 기록만 함<br>채팅 응답 완료 시간은 운영 기록으로 판정 |
| 첫 토큰 시간(TTFT) <br> 평균, short, mid, long | short, mid, long 각 1건의 첫 토큰 시간(초)<br>평균은 선택한 3건의 산술평균 | 기록만 함 |

<br>

**TTFT 측정 기준**

| 항목 | 기준 |
|---|---|
| 입력 선정 | configuration별 원래 생성 입력의 토큰 수 오름차순으로 최소, 중앙, 최대 각 1건<br>개수가 짝수이면 중앙 두 건 중 뒤의 입력 선택, 토큰 수가 같으면 입력 ID 순 |
| 직접 측정 | 같은 configuration과 입력으로 길이별 1회 재생성<br>호출 시작부터 공백을 제외한 첫 본문 도착까지 측정 |
| 공급자 로그 | Qwen과 Kimi는 공급자가 기록한 첫 토큰 시간 사용<br>첫 본문 도착 기준과 구분해 출처 기록 |
| 복구 범위 예외 | grid-v2-r1의 Kimi low는 복구된 18건에서 최소, 중앙, 최대 선정 |
| 기록 | 평균, short, mid, long 순서로 표시<br>선정한 입력 ID, 입력 토큰 수, 호출 경로와 측정 출처 보관 |

<br>

**6. 반복과 실패 처리**

| 항목 | 처리 |
|---|---|
| 채점 변동 | 같은 답변을 Astra 3회, Fable 2회 채점해 점수의 변동만 확인<br>답변을 다시 생성했을 때의 편차는 측정하지 않음 |
| 생성 오류, 빈 본문, 잘림 종료 | 최초 호출 이후 같은 입력으로 최대 3회 재생성해 채점<br>configuration별 재생성 횟수 기록<br>재생성 후에도 같으면 해당 입력은 실패로 처리 |
| 채점 오류, 무효 출력 | 새 세션에서 1회 재시도 |
| 실패 | 재시도 후에도 생성이나 채점이 실패하면 해당 configuration의 평가 전체를 실패로 처리<br>성공한 입력만 모아 평균을 내지 않음 |
| 비교 조건 | 데이터셋, 평가 모델 프롬프트, 채점 입력과 반복 횟수가 같은 결과끼리만 비교 |
