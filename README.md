# 달리기 자세 라벨링 툴 v0.4.5

## 1. 이게 뭔지

```text
영상 등록 → 사용자/측정 정보 입력 → MotionMetrix 값 직접 입력
→ Skeleton Overlay로 포인트/계산 기준 확인 → 육안 평가 입력
→ 세션 저장 → 3차 모델링용 CSV/JSON Export
```

2차의 목표는 Pose Estimation이나 STT/LLM, 위험도 산출, REST API를 완성하는 게 아니라 **3차 모델링에 쓸 정답 데이터셋을 만드는 구조**를 잡는 것입니다. 그 이상은 범위 밖이라고 보면 됩니다.

---

## 2. v0.4.5 변경 사항

### v0.4.2 핫픽스

일부 Windows/로컬 Python 환경에서 `mediapipe`는 깔려 있는데 `mediapipe.solutions`가 노출 안 되는 케이스가 있어서 Preview 생성이 죽는 문제가 있었습니다. `mp.solutions.pose`와 `mediapipe.python.solutions.pose` 두 경로를 다 시도하도록 고쳤고, 둘 다 못 찾으면 앱이 죽는 대신 Preview 화면에 재설치 안내 메시지만 띄우게 바꿨습니다. Preview 입력 방식 우선순위(저장 영상 프레임 기본, 카메라 스냅샷 보조, Live Stream 실험)도 앱/README에 명시했습니다.

### v0.4.1 핫픽스

샘플 세션 불러온 뒤 후면 입력 탭에서 터지던 Streamlit duplicate widget key 문제, 세션 저장 시 `session_id` 위젯 생성 이후 session_state를 건드려서 나던 예외 둘 다 수정했습니다. 촬영 Wizard/Overlay 쪽 MotionMetrix 입력 위젯은 기존 입력 탭과 키가 겹치지 않게 별도 임시 키를 쓰고, 저장 시점에만 동일 세션 필드로 합쳐지도록 정리했습니다. 패키징 전에 테스트하면서 생긴 임시 세션/Export 파일은 정리했고, 샘플 데이터는 `sample_data/`에만 남겨뒀습니다.

| 항목 | 내용 |
|---|---|
| 촬영 순서 Wizard | 후면 정지 → 후면 달리기 → 측면 정지 → 측면 달리기 순서대로 진행 |
| Skeleton Overlay Preview | 업로드 영상 프레임 또는 카메라 스냅샷에 MediaPipe Skeleton Overlay 표시 |
| 선택 포인트 강조 | 선택한 지표에 필요한 포인트만 강조, 전체 보기 토글 별도 제공 |
| 계산정보 동시 출력 | Forward Lean, 무릎각, Shank Angle, 골반선 기울기 등 현재 프레임 참고값 표시 |
| Live Camera Stream (실험) | 브라우저 카메라 스트림에 Overlay 표시. 안정적인 검수는 업로드 영상 Preview 쪽을 씁니다 |
| Preview 결과 저장/Export | Preview 이미지 + 계산정보 요약을 세션 저장과 Export에 포함 |
| v0.3 기능 | 샘플 세션, 검수 시나리오, MotionMetrix 입력 가이드, 필수값만 보기, 단위 정규화, 데이터 품질 리포트는 그대로 유지 |

---

## 3. 주요 기능

| 구분 | 기능 | 설명 |
|---|---|---|
| 세션 관리 | 생성/불러오기/수정 | 검사 1건 = 세션 1개 |
| 샘플 세션 | 사이드바에서 추가 | 처음 쓰는 사람이 입력/Export 구조부터 빠르게 파악 |
| 사용자 정보 | ID, 나이, 성별, 키, 체중, 속도, FPS | 모델 보정 변수로 쓸 기본 정보 |
| 영상 업로드 | 측면/후면 정지·달리기 | 세션 폴더에 저장, Export에 경로 포함 |
| 촬영 Wizard/Overlay | 순서별 Skeleton Preview | 고객 문서 순서대로 포인트/참고값 보면서 작업 |
| MotionMetrix 입력 | 생체역학 지표 직접 입력 | 3차 모델 정답값으로 사용 |
| Skeleton Guide | 포인트/파생 포인트/계산 기준 | 입력값이 어떻게 나온 건지 확인 |
| 육안 자세 평가 | 강도/방향/메모 | 원장님 경험 기반 평가는 MotionMetrix와 별도 저장 |
| 입력 검토 | 필수값 누락/완료율/범위 경고 | 입력 실수와 이상치 사전 확인 |
| Export | wide/long/dictionary/missing/quality | 모델링 개발자와 검수자가 바로 쓸 수 있는 형태로 출력 |
| 백업 | 전체 데이터 ZIP | Streamlit Cloud 환경에서 데이터 날아가는 거 방지용 |

