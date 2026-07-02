# Windows 설치 및 MediaPipe 문제 해결

본 문서는 v0.4.5 코드 기준 Windows 로컬 실행과 Skeleton Preview 관련 MediaPipe 문제 해결 방법을 정리합니다.

---

## 1. 권장 환경

- Windows 10/11
- Python 3.11 x64 권장
- Python 3.12 x64 사용 가능
- Python 3.13 이상 비추천
- Python 3.14 비추천

Skeleton Preview는 MediaPipe Pose API를 사용합니다. 최신 MediaPipe 일부 버전에서는 legacy `mp.solutions.pose` API가 제거되어 Preview가 실패할 수 있으므로, 프로젝트의 `requirements.txt` 기준 설치를 따라야 합니다.

---

## 2. 가장 안전한 설치 방법

프로젝트 폴더에서 아래 파일을 순서대로 실행합니다.

```bat
setup_windows.bat
run_windows.bat
```

`setup_windows.bat`는 기존 `.venv`를 삭제하고 Python 3.11을 우선 사용하여 새 가상환경을 만듭니다. 3.11이 없으면 3.12를 사용합니다.

---

## 3. 직접 명령으로 설치하는 방법

```bat
rmdir /s /q .venv
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Python 3.11이 없다면 `py -3.12`로 바꿔 실행합니다.

---

## 4. 설치 확인

```bat
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe -c "import mediapipe as mp; print(mp.__version__); print(hasattr(mp, 'solutions')); mp.solutions.pose.Pose(static_image_mode=True).close(); print('pose ok')"
```

정상이라면 아래와 비슷하게 출력됩니다.

```text
0.10.21
True
pose ok
```

---

## 5. 하지 말아야 할 것

아래 명령은 사용하지 않는 것을 권장합니다.

```bat
pip install mediapipe
pip install --upgrade mediapipe
pip install --upgrade --force-reinstall mediapipe opencv-python-headless
```

Windows에서 `pip`가 다른 Python 경로를 바라보거나, 최신 MediaPipe가 설치되어 Preview가 동작하지 않을 수 있습니다. 반드시 아래처럼 현재 프로젝트 가상환경의 Python을 명시하세요.

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 6. 자주 발생하는 문제

### 문제 1. `pip` 명령이 Python 3.14를 바라봄

증상:

```text
Fatal error in launcher: Unable to create process using 'C:\Python314\python.exe'
```

해결:

bare `pip`를 쓰지 말고 프로젝트 가상환경의 Python을 명시합니다.

```bat
.venv\Scripts\python.exe -m pip list
```

### 문제 2. `module 'mediapipe' has no attribute 'solutions'`

원인:

- 최신 MediaPipe 일부 버전에서 legacy solutions API가 제거됨
- 또는 잘못된 Python 환경에 MediaPipe가 설치됨

해결:

```bat
rmdir /s /q .venv
setup_windows.bat
run_windows.bat
```

직접 설치 시:

```bat
rmdir /s /q .venv
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install --no-cache-dir -r requirements.txt
```

### 문제 3. Preview 이미지 위 한글이 깨짐

v0.4.5부터 Preview 이미지 위 텍스트는 영문으로 표시합니다.  
앱 우측 계산정보 패널과 입력 가이드는 한글을 유지합니다.

---

## 7. 고객 사용 기준

고객 검수 기준은 Live Stream이 아니라 **저장된 측면/후면 촬영 영상 업로드 + 선택 프레임 Skeleton Preview**입니다.

- 저장 영상 프레임 Preview: 기본 권장
- 카메라 스냅샷: 정지 자세 확인 보조
- Live Stream: 환경 의존성이 큰 실험 기능

최종 학습 정답값은 Preview/Live 값이 아니라 MotionMetrix 직접 입력값입니다.
