import time
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

try:
    import av
except ModuleNotFoundError:
    st.error("PyAV 패키지(av)가 설치되어 있지 않습니다.")
    st.code(
        r"""
# Windows
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary=:all: av==12.3.0
python -m pip install -r requirements.txt
streamlit run app.py
""",
        language="bash",
    )
    st.stop()

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd

try:
    from streamlit_webrtc import RTCConfiguration, VideoProcessorBase, WebRtcMode, webrtc_streamer
except ModuleNotFoundError as e:
    st.error(f"필수 패키지가 설치되어 있지 않습니다: {e.name}")
    st.code(
        r"""
python -m pip install --upgrade pip setuptools wheel
python -m pip install tornado==6.4.2
python -m pip install --only-binary=:all: av==12.3.0
python -m pip install streamlit streamlit-webrtc mediapipe opencv-python numpy pandas pillow
streamlit run app.py
""",
        language="bash",
    )
    st.stop()


ASSET_DIR = Path(__file__).resolve().parent / "assets"
POSE_POINT_IMAGE = ASSET_DIR / "mediapipe_pose_points.png"

RTC_CONFIGURATION = RTCConfiguration(
    {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
        ]
    }
)

LANDMARK_NAMES = [
    "nose",
    "left_eye_inner",
    "left_eye",
    "left_eye_outer",
    "right_eye_inner",
    "right_eye",
    "right_eye_outer",
    "left_ear",
    "right_ear",
    "mouth_left",
    "mouth_right",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_pinky",
    "right_pinky",
    "left_index",
    "right_index",
    "left_thumb",
    "right_thumb",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
    "left_heel",
    "right_heel",
    "left_foot_index",
    "right_foot_index",
]

IMPORTANT_POINT_IDS = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]

VIEW_HINTS = {
    "전면": "러너가 카메라를 바라보는 방향입니다. 좌우 어깨/골반/무릎/발목 밸런스 확인에 유리합니다.",
    "후면": "러너의 뒤쪽을 촬영하는 방향입니다. 좌우 골반/무릎/발목 궤적 비교에 유리합니다.",
    "후측방 45도": "뒤쪽에서 약 45도 비스듬히 촬영하는 방향입니다. 측면 움직임과 좌우 비대칭을 함께 확인하기 좋습니다.",
}


def visibility_label(value: float) -> str:
    if value >= 0.75:
        return "높음"
    if value >= 0.5:
        return "보통"
    return "낮음"