---

## 4. 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 5. GitHub / Streamlit Cloud 배포

### GitHub

이 폴더를 통째로 repository에 올립니다. 필수 파일/폴더:

```text
app.py
requirements.txt
README.md
.streamlit/config.toml
src/
data/metric_definitions/
docs/
sample_data/
```

### Streamlit Cloud

Streamlit Cloud 접속 → `New app` → GitHub repository 선택 → Branch 선택 → Main file path에 `app.py` 입력 → Deploy.

### 배포 시 주의

Streamlit Cloud의 파일 저장소는 운영용 영구 저장소가 아닙니다. 테스트 중 생긴 세션 데이터는 **Export나 백업 ZIP을 자주 받아두세요.** 운영 서버, DB, 장기 보관, 24시간 장애 대응은 이 PoC 라벨링 툴 범위에 안 들어갑니다.

---

## 6. 사용 방법

### STEP 0. 샘플 세션

사이드바에서 `샘플 세션 추가` 누르면 예시 값이 들어간 `SAMPLE_001` 세션이 생깁니다. 사용법 확인용이고, 실제 검수/모델링에는 실제 MotionMetrix 값과 영상을 넣어야 합니다.

### STEP 1. 세션 정보 입력

`1. 세션 정보` 탭에서 검사 1건의 기본 정보를 입력합니다.

| 항목 | 설명 |
|---|---|
| 세션 ID | 자동 생성 가능, 검사 1건의 고유 ID |
| 사용자 ID | 개인정보 최소화를 위해 이름 대신 ID 권장 |
| 나이/성별/키/체중 | 모델 보정 변수 |
| 달리기 속도 | MotionMetrix와 스마트폰 영상 비교에 필요 |
| FPS | 측면/후면 영상의 프레임 정보 |
| 측정 시작/종료 | MotionMetrix 값과 비교할 영상 구간 |

### STEP 2. 촬영 Wizard / Skeleton Overlay Preview

`2. 촬영 Wizard/Overlay` 탭에서 고객 문서 순서대로 진행합니다.

```text
1. 후면 전신 정지 2~3초
2. 후면 달리기 촬영/확인
3. 측면 전신 정지 2~3초
4. 측면 달리기 촬영/확인
```

| 방식 | 설명 | 권장도 |
|---|---|---|
| 저장된 영상 프레임 | 촬영 완료 후 영상 업로드, 특정 시점 선택해 Overlay 생성 | 기본 / 검수 권장 |
| 카메라 스냅샷 | 브라우저 카메라로 단일 이미지 촬영해 Overlay 생성 | 보조 기능 |
| Live Camera Stream | 실시간 카메라 화면에 Overlay 표시 | 실험 기능, 환경 의존적 |

Overlay 화면에는 선택 지표의 사용 포인트, 기준선, 현재 프레임 참고 계산값이 뜹니다. 이건 라벨링 보조용이고, 최종 학습 정답값은 어디까지나 MotionMetrix 직접 입력값입니다.

실사용은 **저장된 영상 업로드 방식**을 기본으로 잡으세요. 워드 문서 순서대로 후면/측면 영상을 먼저 찍어두고, 그걸 업로드해서 프레임 Preview를 생성하는 흐름이 제일 안정적입니다. 카메라 스냅샷은 정지 자세나 포인트 노출 여부를 빠르게 확인할 때만 쓰고, Live Camera Stream은 브라우저/PC/Streamlit Cloud 조합에 따라 동작이 들쭉날쭉해서 검수 기준 기능으로는 보지 않는 게 좋습니다.

### STEP 3. 영상 업로드

`2. 영상 업로드` 탭에서 등록합니다.

```text
side_static   : 측면 전신 정지 영상 또는 정지 구간
side_running  : 측면 달리기 영상
rear_static   : 후면 전신 정지 영상 또는 정지 구간
rear_running  : 후면 달리기 영상
```

