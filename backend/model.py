# model.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import pandas as pd
import joblib
from auth import get_current_user
from datetime import datetime
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

router = APIRouter()

# Load the ML model
try:
    model = joblib.load("water_quality_model.pkl")
except FileNotFoundError:
    raise FileNotFoundError("water_quality_model.pkl not found. Please ensure the model file exists.")

# MongoDB setup
client = MongoClient(MONGODB_URI)
db = client["water_api"]
reports = db["reports"]

@router.post("/predict")
async def predict(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read and validate CSV
        df = pd.read_csv(file.file)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Make predictions (remove Potability column if it exists)
        feature_df = df.drop("Potability", axis=1, errors="ignore")
        
        # Validate that we have the required features
        if feature_df.empty:
            raise HTTPException(status_code=400, detail="No valid features found in CSV")
        
        preds = model.predict(feature_df)

        # Store report in MongoDB
        report = {
            "username": user["username"],
            "timestamp": datetime.now().isoformat(),
            "filename": file.filename,
            "predictions": preds.tolist(),
            "num_samples": len(preds)
        }
        
        result = reports.insert_one(report)
        
        return {
            "message": "✅ Prediction complete", 
            "predictions": preds.tolist(),
            "num_samples": len(preds),
            "report_id": str(result.inserted_id)
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty or corrupted")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/reports")
async def get_reports(user: dict = Depends(get_current_user)):
    """Get all reports for the current user"""
    try:
        user_reports = list(reports.find(
            {"username": user["username"]}, 
            {"_id": 0}  # Exclude MongoDB _id field
        ).sort("timestamp", -1))  # Sort by newest first
        
        return {
            "message": "✅ Reports retrieved successfully",
            "reports": user_reports,
            "total_reports": len(user_reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reports: {str(e)}")

@router.get("/reports/{report_id}")
async def get_report(report_id: str, user: dict = Depends(get_current_user)):
    """Get a specific report by ID"""
    try:
        from bson import ObjectId
        
        report = reports.find_one({
            "_id": ObjectId(report_id),
            "username": user["username"]
        })
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Convert ObjectId to string for JSON serialization
        report["_id"] = str(report["_id"])
        
        return {
            "message": "✅ Report retrieved successfully",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")

@router.post("/explain")
async def explain(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        df = pd.read_csv(file.file)
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        feature_df = df.drop("Potability", axis=1, errors="ignore")
        shap_values = model.explain_prediction(feature_df)
        return {"message": "✅ Explanation complete", "explanations": shap_values.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")
