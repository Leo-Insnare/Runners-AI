# 달리기 자세 라벨링 툴 v0.4.8

## 1. 2차 프로젝트 목표

```text
영상 등록 → 사용자/측정 정보 입력 → MotionMetrix 값 직접 입력
→ Skeleton Overlay로 포인트/계산 기준 확인 → 육안 평가 입력
→ 세션 저장 → 3차 모델링용 CSV/JSON Export
```

2차의 목표는 Pose Estimation이나 STT/LLM, 위험도 산출, REST API를 완성하는 게 아니라 **3차 모델링에 쓸 정답 데이터셋을 만드는 구조**를 잡는 것입니다.

---

## 1. 툴의 목적

본 Streamlit 앱은 정형외과 전문의 음성 소견 기반 달리기 자세 교정 AI 프로젝트의 **2차 라벨링 툴 개발 산출물**입니다.

2차 단계에서는 음성 자동 입력보다 **MotionMetrix 결과값 직접 입력**을 우선으로 하며, 고객이 촬영한 측면/후면 영상을 세션 단위로 등록하고, 각 지표에 필요한 Skeleton Point와 계산 기준을 확인하면서 3차 모델링용 데이터를 저장합니다.

```text
저장 영상 업로드
→ 세션 정보 입력
→ Skeleton Overlay Preview / 결과 영상 확인
→ MotionMetrix 결과값 직접 입력
→ 육안 자세 평가 입력
→ 저장
→ 3차 모델링용 CSV/JSON Export
```

최종 학습 정답값은 Preview 또는 Live Stream 값이 아니라 **고객이 직접 입력한 MotionMetrix 결과값**입니다.
>>>>>>> 661f8cc (Update labeling tool to v0.4.8)

---

## 2. 고객 기준 기본 사용 방식

고객 검수 및 실사용 기준은 아래 방식입니다.

```text
1. 스마트폰/카메라로 후면 정지 영상 촬영
2. 후면 달리기 영상 촬영
3. 측면 정지 영상 촬영
4. 측면 달리기 영상 촬영
5. 저장된 영상을 Streamlit 툴에 업로드
6. 선택 프레임에서 Skeleton Overlay Preview 확인
7. MotionMetrix 결과값 직접 입력
8. 육안 자세 평가 입력
9. 저장 및 Export
```

| 방식 | 사용 기준 | 설명 |
|---|---|---|
| 저장 영상 프레임 Preview | 기본 권장 | 촬영 완료된 영상을 업로드하고 특정 프레임에서 Skeleton Overlay와 참고 계산값을 확인합니다. |
| 카메라 스냅샷 | 보조 | 정지 자세, 전신 노출, 포인트 검출 여부를 빠르게 확인합니다. |
| Live Camera Stream | 실험 기능 | 브라우저/PC/Streamlit Cloud 환경에 따라 동작이 달라질 수 있습니다. 검수 기준 기능으로 보지 않습니다. |

---

## 3. 주요 기능

| 구분 | 기능 | 설명 |
|---|---|---|
| 세션 관리 | 신규 생성/불러오기/수정 | 검사 1건을 하나의 세션으로 저장합니다. |
| 샘플 세션 | 샘플 데이터 추가 | 처음 사용하는 고객이 입력/Export 구조를 빠르게 확인할 수 있습니다. |
| 사용자 정보 | ID, 나이, 성별, 키, 체중, 속도, FPS | 3차 모델링의 보정 변수로 사용할 수 있습니다. |
| 영상 업로드 | 측면/후면 정지·달리기 영상 | 세션 폴더에 저장하고 Export에 영상 경로를 포함합니다. |
| Skeleton 결과 영상 | MP4/CSV 다운로드 | 업로드한 영상에서 지표별 Skeleton Overlay 결과 영상과 프레임별 참고 계산 CSV를 생성합니다. |
| 촬영 Wizard/Overlay | 고객 문서 순서 기반 작업 | 후면 정지 → 후면 달리기 → 측면 정지 → 측면 달리기 순서로 확인합니다. |
| Skeleton Overlay Preview | 선택 프레임 Skeleton 표시 | MediaPipe 기반 Skeleton을 표시하고 필요한 포인트만 강조합니다. |
| 계산정보 표시 | 참고 계산값 동시 출력 | Forward Lean, Knee Angle, Shank Angle, Pelvic Line Tilt 등 현재 프레임 기준 참고값을 표시합니다. |
| MotionMetrix 입력 | 결과값 직접 입력 | 3차 모델의 정답값으로 사용됩니다. 필수 직접 입력 영역은 🟧 주황색 표시로 구분됩니다. |
| Skeleton Guide | 포인트/계산 기준 확인 | 지표별 사용 포인트, 파생 포인트, 계산 기준을 확인합니다. |
| 육안 자세 평가 | 강도/방향/메모 | 원장님 경험 기반 평가값을 별도로 저장합니다. |
| 입력 검토 | 누락/완료율/범위 경고 | 필수값 누락과 이상 범위 값을 확인합니다. |
| Export | 모델링용 파일 생성 | wide/long CSV, metric dictionary, missing report, data quality report를 생성합니다. |
| 백업 | 전체 데이터 ZIP | 테스트 환경에서 데이터 유실을 방지합니다. |

