from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from schemas import WaterQualityAnalysisRequest, WaterAppearancePayload, WaterTestStripPayload
from agents.master_agent import run_pipeline
from cv.submission_handler import process_submission
import os
from dotenv import load_dotenv

# Load .env from the project root if it exists
root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
load_dotenv(root_env)

app = FastAPI(title="WaterForAll API", description="Backend API for WaterForAll")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running successfully"}

class ManualSubmissionRequest(BaseModel):
    params: dict[str, float]
    area_id: Optional[str] = None
    scenario: str = "custom"
    scenario_label: str = "Manual Entry"

@app.post("/cv/submissions")
def cv_submissions(req: ManualSubmissionRequest):
    # Construct a dummy request because we are bypassing CV for manual injection
    appearance_payload = WaterAppearancePayload(
        image_url="manual://",
        clarity_classification="clear",
        particle_detected=False,
        confidence_score=1.0,
    )
    
    strip_payload = WaterTestStripPayload(
        image_url="manual://",
        ph=req.params.get("ph"),
        chlorine_residual_ppm=req.params.get("chlorine_residual_ppm"),
        turbidity_ntu=req.params.get("turbidity_ntu"),
        nitrate_ppm=req.params.get("nitrate_ppm"),
        confidence_score=1.0,
    )
    
    wq_req = WaterQualityAnalysisRequest(
        user_id="manual_user",
        location=req.area_id,
        appearance=appearance_payload,
        test_strip=strip_payload
    )
    
    # Run the agent pipeline
    result = run_pipeline(
        request=wq_req,
        scenario=req.scenario,
        scenario_label=req.scenario_label,
        manual_overrides=req.params
    )
    
    return result

@app.post("/api/analyze")
async def analyze_photos(
    water_image: UploadFile = File(...),
    test_strip_image: Optional[UploadFile] = File(None),
    area_id: Optional[str] = Form(None)
):
    image_items = []
    
    # Only pass test strip image to process_submission if present
    # since submission_handler is designed to parse kits/meters.
    if test_strip_image:
        strip_bytes = await test_strip_image.read()
        image_items.append((strip_bytes, None))
    else:
        # fallback to passing water image if no strip provided
        water_bytes = await water_image.read()
        image_items.append((water_bytes, None))
        
    sub_res = process_submission(image_items, cv_provider="local")
    
    # Extract params from cv results
    params = {}
    strip_conf = 0.5 # Default low confidence if no parsing
    if sub_res.results:
        res = sub_res.results[0]
        strip_conf = res.overall_confidence
        for p in res.parameters:
            try:
                key = p.name.lower()
                val = float(p.estimated_value)
                if 'ph' in key:
                    params['ph'] = val
                elif 'chlorine' in key:
                    params['chlorine_residual_ppm'] = val
                elif 'turbidity' in key:
                    params['turbidity_ntu'] = val
                elif 'nitrate' in key:
                    params['nitrate_ppm'] = val
                elif 'nitrite' in key:
                    params['nitrite_ppm'] = val
                elif 'hardness' in key:
                    params['hardness_ppm'] = val
                elif 'iron' in key:
                    params['iron_ppm'] = val
            except Exception:
                pass

    appearance_payload = WaterAppearancePayload(
        image_url="uploaded://water",
        clarity_classification="clear",
        particle_detected=False,
        confidence_score=1.0,
    )
    
    strip_payload = WaterTestStripPayload(
        image_url="uploaded://strip",
        ph=params.get("ph"),
        chlorine_residual_ppm=params.get("chlorine_residual_ppm"),
        turbidity_ntu=params.get("turbidity_ntu"),
        nitrate_ppm=params.get("nitrate_ppm"),
        nitrite_ppm=params.get("nitrite_ppm"),
        hardness_ppm=params.get("hardness_ppm"),
        iron_ppm=params.get("iron_ppm"),
        confidence_score=strip_conf,
    )
    
    wq_req = WaterQualityAnalysisRequest(
        user_id="upload_user",
        location=area_id,
        appearance=appearance_payload,
        test_strip=strip_payload
    )
    
    result = run_pipeline(
        request=wq_req,
        scenario="custom",
        scenario_label="Photo Upload Analysis",
        manual_overrides=None
    )
    
    return result
