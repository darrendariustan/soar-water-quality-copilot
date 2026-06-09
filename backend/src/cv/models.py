from pydantic import BaseModel
from typing import Literal


class MatchedColour(BaseModel):
    rgb: list[int]
    hsv: list[int]


class ParameterReading(BaseModel):
    name: str
    estimated_value: str
    unit: str
    matched_colour: MatchedColour
    confidence: float


class ImageQuality(BaseModel):
    brightness: Literal["low", "acceptable", "high"]
    blur: Literal["low", "medium", "high"]
    lighting_warning: bool


class StripAnalysisResult(BaseModel):
    image_type: Literal["test_strip"] = "test_strip"
    parameters: list[ParameterReading]
    overall_confidence: float
    image_quality: ImageQuality
    warnings: list[str]


class WaterAppearance(BaseModel):
    clarity: Literal["clear", "slightly_cloudy", "cloudy", "opaque"]
    colour: Literal["colourless", "slightly_yellow", "slightly_brown", "green", "other"]
    visible_particles: bool


class WaterSampleResult(BaseModel):
    image_type: Literal["water_sample"] = "water_sample"
    appearance: WaterAppearance
    overall_confidence: float
    warnings: list[str]
