from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from .config import API_VERSION, MODEL_VERSION, load_status
from .debug_export_adapter import DebugExportAdapter
from .model_engine import FrozenModelEngine
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ModelInfoResponse,
    OverstrideRequest,
    OverstrideResponse,
    StrikeRequest,
    StrikeResponse,
)
from .security import require_token

app = FastAPI(title="RunningAI API", version="1.2.0")


@lru_cache(maxsize=1)
def get_engine() -> FrozenModelEngine:
    return FrozenModelEngine()


def _overstride_features(req: OverstrideRequest) -> dict[str, float | None]:
    features = dict(req.features)
    if req.patient_meta.height_cm is not None:
        features["height_cm"] = req.patient_meta.height_cm
    if req.patient_meta.running_speed_kmh is not None:
        features["running_speed_kmh"] = req.patient_meta.running_speed_kmh
    return features


@app.get("/health")
def health():
    return {"status": "ok", "api_version": API_VERSION, "model_version": MODEL_VERSION}


@app.get(
    "/api/v1/model/info",
    response_model=ModelInfoResponse,
    dependencies=[Depends(require_token)],
)
def model_info():
    engine = get_engine()
    status = load_status()
    return ModelInfoResponse(
        api_version=API_VERSION,
        model_version=MODEL_VERSION,
        stage="final-independent-completed" if status.get("final_independent_test_completed") else "frozen-pre-final-independent",
        supported_metrics=[
            "overstride",
            "strike_type",
            "cadence",
            "contact_time",
            "forward_lean",
            "max_thigh_flexion",
            "max_thigh_extension",
            "knee_flexion_touchdown",
            "pelvic_drop",
            "hip_hike_difference",
            "shank_angle_touchdown",
        ],
        final_independent_test_completed=bool(status.get("final_independent_test_completed", False)),
        final_independent_targets_met=status.get("final_independent_targets_met"),
        artifact_integrity=engine.status.artifact_integrity,
        strike_aggregation="bilateral patient-consensus",
        strike_rescue_rule="anchor=forefoot and rescue P(heel)>=0.65",
        notes=[
            "feet[].prediction is a per-foot auxiliary output.",
            "The frozen v0.16 Strike performance gate applies to final_class.",
            "Debug Export and direct API requests use the same FrozenModelEngine.",
        ],
    )


@app.post(
    "/api/v1/predict/overstride",
    response_model=OverstrideResponse,
    dependencies=[Depends(require_token)],
)
def predict_overstride(req: OverstrideRequest):
    try:
        raw = get_engine().predict_overstride(_overstride_features(req))
    except Exception as e:
        raise HTTPException(status_code=422, detail={"code": "OVERSTRIDE_INPUT_ERROR", "message": str(e)}) from e
    quality = req.quality_tier
    review = raw["status"] != "completed" or (quality is not None and quality == "low")
    return OverstrideResponse(
        session_id=req.session_id,
        patient_id=req.patient_meta.patient_id,
        prediction_mm=raw["prediction_mm"],
        prediction_std_mm=raw["prediction_std_mm"],
        model_pair_count=raw["model_pair_count"],
        quality_tier=quality,
        review_required=review,
        status=raw["status"],
        reason=raw["reason"],
        model_version=MODEL_VERSION,
    )


@app.post(
    "/api/v1/predict/strike-type",
    response_model=StrikeResponse,
    dependencies=[Depends(require_token)],
)
def predict_strike(req: StrikeRequest):
    try:
        raw = get_engine().predict_strike([x.model_dump() for x in req.feet])
    except Exception as e:
        raise HTTPException(status_code=422, detail={"code": "STRIKE_INPUT_ERROR", "message": str(e)}) from e
    return StrikeResponse(
        session_id=req.session_id,
        patient_id=req.patient_meta.patient_id,
        status=raw["status"],
        reason=raw["reason"],
        feet=raw["feet"],
        patient_anchor_class=raw["patient_anchor_class"],
        patient_anchor_confidence=raw["patient_anchor_confidence"],
        final_class=raw["final_class"],
        final_confidence=raw["final_confidence"],
        review_required=raw["review_required"],
        rescue_p_heel=raw["rescue_p_heel"],
        rescue_activated=raw["rescue_activated"],
        model_version=MODEL_VERSION,
    )


@app.post(
    "/api/v1/analyze",
    response_model=AnalyzeResponse,
    dependencies=[Depends(require_token)],
)
def analyze(req: AnalyzeRequest):
    overstride = predict_overstride(OverstrideRequest(
        session_id=req.session_id,
        patient_meta=req.patient_meta,
        features=req.overstride_features,
        quality_tier=req.quality.quality_tier,
    ))
    strike = predict_strike(StrikeRequest(
        session_id=req.session_id,
        patient_meta=req.patient_meta,
        feet=req.strike_feet,
    ))
    info = model_info()
    return AnalyzeResponse(
        session_id=req.session_id,
        patient_id=req.patient_meta.patient_id,
        overstride=overstride,
        strike_type=strike,
        posture_metrics=req.posture_metrics,
        quality=req.quality,
        model_info=info.model_dump(),
    )


@app.post(
    "/api/v1/adapter/debug-export",
    response_model=AnalyzeRequest,
    dependencies=[Depends(require_token)],
)
async def adapt_debug_export(file: UploadFile = File(...)):
    try:
        result = DebugExportAdapter.from_bytes(await file.read()).build()
        return result.request
    except Exception as e:
        raise HTTPException(status_code=422, detail={"code": "DEBUG_EXPORT_ERROR", "message": str(e)}) from e


@app.post(
    "/api/v1/analyze/debug-export",
    response_model=AnalyzeResponse,
    dependencies=[Depends(require_token)],
)
async def analyze_debug_export(file: UploadFile = File(...)):
    try:
        result = DebugExportAdapter.from_bytes(await file.read()).build()
    except Exception as e:
        raise HTTPException(status_code=422, detail={"code": "DEBUG_EXPORT_ERROR", "message": str(e)}) from e
    return analyze(result.request)
