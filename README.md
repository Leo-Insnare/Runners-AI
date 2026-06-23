# Running Pose Mobile Skeleton Viewer

2차 본개발 전 고객 검증용 PoC UI입니다. 스마트폰 브라우저에서 Streamlit Cloud URL로 접속하면 MediaPipe Pose 기반의 실시간 skeleton overlay와 각 관절의 정규화 좌표를 바로 확인할 수 있습니다.

---

## 데모 목적

본개발 전에 고객이 다음 내용을 실제로 확인하는 것이 목적입니다.

- 스마트폰 카메라에서 skeleton이 실시간으로 어떻게 그려지는지
- MediaPipe Pose 33개 landmark의 구조와 번호 배치
- 각 point의 정규화 좌표 `x / y / z`가 어떤 형태로 나오는지
- 전면 · 후면 · 후측방 45도 촬영 방향별 pose 결과 차이

---

## 주요 기능

- 스마트폰 브라우저에서 카메라 실시간 입력 (후면 카메라 우선)
- 촬영 방향 선택 — 전면 / 후면 / 후측방 45도
- skeleton overlay + 주요 landmark 번호 표시
- 33개 landmark reference 이미지 상시 표시
- 정규화 좌표 실시간 출력
  - `x` — 화면 가로 기준 0 ~ 1
  - `y` — 화면 세로 기준 0 ~ 1
  - `z` — MediaPipe 기준 상대 깊이값 (실제 거리 아님)
- 현재 프레임 좌표 CSV 다운로드
- 최근 좌표 로그 CSV 다운로드

---

## 로컬 실행

Python 3.11 기준입니다. 다른 버전에서는 MediaPipe 의존성 문제가 생길 수 있습니다.

### Windows

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

마찬가지로 스크립트를 쓸 수 있습니다.

```bash
chmod +x run_local_py311_macos_linux.sh && ./run_local_py311_macos_linux.sh
```

로컬 환경 관련 추가 내용은 `README_LOCAL_PY311.md`를 참고하세요.

---

## Streamlit Cloud 배포

1. GitHub 저장소를 만들고 아래 네 개 파일을 올립니다.
   ```
   app.py
   requirements.txt
   runtime.txt
   assets/mediapipe_pose_points.png
   ```
2. Streamlit Cloud → **New app** → 저장소 · 브랜치 선택
3. Main file path: `app.py`
4. Deploy 후 생성된 HTTPS URL을 고객에게 공유합니다.

---

## 촬영 권장 조건

결과 품질은 촬영 환경에 크게 좌우됩니다. 데모 전에 아래 조건을 먼저 맞춰두는 것이 좋습니다.

- 후면 카메라 사용, 한 명만 프레임에 포함
- 전신이 화면 안에 들어오도록 3 ~ 5m 거리 확보
- 역광 · 저조도 · 흔들림 피하기 (가능하면 삼각대)
- 전면 / 후면 / 후측방 45도 각 방향을 동일 조건에서 테스트

---

## 좌표 해석

데모에서 표시하는 좌표는 정규화값입니다. 실제 cm/mm 거리가 아닙니다.

| 컬럼 | 설명 |
|------|------|
| `x` | 화면 왼쪽 = 0, 오른쪽 = 1 |
| `y` | 화면 위쪽 = 0, 아래쪽 = 1 |
| `z` | MediaPipe 추정 상대 깊이값. 절대 거리 아님 |
| `visibility` | 해당 landmark의 검출 신뢰도 (0 ~ 1) |

이 좌표를 본개발 알고리즘에서 바로 판단에 쓰는 건 권장하지 않습니다. frame sampling, smoothing, 이상치 제거, 촬영 방향별 지표 변환 단계를 거친 뒤 사용하는 것이 안전합니다.

---

## Description

> 스마트폰 카메라로 촬영한 영상에서 주요 관절 33개 point를 실시간으로 추출하고, 각 point를 정규화된 `x / y / z` 좌표로 보여주는 데모입니다.
> 본 알고리즘 단계에서는 이 좌표를 기반으로 좌우 밸런스, 관절 각도, 착지 패턴 등 자세 지표를 계산하는 구조로 확장됩니다.
