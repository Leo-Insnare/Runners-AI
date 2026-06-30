# Live / Preview Skeleton Overlay 가이드

본 문서는 v0.4.5 코드 기준의 Live / Preview Skeleton Overlay 사용 가이드입니다.  
문서 패치 v0.4.6에서 Windows/MediaPipe 설치 안내와 검수 기준 표현을 정리했습니다.

---

## 1. 목적

Live / Preview Skeleton Overlay는 고객이 워드에 정리한 촬영 순서에 맞춰 작업하면서, 필요한 Skeleton Point와 참고 계산값을 화면에서 확인하기 위한 **라벨링 보조 기능**입니다.

최종 학습 정답값은 기존과 동일하게 **MotionMetrix 결과값 직접 입력값**입니다. Overlay에서 표시되는 값은 스마트폰/웹캠 영상 기반의 참고값이며, 3차 모델링에서 보정 학습에 사용할 원시 후보값 또는 검토용 값입니다.

---

## 2. 고객 기준 작업 순서

```text
1. 세션 정보 입력
2. 후면 전신 정지 2~3초 촬영/확인
3. 후면 달리기 촬영/확인
4. 측면 전신 정지 2~3초 촬영/확인
5. 측면 달리기 촬영/확인
6. MotionMetrix 결과값 직접 입력
7. 육안 자세 평가 입력
8. 저장 및 Export
```

---

## 3. Preview 방식 구분

| 방식 | 사용 기준 | 설명 |
|---|---|---|
| 저장된 영상 프레임 Preview | 기본 권장 | 촬영 완료된 영상을 업로드하고 특정 시점의 프레임에서 Skeleton Overlay를 생성합니다. 고객 검수 기준입니다. |
| 카메라 스냅샷 | 보조 | 정지 자세, 전신 노출, 포인트 검출 여부를 단일 이미지로 확인합니다. |
| Live Camera Stream | 실험 기능 | 실시간 카메라 화면 위에 Overlay를 표시합니다. 브라우저/PC/Streamlit Cloud 환경에 따라 동작이 달라질 수 있습니다. |

고객 검수와 실제 라벨링 작업은 **저장된 영상 프레임 Preview**를 기준으로 합니다.

---

## 4. 저장 영상 프레임 Preview 사용 방법

1. `3. 영상 업로드` 탭에서 후면/측면 영상을 등록합니다.
2. `2. 촬영 Wizard/Overlay` 탭으로 이동합니다.
3. 작업 순서를 선택합니다.
   - 후면 전신 정지
   - 후면 달리기
   - 측면 전신 정지
   - 측면 달리기
4. 확인할 계산 항목을 선택합니다.
5. 영상 종류와 시간초를 선택합니다.
6. `Skeleton Preview 생성`을 클릭합니다.
7. 필요한 경우 Preview 이미지와 계산정보를 저장합니다.

---

## 5. 작업 단계별 확인 포인트

### 후면 전신 정지 2~3초

확인 목적:

- 전신 노출 여부
- 골반 23·24 검출 상태
- 발목 27·28 검출 상태
- 몸통 중심선 확인

주요 포인트:

```text
23, 24, 27, 28
```

### 후면 달리기

확인 목적:

- 골반 낙하
- 무릎 안쪽 붕괴
- 스텝 폭 / 크로스오버
- 몸통 좌우 기울기

주요 포인트:

```text
11, 12, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32
```

### 측면 전신 정지 2~3초

확인 목적:

- 어깨 중심
- 골반 중심
- 몸통선
- 수직 기준선
- 지면선

주요 포인트:

```text
11, 12, 23, 24, 27, 28, 29, 30, 31, 32
```

### 측면 달리기

확인 목적:

- Forward Lean
- Overstride
- Hip / Knee ROM
- Shank Angle
- Foot Strike Type
- Cadence / Contact Time 후보 이벤트
- Vertical Oscillation
- Step / Stride Length
- Flight Time

주요 포인트:

```text
7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32
```

---

## 6. 표시되는 계산정보의 의미

Overlay 화면에는 현재 프레임 기준 참고 계산값이 표시됩니다.

예시:

| 항목 | 의미 |
|---|---|
| Forward Lean | 골반 중심에서 어깨 중심으로 이어지는 선과 화면 수직선 사이의 각도 |
| Knee Angle | 고관절-무릎-발목 기준 현재 프레임 각도 |
| Shank Angle | 무릎-발목 선과 수직선 사이의 각도 |
| Pelvic Line Tilt | 후면 기준 23-24 골반선 기울기 |
| Detected points | 현재 프레임에서 검출된 Skeleton Point 수 |

Preview 이미지 위 텍스트는 운영체제/브라우저 폰트 차이로 한글이 깨질 수 있어 영문으로 표시합니다. 앱 우측 계산정보 패널과 입력 가이드는 한글 설명을 유지합니다.

---

## 7. 단일 프레임에서 확정할 수 없는 항목

아래 항목은 단일 프레임만으로 최종값을 확정할 수 없습니다.

- Contact Time
- Cadence
- Flight Time
- Vertical Oscillation
- Step / Stride Length
- Braking Force
- Running Economy
- Running Type

위 항목은 여러 프레임, 착지/이탈 이벤트, 속도, 체중, MotionMetrix 정답값이 함께 필요하므로 3차에서 구간/이벤트 기반 계산 또는 보정 모델로 연결합니다.

---

## 8. MediaPipe 설치/환경 오류 대응

Preview 생성 시 아래 메시지가 보이면 MediaPipe 버전 호환 문제일 가능성이 큽니다.

```text
module 'mediapipe' has no attribute 'solutions'
```

이 경우 아래 명령처럼 최신 MediaPipe를 강제 설치하면 안 됩니다.

```bat
pip install --upgrade mediapipe
pip install --upgrade --force-reinstall mediapipe opencv-python-headless
```

대신 프로젝트 폴더에서 제공된 설치 스크립트를 사용합니다.

```bat
setup_windows.bat
run_windows.bat
```

직접 설치해야 하는 경우에는 반드시 현재 프로젝트 가상환경의 Python을 명시합니다.

```bat
rmdir /s /q .venv
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Python 3.11이 없다면 `py -3.12`로 바꿔 실행합니다.

---

## 9. 범위 안내

포함되는 기능:

- 촬영 순서 Wizard
- 업로드 영상 프레임 기반 Skeleton Overlay
- 카메라 스냅샷 기반 Skeleton Overlay
- 선택 지표별 필요한 포인트 강조
- 수직선/지면선/몸통선 등 기준선 표시
- 현재 프레임 기준 참고 계산정보 표시
- Preview 이미지 및 결과 저장
- Export에 Preview 요약 포함

포함되지 않는 기능:

- 상용 수준 실시간 분석 성능 보장
- MotionMetrix 수준의 정확한 자동 수치 산출 보장
- Braking Force / Running Economy 최종 자동 산출
- 위험도 및 처방 자동 추론
- REST API 서버
- 모바일 앱 내 카메라 촬영 UI
