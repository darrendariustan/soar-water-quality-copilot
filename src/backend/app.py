from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from schemas import WaterQualityAnalysisRequest, WaterAppearancePayload, WaterTestStripPayload
from agents.master_agent import run_pipeline
from agents.schemas import WaterTestResult
from cv.submission_handler import process_submission
from cv.classifier import classify_water_sample
from cv.engine import load_image
import os
import uuid
from datetime import datetime, timezone
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
        nitrite_ppm=req.params.get("nitrite_ppm"),
        hardness_ppm=req.params.get("hardness_ppm"),
        iron_ppm=req.params.get("iron_ppm"),
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

class ChatMessageRequest(BaseModel):
    message: str
    history: Optional[list[dict]] = None
    scenario: Optional[str] = None
    result_id: Optional[str] = None
    context: Optional[dict] = None

from fastapi.responses import StreamingResponse
import json
from agents.chat_agent import get_chat_agent

@app.post("/api/chat/stream")
async def chat_stream(req: ChatMessageRequest):
    context_str = ""
    if req.context:
        context_str = f"\n\nCURRENT DASHBOARD CONTEXT:\n{json.dumps(req.context, indent=2)}\n\n"
        
    system_prompt = (
        "You are an agentic water safety educator. Answer the user's questions about water safety in plain language. "
        "Keep it to a maximum of 4 short, actionable sentences. No emojis. "
        "You have access to tools to search for guidelines, web searches, or community risk trends if the user asks something outside the current dashboard context. "
        "If the user asks you to modify or update the dashboard parameters (e.g. pH, turbidity, chlorine), "
        "you MUST append a command block to the VERY END of your response in this exact format: "
        "[UPDATE_PARAMS: {\"parameter_name\": value}]. "
        "Use valid JSON inside the brackets. Available keys: ph, chlorine_residual_ppm, turbidity_ntu, nitrate_ppm, nitrite_ppm, hardness_ppm, iron_ppm."
        f"{context_str}"
    )
    
    async def generate():
        try:
            agent = get_chat_agent(system_prompt)
            messages = req.history or []
            messages.append({"role": "user", "content": req.message})
            
            async for event in agent.astream_events({"messages": messages}, version="v2"):
                if event["event"] == "on_chat_model_stream":
                    if event["metadata"].get("langgraph_node") == "agent":
                        chunk = event["data"]["chunk"]
                        if chunk.content and not chunk.tool_call_chunks:
                            text = chunk.content if isinstance(chunk.content, str) else str(chunk.content)
                            yield f"data: {json.dumps({'text': text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'LLM is currently unavailable: {e}'})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

_CLARITY_LABEL = {"clear": "Clear", "cloudy": "Cloudy", "colored": "Colored", "contaminated": "Cloudy"}


def _classify_appearance(water_bytes: bytes):
    """Visual-only appearance from the water photo. Returns (ui_appearance, particle_detected, confidence)."""
    sample = classify_water_sample(load_image(water_bytes))
    a = sample.appearance
    if a.visible_particles or a.clarity == "opaque":
        ui = "contaminated"
    elif a.colour != "colourless":
        ui = "colored"
    elif a.clarity in ("cloudy", "slightly_cloudy"):
        ui = "cloudy"
    else:
        ui = "clear"
    return ui, a.visible_particles, round(sample.overall_confidence, 3)


@app.post("/api/analyze")
async def analyze_photos(
    water_image: UploadFile = File(...),
    test_strip_images: Optional[list[UploadFile]] = File(None),
    area_id: Optional[str] = Form(None)
):
    water_bytes = await water_image.read()
    ui_appearance, particles, appearance_conf = _classify_appearance(water_bytes)

    strips = test_strip_images or []

    # No test kit: a photo cannot measure chemical parameters, so we report a
    # visual-only screen instead of inferring pH/chlorine/nitrate/etc.
    if not strips:
        if ui_appearance == "clear":
            risk = "unknown"
            summary = (
                "The water looks clear, but a photo cannot measure chemical safety. "
                "Use a test strip or seek laboratory testing to confirm."
            )
            warnings = []
        else:
            risk = "caution"
            summary = (
                f"The water appears {ui_appearance}. Appearance alone cannot confirm safety, "
                "so do not assume it is safe to drink."
            )
            warnings = [
                "Discoloured or cloudy water can indicate sediment, iron or chemical "
                "contamination. Boiling does not remove chemicals or metals."
            ]
        return WaterTestResult(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            scenario="custom",
            scenarioLabel="Photo Upload Analysis (visual only)",
            waterAppearance=ui_appearance,
            overallRisk=risk,
            confidence=appearance_conf,
            summary=summary,
            parameters=[],
            recommendations=[
                "A photo cannot measure pH, chlorine, nitrate, nitrite, hardness or iron. Use a test strip for those readings.",
                "Let the water settle, then filter it through a clean cloth or household filter.",
                "Seek a proper water test before drinking, especially if the water is discoloured or cloudy.",
            ],
            warnings=warnings,
            sources=["World Health Organization: Guidelines for Drinking-water Quality, 4th edition"],
        )

    # One or more test kit images provided: classify each kit, read it, and merge
    # the standard parameter readings across all images. Up to 3 images supported.
    image_items = []
    for s in strips[:3]:
        image_items.append((await s.read(), None))
    sub_res = process_submission(image_items, cv_provider=os.getenv("CV_PROVIDER", "local"))

    params = {}
    kit_types = []
    confidences = []
    for res in sub_res.results:
        kit_types.append(res.kit_type)
        confidences.append(res.overall_confidence)
        for p in res.parameters:
            try:
                key = p.name.lower()
                val = float(p.estimated_value)
            except (TypeError, ValueError):
                continue
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
    strip_conf = max(confidences) if confidences else 0.5

    appearance_payload = WaterAppearancePayload(
        image_url="uploaded://water",
        clarity_classification=_CLARITY_LABEL.get(ui_appearance, "Clear"),
        particle_detected=particles,
        confidence_score=appearance_conf,
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
        test_strip=strip_payload,
    )
    return run_pipeline(
        request=wq_req,
        scenario="custom",
        scenario_label="Photo Upload Analysis",
        manual_overrides=None,
    )
