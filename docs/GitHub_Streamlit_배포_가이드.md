# GitHub / Streamlit Cloud 배포 가이드

본 문서는 v0.4.5 코드와 v0.4.6 문서 패치를 GitHub와 Streamlit Cloud에 반영하는 방법을 정리합니다.

---

## 1. 기존 GitHub repository를 삭제해야 하나요?

삭제할 필요 없습니다. 기존 repository를 유지하고 파일만 교체한 뒤 commit/push 하는 방식을 권장합니다.

권장 흐름:

```text
기존 repo 유지
→ v0.4.5 코드 반영
→ v0.4.6 문서 패치 반영
→ commit/push
→ Streamlit Cloud 재배포 확인
```

---

## 2. 포함할 파일/폴더

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

---

## 3. 제외할 파일/폴더

```text
.venv/
data/sessions/
exports/
backups/
__pycache__/
*.pyc
.streamlit/secrets.toml
실제 고객 영상
실제 개인정보
실제 MotionMetrix 결과 파일
```

`.gitignore`에 위 항목이 포함되어 있는지 확인하세요.

---

## 4. Git 명령 예시

```bash
git status
git add .
git commit -m "Release running labeling tool v0.4.5 with docs patch v0.4.6"
git push origin main
```

태그를 남기려면:

```bash
git tag v0.4.6-docs
git push origin v0.4.6-docs
```

---

## 5. Streamlit Cloud 배포

1. Streamlit Cloud 접속
2. 기존 app 선택
3. GitHub repo/branch 확인
4. Main file path가 `app.py`인지 확인
5. `Reboot app` 또는 자동 재배포 확인

---

## 6. 고객에게 전달할 때

아래 표현을 권장합니다.

```text
기존 테스트 버전을 고객 문서 기준 촬영 흐름과 Skeleton Overlay Preview가 포함된 검수용 개발본으로 업데이트했습니다.
기본 사용 방식은 저장된 측면/후면 촬영 영상 업로드 후 선택 프레임에서 Skeleton Preview를 확인하고,
MotionMetrix 결과값을 직접 입력하는 방식입니다.
Live Stream은 환경 의존성이 있는 보조 기능이며,
최종 학습 정답값은 MotionMetrix 직접 입력값 기준으로 저장됩니다.
```
