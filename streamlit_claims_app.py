import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="🩺 Insurance Claim Predictor", layout="centered")

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

    try:
        response = requests.post("http://localhost:8000/predict/", json=input_data)
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