class PoseProcessor(VideoProcessorBase):
    """MediaPipe Pose processor for smartphone browser camera input."""

    def __init__(self, view_direction: str, overlay_labels: bool = True) -> None:
        self.lock = threading.Lock()
        self.view_direction = view_direction
        self.overlay_labels = overlay_labels
        self.frame_index = 0
        self.latest_landmarks: List[Dict[str, Any]] = []
        self.latest_summary: Dict[str, Any] = {
            "status": "waiting",
            "view_direction": view_direction,
            "frame_index": 0,
            "detected_points": 0,
            "avg_visibility": 0.0,
            "timestamp": None,
        }
        self.history: deque = deque(maxlen=33 * 300)

        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def _landmarks_to_rows(self, results: Any, frame_index: int) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        if not results.pose_landmarks:
            return rows

        timestamp = datetime.now().isoformat(timespec="milliseconds")

        for idx, lm in enumerate(results.pose_landmarks.landmark):
            visibility = round(float(getattr(lm, "visibility", 0.0)), 6)
            rows.append(
                {
                    "timestamp": timestamp,
                    "view_direction": self.view_direction,
                    "frame_index": frame_index,
                    "point_id": idx,
                    "point_name": LANDMARK_NAMES[idx] if idx < len(LANDMARK_NAMES) else f"landmark_{idx}",
                    "x": round(float(lm.x), 6),
                    "y": round(float(lm.y), 6),
                    "z": round(float(lm.z), 6),
                    "visibility": visibility,
                    "visibility_level": visibility_label(visibility),
                }
            )
        return rows

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image_bgr = frame.to_ndarray(format="bgr24")
        height, width = image_bgr.shape[:2]

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = self.pose.process(image_rgb)
        image_rgb.flags.writeable = True

        annotated_bgr = image_bgr.copy()
        rows: List[Dict[str, Any]] = []
        status = "no_pose"
        avg_visibility = 0.0

        if results.pose_landmarks:
            rows = self._landmarks_to_rows(results, self.frame_index)
            status = "pose_detected"
            if rows:
                avg_visibility = float(np.mean([r["visibility"] for r in rows]))

            self.mp_drawing.draw_landmarks(
                annotated_bgr,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_styles.get_default_pose_landmarks_style(),
            )

            if self.overlay_labels:
                for point_id in IMPORTANT_POINT_IDS:
                    lm = results.pose_landmarks.landmark[point_id]
                    if getattr(lm, "visibility", 0.0) < 0.45:
                        continue
                    x_px = int(lm.x * width)
                    y_px = int(lm.y * height)
                    if 0 <= x_px < width and 0 <= y_px < height:
                        cv2.putText(
                            annotated_bgr,
                            str(point_id),
                            (x_px + 6, y_px - 6),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.45,
                            (255, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

            cv2.putText(
                annotated_bgr,
                f"{self.view_direction} | Pose OK | points {len(rows)} | vis {avg_visibility:.2f}",
                (18, 34),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
        else:
            cv2.putText(
                annotated_bgr,
                "No pose - keep full body visible",
                (18, 34),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

        with self.lock:
            self.latest_landmarks = rows
            self.latest_summary = {
                "status": status,
                "view_direction": self.view_direction,
                "frame_index": self.frame_index,
                "detected_points": len(rows),
                "avg_visibility": round(avg_visibility, 4),
                "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            }
            if rows:
                self.history.extend(rows)
            self.frame_index += 1

        return av.VideoFrame.from_ndarray(annotated_bgr, format="bgr24")


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def render_landmark_reference() -> None:
    st.subheader("MediaPipe Pose 33개 Skeleton Point")
    if POSE_POINT_IMAGE.exists():
        st.image(str(POSE_POINT_IMAGE), caption="MediaPipe Pose landmark index", width="stretch")
    else:
        st.warning("assets/mediapipe_pose_points.png 파일이 없습니다.")

    ref_df = pd.DataFrame({"point_id": list(range(len(LANDMARK_NAMES))), "point_name": LANDMARK_NAMES})
    st.dataframe(ref_df, width="stretch", hide_index=True, height=520)


def render_coordinate_guide() -> None:
    st.markdown(
        """
        #### 정규화 좌표 해석
        - `x`: 화면의 가로 위치입니다. `0`은 왼쪽, `1`은 오른쪽입니다.
        - `y`: 화면의 세로 위치입니다. `0`은 위쪽, `1`은 아래쪽입니다.
        - `z`: MediaPipe가 추정하는 상대 깊이값입니다. 절대 거리나 cm/mm 값이 아닙니다.
        - `visibility`: 해당 포인트가 화면에서 안정적으로 보이는 정도입니다. PoC에서는 보통 `0.5` 이상을 유효 후보로 봅니다.
        """
    )


def make_media_constraints(camera_source: str, orientation: str) -> Dict[str, Any]:
    facing_mode = "environment" if camera_source == "스마트폰 후면 카메라" else "user"

    if orientation == "세로 촬영":
        width_ideal, height_ideal = 720, 1280
    else:
        width_ideal, height_ideal = 1280, 720

    return {
        "video": {
            "facingMode": {"ideal": facing_mode},
            "width": {"ideal": width_ideal},
            "height": {"ideal": height_ideal},
            "frameRate": {"ideal": 30, "max": 30},
        },
        "audio": False,
    }


def main() -> None:
    st.set_page_config(
        page_title="Running Pose Mobile Skeleton Viewer",
        page_icon="🏃",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🏃 Running Pose Mobile Skeleton Viewer")
    st.caption("스마트폰 브라우저 + Streamlit Cloud + MediaPipe Pose 기반 실시간 skeleton/정규화 좌표 확인용 PoC UI")

    with st.sidebar:
        st.header("촬영 설정")
        view_direction = st.radio("러너 촬영 방향", ["전면", "후면", "후측방 45도"], index=0)
        st.caption(VIEW_HINTS[view_direction])

        camera_source = st.radio(
            "스마트폰 카메라",
            ["스마트폰 후면 카메라", "스마트폰 전면 카메라"],
            index=0,
            help="달리는 사람을 다른 사람이 촬영하는 경우 후면 카메라를 권장합니다.",
        )
        orientation = st.radio("촬영 화면 방향", ["세로 촬영", "가로 촬영"], index=0)

        st.divider()
        show_reference = st.toggle("Skeleton point 이미지 함께 보기", value=True)
        show_live_table = st.toggle("실시간 좌표 테이블 표시", value=True)
        show_only_important = st.toggle("주요 포인트만 먼저 보기", value=True)
        overlay_labels = st.toggle("영상 위 주요 point 번호 표시", value=True)
        table_refresh_sec = st.slider("좌표 갱신 간격(초)", 0.2, 1.5, 0.5, 0.1)

        st.divider()
        st.info("Streamlit Cloud URL은 HTTPS로 제공되므로 스마트폰 카메라 권한 허용 후 바로 테스트할 수 있습니다.")

    tab_live, tab_reference, tab_deploy = st.tabs(["실시간 촬영", "포인트/좌표 가이드", "배포/고객 안내"])

    with tab_live:
        st.markdown(
            f"""
            **현재 촬영 방향:** `{view_direction}`  
            **카메라:** `{camera_source}` / **화면:** `{orientation}`
            """
        )

        col_video, col_data = st.columns([1.1, 1.0], gap="large")

        with col_video:
            st.subheader("실시간 Skeleton Overlay")
            st.caption("스마트폰에서 접속 후 Start를 누르고 카메라 권한을 허용하세요. 전신이 화면에 들어오도록 3~5m 정도 거리를 권장합니다.")

            media_constraints = make_media_constraints(camera_source, orientation)

            ctx = webrtc_streamer(
                key=f"running-pose-{view_direction}-{camera_source}-{orientation}",
                mode=WebRtcMode.SENDRECV,
                frontend_rtc_configuration=RTC_CONFIGURATION,
                server_rtc_configuration=RTC_CONFIGURATION,
                video_processor_factory=lambda: PoseProcessor(
                    view_direction=view_direction,
                    overlay_labels=overlay_labels,
                ),
                media_stream_constraints=media_constraints,
                async_processing=True,
            )

            st.warning(
                "이 화면은 고객이 skeleton과 좌표가 어떤 형태로 나오는지 확인하는 데모입니다. "
                "z 좌표는 상대 깊이값이며 실제 거리값으로 보증하지 않습니다.",
                icon="⚠️",
            )

        with col_data:
            st.subheader("정규화 3D 좌표 출력")
            render_coordinate_guide()

            status_box = st.empty()
            metric_cols = st.columns(3)
            table_box = st.empty()
            download_box = st.empty()

            if ctx.video_processor and show_live_table:
                while ctx.state.playing:
                    with ctx.video_processor.lock:
                        rows = list(ctx.video_processor.latest_landmarks)
                        summary = dict(ctx.video_processor.latest_summary)
                        history_rows = list(ctx.video_processor.history)

                    status_box.json(summary, expanded=False)
                    metric_cols[0].metric("상태", summary.get("status", "waiting"))
                    metric_cols[1].metric("검출 Point", summary.get("detected_points", 0))
                    metric_cols[2].metric("평균 Visibility", summary.get("avg_visibility", 0.0))

                    if rows:
                        df = pd.DataFrame(rows)
                        if show_only_important:
                            display_df = df[df["point_id"].isin(IMPORTANT_POINT_IDS)].copy()
                        else:
                            display_df = df.copy()

                        display_cols = [
                            "view_direction",
                            "frame_index",
                            "point_id",
                            "point_name",
                            "x",
                            "y",
                            "z",
                            "visibility",
                            "visibility_level",
                        ]
                        table_box.dataframe(
                            display_df[display_cols],
                            width="stretch",
                            hide_index=True,
                            height=520,
                        )

                        csv_cols = [
                            "timestamp",
                            "view_direction",
                            "frame_index",
                            "point_id",
                            "point_name",
                            "x",
                            "y",
                            "z",
                            "visibility",
                            "visibility_level",
                        ]
                        current_csv = dataframe_to_csv_bytes(df[csv_cols])
                        download_box.download_button(
                            label="현재 프레임 정규화 좌표 CSV 다운로드",
                            data=current_csv,
                            file_name=f"pose_normalized_{view_direction}_current.csv",
                            mime="text/csv",
                            key=f"download_current_{summary.get('frame_index', 0)}",
                        )

                        if history_rows:
                            history_df = pd.DataFrame(history_rows)
                            download_box.download_button(
                                label="최근 좌표 로그 CSV 다운로드",
                                data=dataframe_to_csv_bytes(history_df[csv_cols]),
                                file_name=f"pose_normalized_{view_direction}_history.csv",
                                mime="text/csv",
                                key=f"download_history_{summary.get('frame_index', 0)}",
                            )
                    else:
                        table_box.info("아직 pose가 감지되지 않았습니다. 전신이 화면에 들어오도록 카메라 거리와 각도를 조정해 주세요.")

                    time.sleep(table_refresh_sec)
            else:
                st.info("Start 버튼을 누르면 정규화 좌표가 표시됩니다.")

        if show_reference:
            st.divider()
            render_landmark_reference()

    with tab_reference:
        render_landmark_reference()
        render_coordinate_guide()
        st.markdown(
            """
            #### 
            이 데모는 스마트폰 카메라 영상에서 사람의 주요 관절 33개 포인트를 추출하고, 각 포인트를 `x, y, z` 정규화 좌표로 표시합니다.  
            추후 3차 알고리즘 단계에서는 이 좌표를 기반으로 좌우 밸런스, 관절 각도, 보폭/착지 패턴 등 지표를 계산하는 구조로 확장합니다.
            """
        )

    with tab_deploy:
        st.subheader("Streamlit Cloud 이용 가이드")
        st.markdown(
            """
            #### 고객 데모 전 권장 촬영 조건
            - 한 명만 화면에 나오게 촬영
            - 전신이 화면 안에 들어오게 촬영
            - 심한 역광, 저조도, 흔들림 피하기
            - 가능하면 스마트폰을 고정하거나 삼각대 사용
            - 전/후/후측방 45도별 샘플을 동일 조건으로 각각 촬영
            """
        )


if __name__ == "__main__":
    main()