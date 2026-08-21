# RunningAI API v1.2

v0.16 frozen 모델 API 통합본입니다. Python 3.12 환경을 권장합니다. Debug Export ZIP을 바로 분석할 수 있고, 직접 JSON 요청도 지원합니다.

## 실행

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
python run_api.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python run_api.py
```

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- `/api/v1/*`: Bearer Token 필요

## 주요 API

- `GET /health`
- `GET /api/v1/model/info`
- `POST /api/v1/predict/overstride`
- `POST /api/v1/predict/strike-type`
- `POST /api/v1/analyze`
- `POST /api/v1/adapter/debug-export`
- `POST /api/v1/analyze/debug-export`

Strike의 최종 판정값은 `final_class`입니다. `feet[].prediction`은 좌우 발별 참고값입니다.

Debug Export 연동은 `integrations/streamlit_client.py`, parity 검증은 `scripts/validate_parity.py`를 사용합니다.

```bash
pytest -q
```

상세 규격은 `API_SPEC_v1.md`, 검증 결과는 `PARITY_VALIDATION.md`에 정리했습니다.
