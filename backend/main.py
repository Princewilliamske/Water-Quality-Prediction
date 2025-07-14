# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from auth import router as auth_router
from model import router as model_router
from monitor import router as monitor_router

app = FastAPI(
    title="🌊 Water Quality AI API",
    description="API with authentication, prediction, and drift monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(model_router, prefix="/model", tags=["Prediction"])
app.include_router(monitor_router, prefix="/monitor", tags=["Monitoring"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
