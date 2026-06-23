# Runners-AI

Smartphone browser + Streamlit Cloud + MediaPipe Pose 기반 실시간 running skeleton / normalized coordinate viewer입니다.

## 주요 기능

- 스마트폰 브라우저 카메라 입력
- 전면 / 후면 / 후측방 45도 촬영 방향 선택
- MediaPipe Pose 33개 landmark skeleton overlay
- 정규화 좌표 `x, y, z, visibility` 실시간 표시
- 현재 프레임 / 최근 로그 CSV 다운로드

## Streamlit Cloud 배포 설정

- Repository: `Leo-Insnare/Runners-AI`
- Branch: `main`
- Main file path: `app.py`
- Python: `3.11`

## 로컬 실행

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
streamlit run app.py
```

## 고객 데모 주의사항

- 스마트폰 카메라 접근은 HTTPS 환경에서 안정적으로 동작합니다.
- Streamlit Cloud URL은 HTTPS로 제공됩니다.
- MediaPipe `z` 좌표는 상대 깊이 추정값이며 실제 cm/mm 단위 실측값이 아닙니다.
- 본 앱은 2차 프로젝트 전 고객 확인용 PoC 데모입니다.