---

## 4. Windows 권장 실행 방법

Windows에서는 반드시 제공된 배치 파일 사용을 권장합니다.

```bat
setup_windows.bat
run_windows.bat
```

`setup_windows.bat`는 Python 3.11을 우선 사용하여 `.venv` 가상환경을 생성하고, `requirements.txt` 기준으로 필요한 패키지를 설치합니다. Python 3.11이 없으면 Python 3.12를 사용합니다.

### 직접 명령으로 실행해야 하는 경우

```bat
rmdir /s /q .venv
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Python 3.11이 없다면 `py -3.12`로 바꿔 실행합니다.

### 사용하지 말아야 할 명령

아래 명령은 사용하지 않는 것을 권장합니다.

```bat
pip install mediapipe
pip install --upgrade mediapipe
pip install --upgrade --force-reinstall mediapipe opencv-python-headless
```

Windows에서 `pip`가 다른 Python 경로를 바라보거나 최신 MediaPipe가 설치되어 Skeleton Preview가 동작하지 않을 수 있습니다. 반드시 현재 프로젝트 가상환경의 Python을 명시하세요.

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 5. GitHub / Streamlit Cloud 배포 방법

### GitHub 업로드

기존 repository를 삭제할 필요는 없습니다. 기존 repo의 파일을 v0.4.5 코드와 본 문서 패치로 교체한 뒤 commit/push 하면 됩니다.

GitHub에 포함할 파일/폴더:

```text
app.py
requirements.txt
README.md
runtime.txt
setup_windows.bat
run_windows.bat
.streamlit/config.toml
src/
data/metric_definitions/
docs/
sample_data/
```

GitHub에 포함하지 않을 파일/폴더:

```text
.venv/
data/sessions/
exports/
backups/
__pycache__/
*.pyc
.streamlit/secrets.toml
실제 고객 영상/개인정보/실제 MotionMetrix 결과 파일
```

### Streamlit Cloud 배포

1. Streamlit Cloud 접속
2. `New app` 선택
3. GitHub repository 선택
4. Branch 선택
5. Main file path에 `app.py` 입력
6. Deploy 실행

`runtime.txt`를 통해 Python 버전을 지정합니다. Streamlit Cloud는 테스트용 경량 환경이므로, 생성된 세션 데이터는 Export 또는 백업 ZIP으로 자주 다운로드해야 합니다.

---

## 6. 앱 사용 순서

### STEP 0. 샘플 세션 확인

좌측 사이드바에서 `샘플 세션 추가`를 클릭하면 예시 입력값이 포함된 `SAMPLE_001` 세션이 생성됩니다.

샘플 세션은 사용법 확인용입니다. 실제 검수/모델링에는 고객 측 실제 MotionMetrix 값과 실제 영상을 입력해야 합니다.

### STEP 1. 세션 정보 입력

`1. 세션 정보` 탭에서 검사 1건의 기본 정보를 입력합니다.

| 항목 | 설명 |
|---|---|
| 세션 ID | 검사 1건의 고유 ID입니다. 자동 생성할 수 있습니다. |
| 사용자 ID | 개인정보 최소화를 위해 이름 대신 ID 사용을 권장합니다. |
| 나이/성별/키/체중 | 모델 보정 변수로 사용할 수 있습니다. |
| 달리기 속도 | MotionMetrix 값과 스마트폰 영상 지표 비교에 필요합니다. |
| FPS | 측면/후면 영상 프레임 정보를 입력합니다. |
| 측정 시작/종료 | MotionMetrix 값과 비교할 영상 구간을 기록합니다. |

### STEP 2. 촬영 Wizard / Skeleton Overlay Preview

`2. 촬영 Wizard/Overlay` 탭에서 고객 문서 순서대로 작업합니다.

```text
1. 후면 전신 정지 2~3초
2. 후면 달리기 촬영/확인
3. 측면 전신 정지 2~3초
4. 측면 달리기 촬영/확인
```

저장된 영상 프레임 Preview를 기본으로 사용합니다. 선택한 지표에 따라 필요한 Skeleton Point, 기준선, 현재 프레임 기준 참고 계산값이 표시됩니다.

Preview 이미지 위 텍스트는 운영체제/브라우저 폰트 차이로 한글이 깨질 수 있어 영문으로 표시합니다. 앱 우측 계산정보 패널과 입력 가이드는 한글 설명을 유지합니다.

### STEP 3. 영상 업로드

`3. 영상 업로드` 탭에서 영상을 등록합니다.

```text
side_static    : 측면 전신 정지 영상 또는 정지 구간
side_running   : 측면 달리기 영상
rear_static    : 후면 전신 정지 영상 또는 정지 구간
rear_running   : 후면 달리기 영상
```

저장된 영상은 세션 폴더의 `videos/` 하위에 보관되며, 영상 경로는 `videos.json`, `session_meta.json`, `training_dataset_wide.csv`, `training_dataset_long.csv`에 포함됩니다.

### STEP 4. MotionMetrix 값 입력

아래 탭에서 MotionMetrix 결과값을 직접 입력합니다.

| 탭 | 주요 입력 항목 |
|---|---|
| `4. MotionMetrix 입력 - 측면` | Forward Lean, Overstride, Braking Force, Hip/Knee ROM, Shank Angle, Cadence, Contact Time, Vertical Oscillation 등 |
| `5. MotionMetrix 입력 - 후면` | Pelvic Drop, Knee Medial Collapse, Step Width/Crossover, Trunk Lateral Tilt 등 |
| `6. 종합/선택 입력` | Running Economy, Running Type, Vertical Force, Lateral Force, Stride Rating 등 |

사이드바의 `필수값만 보기`를 켜면 먼저 입력해야 하는 core 필수 항목만 표시됩니다.

### STEP 5. 육안 자세 평가 입력

`7. 육안 평가` 탭에서 원장님 경험 기반 평가를 입력합니다.

| 항목 | 입력 구조 |
|---|---|
| 걷듯이 뛴다 | 강도 / 방향 / 메모 |
| 뒤뚱거린다 | 강도 / 방향 / 메모 |
| 좌우 비대칭 | 강도 / 방향 / 메모 |
| 팔 동작 비대칭 | 강도 / 방향 / 메모 |
| 상체 좌우 흔들림 | 강도 / 방향 / 메모 |
| 무릎 상승 부족 | 강도 / 방향 / 메모 |

화면에는 한글 선택값이 보이고, 저장값은 모델링용 영문 코드로 저장됩니다.

### STEP 6. Skeleton Guide 확인

`8. Skeleton Guide` 탭에서 전체 Skeleton Point와 지표별 계산 기준을 확인합니다.

예시:

```text
Forward Lean
- 사용 포인트: 11, 12, 23, 24
- 파생 포인트: shoulder_center, pelvis_center, trunk_line
- 계산 기준: 골반 중심 → 어깨 중심 선과 화면 수직선 사이의 각도
```

### STEP 7. 검토 / Export

`9. 검토/Export` 탭에서 누락값, 입력 완료율, 데이터 품질 요약을 확인한 뒤 Export를 생성합니다.

생성 파일:

```text
training_dataset_wide.csv
training_dataset_long.csv
metric_dictionary.csv
missing_value_report.csv
data_quality_report.csv
data_quality_summary.csv
```

---

## 7. Export 파일 설명

| 파일 | 용도 |
|---|---|
| `training_dataset_wide.csv` | 1 row = 1 session 구조의 3차 모델 학습용 데이터 |
| `training_dataset_long.csv` | metric 단위 검수/추적용 데이터 |
| `metric_dictionary.csv` | 각 컬럼의 의미, 단위, skeleton point, 계산 기준 설명 |
| `missing_value_report.csv` | 필수값 누락 확인 |
| `data_quality_report.csv` | 세션별 데이터 품질 검토 |
| `data_quality_summary.csv` | 전체 세션 품질 요약 |

---

## 8. 2차/3차 범위 안내

### 2차 포함 범위

- MotionMetrix 결과값 직접 입력
- 측면/후면 영상 세션 관리
- 고객 문서 순서 기반 촬영 Wizard
- 업로드 영상 프레임 기반 Skeleton Overlay Preview
- 카메라 스냅샷 기반 Skeleton Overlay Preview
- 선택 지표별 필요한 Skeleton Point 강조
- 현재 프레임 기준 참고 계산정보 표시
- Skeleton Point 및 계산 기준 확인
- 육안 자세 평가 입력
- 세션 저장 및 3차 모델링용 Export
- 누락값/데이터 품질 리포트
- 전체 백업 ZIP 생성

### 실험/보조 기능

- Live Camera Stream 기반 Skeleton Overlay

Live Stream은 브라우저 권한, PC 카메라, 네트워크, Streamlit Cloud 환경에 따라 동작이 달라질 수 있습니다. 고객 검수 기준은 저장 영상 프레임 Preview입니다.

### 3차 또는 별도 협의 범위

- MotionMetrix 수준의 자동 수치 산출 보장
- Braking Force 최종 자동 산출
- Running Economy 최종 자동 산출
- Running Type 최종 자동 분류
- STT/LLM 기반 음성 자동 입력
- 위험도/교정 처방 추론
- REST API 서버
<<<<<<< HEAD
- 운영 서버 구축
- DB 기반 장기 운영
- MotionMetrix 원본 파일 자동 파싱
=======
- MotionMetrix 파일 자동 파싱
- 모바일 앱 내 카메라 촬영 UI
- 운영 서버 구축 또는 상용 서비스 수준 장애 대응
- 실시간 분석 성능 보장

---
