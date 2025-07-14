# 🌊 Water Quality AI API and Dashboard

## Overview

The **Water Quality AI API and Dashboard** is a full-stack application designed to predict water potability using a machine learning model, provide real-time data monitoring, and offer interpretability through SHAP explanations. The system integrates a FastAPI backend with MongoDB for data storage, a Streamlit frontend for user interaction, and MQTT for potential integration with IoT devices. It supports user authentication, CSV-based predictions, report management, and model drift monitoring.

## Features

- **Authentication**: Secure user registration and login using JWT-based OAuth2 authentication with bcrypt password hashing.
- **Prediction**: Upload CSV files containing water quality data to predict potability using a pre-trained machine learning model (`EnhancedWaterQualityPredictor`).
- **Report Management**: Store and retrieve prediction reports in MongoDB, accessible only to authenticated users.
- **Drift Monitoring**: Placeholder for real-time IoT data integration via MQTT and model drift detection.
- **Interpretability**: SHAP-based feature importance explanations for predictions (note: the `/explain` endpoint is referenced but not implemented in the provided code).
- **User Interface**: A responsive Streamlit dashboard for uploading data, viewing predictions, and monitoring drift, styled with custom CSS.

## Project Structure

```
 ├──frontend/
      ├── app.py                 # Streamlit frontend for the dashboard
      ├── style.css              # Custom CSS for Streamlit dashboard
      ├── requirements.txt       # Frontend dependencies (Streamlit-specific)
 ├──backend/
      ├── main.py                # FastAPI main application with CORS and router setup
      ├── model.py               # FastAPI prediction and report management endpoints
      ├── monitor.py             # FastAPI drift monitoring endpoint and MQTT setup
      ├── requirements.txt       # Backend dependencies
      ├── auth.py                # FastAPI authentication endpoints (register, login)
      ├── .env                   # Environment variables (MongoDB URI, Secret Key)
      └── water_quality_model.pkl # Pre-trained machine learning model 
```

## Prerequisites

- Python 3.11+
- MongoDB Atlas or local MongoDB instance
- MQTT broker (e.g., `mqtt.eclipseprojects.io` for testing)
- Pre-trained `water_quality_model.pkl` (generated from `EnhancedWaterQualityPredictor`)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone <repository_url>
   cd water-quality-ai
   ```

2. **Install Dependencies**:

   - Backend:

     ```bash
     pip install -r requirements.txt
     ```
   - Frontend (Streamlit):

     ```bash
     pip install -r requirements.txt  # Second requirements.txt for Streamlit
     ```

3. **Set Up Environment Variables**:

   - Create a `.env` file in the root directory with the following:

     ```plaintext
     MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
     SECRET_KEY=<your_secret_key>
     ```
   - Replace `<username>`, `<password>`, `<cluster>`, and `<your_secret_key>` with your MongoDB credentials and a secure JWT secret key.

4. **Ensure Model Availability**:

   - Place the pre-trained `water_quality_model.pkl` in the project root directory. This file should be generated using the `EnhancedWaterQualityPredictor` class.

## Running the Application

1. **Start the FastAPI Backend**:

   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`. Use tools like Postman or curl to test endpoints.

2. **Start the Streamlit Frontend**:

   ```bash
   streamlit run app.py
   ```

   The dashboard will be available at `http://localhost:8501`.

## Usage

### 1. Authentication

- **Register**: Use the Streamlit dashboard to create a new account by providing a username, password, and email.
- **Login**: Log in with your credentials to obtain a JWT token, stored in `st.session_state.token`.
- **Logout**: Clear the session token via the sidebar.

### 2. Prediction

- Navigate to "Upload & Predict" in the Streamlit dashboard.
- Upload a CSV file with water quality features (e.g., pH, Hardness, Solids, etc.).
- Click "Predict Potability" to generate predictions and store results in MongoDB.
- View predictions in the dashboard and retrieve report IDs for later access.

### 3. Report Management

- Access all reports for the logged-in user via "Reports" (not explicitly shown in the dashboard but available via API).
- Retrieve a specific report by ID using the `/reports/{report_id}` endpoint.

### 4. Drift Monitoring

- Access the "Monitor Drift" section for a placeholder drift metric (random value for demonstration).
- The system is set up to receive IoT data via MQTT, but drift checks are not fully implemented.

### 5. SHAP Explanations

- The dashboard references an `/explain` endpoint for SHAP explanations, but this is not implemented in `model.py`. To add this functionality, implement the endpoint using the `explain_prediction` method from `EnhancedWaterQualityPredictor`.

## API Endpoints

- **Authentication** (`/auth`):
  - `POST /register`: Register a new user.
  - `POST /token`: Obtain a JWT token for login.
- **Prediction** (`/model`):
  - `POST /predict`: Predict water potability from a CSV file.
  - `GET /reports`: Retrieve all reports for the authenticated user.
  - `GET /reports/{report_id}`: Retrieve a specific report by ID.
- **Monitoring** (`/monitor`):
  - `GET /drift`: Check model drift status (placeholder).

## Known Issues and Improvements

1. **Missing** `/explain` **Endpoint**:

   - The Streamlit dashboard references a `POST /explain` endpoint, but it is not implemented in `model.py`. To fix, add:

     ```python
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
     ```
   - Ensure `water_quality_model.pkl` is compatible with the `explain_prediction` method from `EnhancedWaterQualityPredictor`.

2. **Drift Monitoring Placeholder**:

   - The `/drift` endpoint returns a random metric. Implement actual drift detection using statistical tests (e.g., KS test) or drift detection libraries (e.g., Alibi Detect) with IoT data from MQTT.

3. **Duplicate** `requirements.txt`:

   - There are two `requirements.txt` files (backend and frontend). Consider merging them or clearly separating backend and frontend dependencies in documentation.

4. **Security**:

   - The `.env` file contains sensitive credentials. Ensure it is not exposed in version control (add to `.gitignore`).
   - The CORS middleware allows all origins (`allow_origins=["*"]`). Restrict to specific origins in production.

5. **Error Handling**: Juno

   - Enhance error messages in the Streamlit dashboard and API for better user feedback.

## Dependencies

- **Backend**: FastAPI, Uvicorn, Pandas, Joblib, Pymongo, Bcrypt, Python-dotenv, Paho-mqtt, Numpy, Scikit-learn, Imbalanced-learn, Optuna, XGBoost, LightGBM, SHAP, Passlib, Jose, JWT.
- **Frontend**: Streamlit, Requests, Pandas, Numpy, Matplotlib, SHAP.

## Future Enhancements

- Implement the `/explain` endpoint for SHAP explanations.
- Add real-time drift detection using IoT data.
- Enhance the Streamlit dashboard with interactive visualizations (e.g., detailed report views).
- Add data validation for CSV uploads to ensure required features are present.
- Implement rate limiting and additional security measures for the API.

## License

This project is licensed under the MIT License.
