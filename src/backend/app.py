from fastapi import FastAPI

app = FastAPI(title="WaterForAll API", description="Backend API for WaterForAll")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running successfully"}