저장된 영상은 세션 폴더의 `videos/`에 보관되고, 경로는 `videos.json`, `session_meta.json`, `training_dataset_wide.csv`, `training_dataset_long.csv`에 같이 들어갑니다.

### STEP 4. MotionMetrix 값 입력

측면, 후면, 종합/선택 탭에서 MotionMetrix 결과값을 직접 입력합니다. 사이드바 `필수값만 보기`를 켜면 먼저 채워야 하는 core 항목만 보입니다. 각 입력창에는 사용 포인트와 계산 기준이 같이 표시됩니다.

### STEP 5. 육안 자세 평가 입력

`6. 육안 평가` 탭에서 원장님 경험 기반 평가를 입력합니다.

| 항목 | 입력 구조 |
|---|---|
| 걷듯이 뛴다 | 강도 / 방향 / 메모 |
| 뒤뚱거린다 | 강도 / 방향 / 메모 |
| 좌우 비대칭 | 강도 / 방향 / 메모 |
| 팔 동작 비대칭 | 강도 / 방향 / 메모 |
| 상체 좌우 흔들림 | 강도 / 방향 / 메모 |
| 무릎 상승 부족 | 강도 / 방향 / 메모 |

화면엔 한글로 보이지만 저장값은 모델링 처리를 위해 `none`, `mild`, `clear`, `severe`, `left`, `right`, `both` 같은 코드값으로 들어갑니다.

### STEP 6. Skeleton Guide 확인

`7. Skeleton Guide` 탭에서 전체 포인트와 지표별 계산 기준을 확인할 수 있습니다.

| 구분 | 포인트 |
|---|---|
| 머리 | 7 또는 8 |
| 어깨 | 11, 12 |
| 팔꿈치 | 13, 14 |
| 손목 | 15, 16 |
| 골반 | 23, 24 |
| 무릎 | 25, 26 |
| 발목 | 27, 28 |
| 뒤꿈치 | 29, 30 |
| 발끝 | 31, 32 |

### STEP 7. 검토 / Export

`9. 검토/Export` 탭에서: 필수값 누락 확인 → 입력 완료율 확인 → 현재 세션 저장 → 전체 Export 생성 → CSV 및 백업 ZIP 다운로드.

---

## 7. 저장 구조

```text
data/
  metric_definitions/
    metric_definitions_v0_4_5.json
    metric_definitions_v0_3.json
    metric_definitions_v0_2.json
    metric_definitions_v0_1.json
    keypoint_registry.json
    visual_label_definitions.json
  sessions/
    SESS_YYYYMMDD_HHMMSS/
      session_meta.json
      motionmetrix_values.json
      visual_labels.json
      videos.json
      metric_definitions_snapshot.json
      review_status.json
      preview_results.json
      preview/
        preview_YYYYMMDD_HHMMSS.png
      videos/
        side_static.mp4
        side_running.mp4
        rear_static.mp4
        rear_running.mp4

exports/
  training_dataset_wide.csv
  training_dataset_long.csv
  metric_dictionary.csv
  missing_value_report.csv
  data_quality_report.csv
  data_quality_summary.csv
  labeling_data_backup_YYYYMMDD_HHMMSS.zip

docs/
  검수_시나리오.md
  MotionMetrix_입력_가이드.md
  범위_안내.md
  Live_Overlay_Preview_가이드.md

sample_data/
  sample_session/
  sample_exports/
```

---

## 8. Export 파일 설명

| 파일 | 용도 |
|---|---|
| `training_dataset_wide.csv` | 1행 = 1세션. 3차 모델링 기본 입력 데이터셋 |
| `training_dataset_long.csv` | 1행 = 1지표. 검수/누락/계산 기준 확인용 |
| `metric_dictionary.csv` | 지표명, 단위, 사용 포인트, 계산 기준, 모델 역할 설명 |
| `missing_value_report.csv` | 필수값 누락 리포트 |
| `data_quality_report.csv` | 세션별 학습 가능 여부, 영상 누락, 이상 범위 경고 |
| `data_quality_summary.csv` | 전체 세션 수, 학습 가능 세션 수, 누락/경고 개수 요약 |
| `labeling_data_backup_*.zip` | 전체 세션/Export/정의서 백업 |

학습 데이터는 보통 `training_dataset_wide.csv`를 기준으로 구성하고, `training_dataset_long.csv`, `metric_dictionary.csv`, `data_quality_report.csv`로 각 컬럼 의미와 데이터 품질을 같이 확인하면 됩니다.

