import streamlit as st
import requests
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

st.set_page_config(page_title="Water Potability Dashboard", layout="wide")

st.title("💧 Water Potability Prediction Dashboard")

# Auth form toggler
if "token" not in st.session_state:
    auth_mode = st.radio("Choose an option:", ["Login", "Register"])

    username = st.text_input("Username", max_chars=50)
    password = st.text_input("Password", type="password", max_chars=50)

    if auth_mode == "Register":
        email = st.text_input("Email", max_chars=100)

    if st.button(auth_mode):
        if not username or not password or (auth_mode == "Register" and not email):
            st.warning("Please fill all required fields.")
        else:
            if auth_mode == "Login":
                # Login API call
                response = requests.post(
                    "http://localhost:8000/token",
                    data={"username": username, "password": password},
                )
                if response.status_code == 200:
                    st.session_state.token = response.json()["access_token"]
                    st.success("Logged in successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Login failed. Check your username/password.")
            else:
                # Register API call
                response = requests.post(
                    "http://localhost:8000/register",
                    json={"username": username, "password": password, "email": email},
                )
                if response.status_code == 201:
                    st.success("Registration successful! Please login now.")
                else:
                    st.error(f"Registration failed: {response.json().get('detail', response.text)}")

else:
    st.sidebar.title("Actions")
    menu = st.sidebar.radio("Navigate", ["Upload & Predict", "Explain", "Monitor Drift", "Logout"])

    if menu == "Logout":
        st.session_state.pop("token")
        st.experimental_rerun()

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    if menu == "Upload & Predict":
        st.header("📤 Upload Water Quality CSV Data")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("### Sample Data Preview", df.head())

                if st.button("Predict Potability"):
                    data = {"data": df.to_dict(orient="records")}
                    with st.spinner("Predicting..."):
                        response = requests.post(
                            "http://localhost:8000/predict",
                            json=data,
                            headers=headers,
                        )
                    if response.status_code == 200:
                        preds = response.json().get("predictions", [])
                        df["Predicted_Potability"] = preds
                        st.success("Prediction complete!")
                        st.dataframe(df)
                    else:
                        st.error(f"Prediction failed: {response.text}")

            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

    elif menu == "Explain":
        st.header("🧮 SHAP Explanation for Predictions")
        uploaded_file = st.file_uploader("Upload CSV for explanation", type=["csv"], key="explain")

        if uploaded_file:
            try:
                df_exp = pd.read_csv(uploaded_file)
                st.write("### Data Preview", df_exp.head())

                if st.button("Explain Predictions"):
                    data = {"data": df_exp.to_dict(orient="records")}
                    with st.spinner("Generating explanations..."):
                        response = requests.post(
                            "http://localhost:8000/explain",
                            json=data,
                            headers=headers,
                        )
                    if response.status_code == 200:
                        shap_vals = response.json().get("explanations", [])
                        if shap_vals:
                            shap_values = np.array(shap_vals)
                            st.subheader("SHAP Feature Importance (Summary)")

                            fig, ax = plt.subplots(figsize=(10, 6))
                            shap.summary_plot(
                                shap_values, 
                                pd.DataFrame(df_exp), 
                                plot_type="bar", 
                                show=False
                            )
                            st.pyplot(fig)
                        else:
                            st.warning("No SHAP values received.")
                    else:
                        st.error(f"Explanation failed: {response.text}")

            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

    elif menu == "Monitor Drift":
        st.header("📈 Model Drift Monitoring")
        st.info("Real-time IoT data integration and drift monitoring coming soon.")
