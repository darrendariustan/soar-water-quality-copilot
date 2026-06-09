from pydantic import BaseModel, Field
from typing import Optional

class WaterAppearancePayload(BaseModel):
    """
    Metadata payload representing the visual appearance of the water sample.
    """
    image_url: str = Field(..., description="S3 or local path to the water sample image")
    clarity_classification: Optional[str] = Field(None, description="Clear, cloudy, or colored")
    particle_detected: bool = Field(False, description="True if visible particles are detected")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Computer Vision confidence score")

class WaterTestStripPayload(BaseModel):
    """
    Metadata payload representing the readings from a dip test strip.
    """
    image_url: str = Field(..., description="S3 or local path to the test strip image")
    ph: Optional[float] = Field(None, description="pH level (e.g., 6.5 - 8.5 is generally safe)")
    chlorine_residual_ppm: Optional[float] = Field(None, description="Free chlorine residual in ppm")
    turbidity_ntu: Optional[float] = Field(None, description="Turbidity in NTU")
    nitrate_ppm: Optional[float] = Field(None, description="Nitrate level in ppm")
    nitrite_ppm: Optional[float] = Field(None, description="Nitrite level in ppm")
    hardness_ppm: Optional[float] = Field(None, description="Water hardness in ppm")
    iron_ppm: Optional[float] = Field(None, description="Iron concentration in ppm")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Computer Vision confidence score")

class WaterQualityAnalysisRequest(BaseModel):
    """
    Combined request payload for starting an agentic analysis.
    """
    user_id: str = Field(..., description="Anonymized user ID")
    location: Optional[str] = Field(None, description="Approximate location for community risk reporting")
    appearance: WaterAppearancePayload
    test_strip: WaterTestStripPayload