---

## 9. Live / Preview 범위

Live / Preview Skeleton Overlay는 2차 라벨링 작업을 돕는 보조 기능입니다.

지원 범위:
- MediaPipe 기반 포인트 검출
- 선택 지표별 필요 포인트 강조
- 수직선, 지면선, 몸통선 등 기준선 표시
- 현재 프레임 참고 계산값 표시
- Preview 이미지 저장 및 Export 요약 포함

지원하지 않는 범위:
- 상용 수준 실시간 분석 성능 보장
- MotionMetrix 수준의 최종 자동 수치 산출
- Braking Force / Running Economy 최종 자동 산출
- 위험도 및 처방 자동 추론
- REST API 서버
- 모바일 앱 카메라 UI

검수는 `저장된 영상 프레임` Preview 방식을 우선으로 봅니다.

---

## 10. 단위 정규화 기준

| 항목 | 입력 가능 단위 | Export 표준 단위 |
|---|---|---|
| Overstride | cm, mm | cm |
| Contact Time | ms, sec | ms |
| Vertical Oscillation | cm, mm | cm |
| Step/Stride Length | cm, m | cm |
| Flight Time | ms, sec | ms |
| Cadence | steps/min, strides/min | steps/min |

---

## 11. 3차 모델링 연결 방식

2차에서 저장되는 데이터는 3차에서 이렇게 쓰입니다.

```text
스마트폰 스켈레톤 계산값 = X
MotionMetrix 직접 입력값 = y
육안 자세 평가 = 보조 라벨
세션 정보 = 보정 변수
영상 경로 = 원본 영상 매칭 키
```

| 3차 모델 | 입력 X | 정답 y |
|---|---|---|
| Forward Lean 보정 | 스마트폰 몸통 기울기 | MotionMetrix Forward Lean |
| Overstride 보정 | 골반-발목 거리, 키, 속도 | MotionMetrix Overstride |
| Braking Force 추론 | 오버스트라이드, 무릎각, Shank Angle, 체중, 속도 | MotionMetrix Braking Force |
| Running Economy 추론 | Cadence, Contact Time, Vertical Oscillation, Overstride 등 | MotionMetrix Running Economy |
| Running Type 분류 | 전체 지표 묶음 | MotionMetrix Running Type |

---

## 12. 입력 시 주의사항

- 이름 대신 사용자 ID 사용 권장
- MotionMetrix 결과지 단위 확인 후 입력
- 범위 경고는 저장을 막는 게 아니라 원본값/단위 재확인용 안내
- 좌우 기준은 화면 기준이 아니라 신체 기준 좌/우로 통일
- Streamlit Cloud 테스트 환경에서는 Export/백업 ZIP 자주 다운로드
- 현재 버전은 직접 입력 기반. 자동 스켈레톤 계산, STT/LLM, 위험도 산출, REST API는 3차에서 연결

---

## 13. 개발자 참고

```text
app.py                    Streamlit 메인 앱
src/definitions.py        지표 정의 로딩
src/storage.py            세션/영상 저장
src/exporter.py           CSV/리포트 생성
src/ui_components.py      입력 UI, Skeleton Guide, validation
data/metric_definitions/  지표 정의서
docs/                     검수/입력/범위 안내 문서
sample_data/              샘플 입력/Export 예시
```

UI는 `metric_definitions_v0_3.json`을 우선 로딩하고, 없으면 `v0_2` → `v0_1` 순으로 fallback합니다. 지표 추가/수정은 가급적 코드가 아니라 metric definition 파일을 고치는 쪽으로 하세요.

---

## 14. 범위 정리

**포함**
- Streamlit 기반 라벨링 툴
- MotionMetrix 직접 입력
- Skeleton Point / 계산 기준 표시
- 육안 자세 평가
- 세션 저장/수정
- 영상 업로드 및 경로 Export
- CSV/JSON Export
- 데이터 품질 리포트
- 백업 ZIP 생성

**제외 (3차에서 연결 예정)**
- 자동 Pose Estimation 계산
- STT/LLM 음성 입력 자동화
- 위험도/교정 처방 추론
- REST API 서버
- 운영 서버 구축
- DB 기반 장기 운영
- MotionMetrix 원본 파일 자동 파싱