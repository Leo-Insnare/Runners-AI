from __future__ import annotations

from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

StrikeClass = Literal["heel", "midfoot", "forefoot"]
FootName = Literal["left", "right"]
QualityTier = Literal["high", "medium", "low"]
StrikeVector = Annotated[List[Optional[float]], Field(min_length=17, max_length=17)]


class PatientMeta(BaseModel):
    patient_id: str = Field(min_length=1)
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    running_speed_kmh: Optional[float] = None
    video_fps: Optional[float] = None


class OverstrideRequest(BaseModel):
    session_id: str = Field(min_length=1)
    patient_meta: PatientMeta
    features: Dict[str, Optional[float]]
    quality_tier: Optional[QualityTier] = None


class OverstrideResponse(BaseModel):
    session_id: str
    patient_id: str = Field(min_length=1)
    prediction_mm: Optional[float]
    prediction_std_mm: Optional[float]
    model_pair_count: int
    quality_tier: Optional[QualityTier]
    review_required: bool
    status: Literal["completed", "unmeasurable"]
    reason: Optional[str] = None
    model_version: str


class StrikeEvent(BaseModel):
    sequence: List[StrikeVector] = Field(min_length=21, max_length=21)
    rule_class: Optional[StrikeClass] = None


class StrikeFootInput(BaseModel):
    foot: FootName
    events: List[StrikeEvent] = Field(min_length=1)


class StrikeRequest(BaseModel):
    session_id: str = Field(min_length=1)
    patient_meta: PatientMeta
    feet: List[StrikeFootInput] = Field(min_length=2, max_length=2)


class StrikeFootResult(BaseModel):
    foot: FootName
    prediction: Optional[StrikeClass]
    confidence: Optional[float]
    review_required: bool
    local_probabilities: Optional[Dict[str, float]] = None


class StrikeResponse(BaseModel):
    session_id: str
    patient_id: str = Field(min_length=1)
    status: Literal["completed", "unmeasurable"]
    reason: Optional[str] = None
    feet: List[StrikeFootResult]
    patient_anchor_class: Optional[StrikeClass] = None
    patient_anchor_confidence: Optional[float] = None
    final_class: Optional[StrikeClass] = None
    final_confidence: Optional[float] = None
    review_required: bool
    rescue_p_heel: Optional[float] = None
    rescue_activated: bool = False
    aggregation: str = "patient_consensus"
    model_version: str


class PostureMetrics(BaseModel):
    cadence_spm: Optional[float] = None
    contact_time_ms: Optional[float] = None
    forward_lean_deg: Optional[float] = None
    max_thigh_flexion_deg: Optional[float] = None
    max_thigh_extension_deg: Optional[float] = None
    knee_flexion_touchdown_deg: Optional[float] = None
    pelvic_drop_deg: Optional[float] = None
    hip_hike_difference_deg: Optional[float] = None
    shank_angle_touchdown_deg: Optional[float] = None


class QualityInfo(BaseModel):
    quality_tier: Optional[QualityTier] = None
    side_pose_rate: Optional[float] = None
    notes: List[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    session_id: str = Field(min_length=1)
    patient_meta: PatientMeta
    overstride_features: Dict[str, Optional[float]]
    strike_feet: List[StrikeFootInput] = Field(min_length=2, max_length=2)
    posture_metrics: PostureMetrics = Field(default_factory=PostureMetrics)
    quality: QualityInfo = Field(default_factory=QualityInfo)


class AnalyzeResponse(BaseModel):
    session_id: str
    patient_id: str = Field(min_length=1)
    overstride: OverstrideResponse
    strike_type: StrikeResponse
    posture_metrics: PostureMetrics
    quality: QualityInfo
    model_info: Dict[str, object]


class ModelInfoResponse(BaseModel):
    api_version: str
    model_version: str
    stage: str
    supported_metrics: List[str]
    final_independent_test_completed: bool
    final_independent_targets_met: Optional[bool]
    artifact_integrity: bool
    strike_aggregation: str
    strike_rescue_rule: str
    notes: List[str]
