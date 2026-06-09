import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .cv.engine import analyse_test_strip, load_image
from .cv.classifier import classify_water_sample

_STATIC_DIR = Path(__file__).parent / "static"
_CV_PROVIDER = os.getenv("CV_PROVIDER", "local")

app = FastAPI(title="WaterForAll CV API", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(str(_STATIC_DIR / "index.html"))


@app.post("/analyze/test-strip")
async def analyze_test_strip_endpoint(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        if _CV_PROVIDER == "aws":
            from .cv.aws_provider import analyse_test_strip_rekognition
            result = analyse_test_strip_rekognition(raw)
        else:
            img = load_image(raw)
            result = analyse_test_strip(img)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return JSONResponse(result.model_dump())


@app.post("/analyze/water-sample")
async def analyze_water_sample_endpoint(file: UploadFile = File(...)):
    raw = await file.read()
    try:
        if _CV_PROVIDER == "aws":
            from .cv.aws_provider import classify_water_sample_rekognition
            result = classify_water_sample_rekognition(raw)
        else:
            img = load_image(raw)
            result = classify_water_sample(img)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return JSONResponse(result.model_dump())
