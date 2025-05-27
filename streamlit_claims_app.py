import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import os
import streamlit as st
import base64

# Background image and theme toggle
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def set_theme(dark: bool):
    theme = "dark" if dark else "light"
    st.markdown(
        f"""
        <style>
        body {{
            color: {'white' if dark else 'black'};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


st.set_page_config(page_title="🩺 Insurance Claim Predictor", layout="centered")

# Theme and background
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
set_theme(dark_mode)
set_background("insurance_bg.jpg")  # Add your image to the project root


st.title("🩺 Insurance Claim Prediction")
st.markdown("Predict the claim amount based on patient and claim details.")

with st.form("claim_form", clear_on_submit=False):
    st.subheader("👤 Patient Information")
    col1, col2 = st.columns(2)

    with col1:
        age = st.slider("Age", 0, 120, 40)
        income = st.number_input("Annual Income ($)", min_value=0, value=50000)
        gender = st.selectbox("Gender", ["M", "F"])
        marital_status = st.selectbox("Marital Status", ["Married", "Single", "Divorced", "Widowed"])
        employment_status = st.selectbox("Patient Employment Status", ["Retired", "Student", "Employed", "Unemployed"])

    with col2:
        claim_date = st.date_input("Claim Date", value=datetime.today())
        claim_type = st.selectbox("Claim Type", ["Routine", "Emergency", "Inpatient", "Outpatient"])
        claim_status = st.selectbox("Claim Status", ["Pending", "Approved", "Denied"])
        submission_method = st.selectbox("Submission Method", ["Paper", "Online", "Phone"])
        location = st.text_input("Provider Location", value="New York")

    st.subheader("🏥 Clinical & Provider Info")
    col3, col4 = st.columns(2)

    with col3:
        procedure_code = st.text_input("Procedure Code (e.g., Hc219)", value="Hc219")
        diagnosis_code = st.text_input("Diagnosis Code (e.g., Hc219)", value="Hc219")

    with col4:
        specialty = st.selectbox("Provider Specialty", [
            "Cardiology", "Pediatrics", "Neurology", "General Practice", "Orthopedics"
        ])

    submitted = st.form_submit_button("🔍 Predict Claim Amount")

if submitted:
    input_data = {
        "PatientAge": float(age),
        "PatientIncome": float(income),
        "PatientGender": gender,
        "PatientMaritalStatus": marital_status,
        "ClaimType": claim_type,
        "PatientEmploymentStatus": employment_status,
        "ClaimDate": claim_date.strftime("%Y-%m-%d"),
        "DiagnosisCode": diagnosis_code,
        "ProcedureCode": procedure_code,
        "ProviderSpecialty": specialty,
        "ClaimStatus": claim_status,
        "ProviderLocation": location,
        "ClaimSubmissionMethod": submission_method
    }

     #Get the API URL from environment variable with a fallback to localhost
    API_URL = os.getenv("API_URL", "http://localhost:8000")

    try:
        response = requests.post(f"{API_URL}/predict/", json=input_data)
        result = response.json()

        if response.status_code == 200 and result["status"] == "success":
            preds = result["predictions"]
            st.success("✅ Prediction successful!")
            st.metric("📈 Time-Series Prediction", f"${preds['prophet']:,.2f}")
            st.metric("🔧 Residual Adjustment", f"${preds['residual']:,.2f}")
            st.metric("💰 Final Prediction", f"${preds['final']:,.2f}")

            # Optional: Chart
            st.bar_chart(pd.DataFrame({
                "Component": ["Prophet", "Residual", "Final"],
                "Amount": [preds["prophet"], preds["residual"], preds["final"]]
            }).set_index("Component"))

        else:
            st.error(f"❌ Error: {result.get('message', 'Unknown error')}")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection error: {e}")
