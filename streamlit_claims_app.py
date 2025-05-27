import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import os
import base64
import plotly.express as px

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Custom CSS with gold accent colors
def apply_dark_mode(dark_mode):
    if dark_mode:
        background_color = "#1E1E1E"
        text_color = "#F0F0F0"
        input_bg = "#2D2D2D"
        input_text = "#FFFFFF"
        primary_color = "#D4AF37"  # Gold color
        metric_text = "#D4AF37"
        border_color = "#444444"
    else:
        background_color = "#F8F9FA"
        text_color = "#212529"
        input_bg = "#FFFFFF"
        input_text = "#212529"
        primary_color = "#D4AF37"  # Gold color
        metric_text = "#D4AF37"
        border_color = "#DEE2E6"
    
    custom_css = f"""
    <style>
    :root {{
        --primary-color: {primary_color};
        --background-color: {background_color};
        --text-color: {text_color};
        --metric-text: {metric_text};
        --border-color: {border_color};
    }}
    
    body {{
        color: var(--text-color);
        background-color: var(--background-color);
        font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }}
    
    .stApp {{
        background-color: var(--background-color);
        color: var(--text-color);
    }}
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select,
    .stDateInput>div>div>input,
    .stSlider>div>div>div>div {{
        color: var(--input-text) !important;
        background-color: var(--input-bg) !important;
        border: 1px solid var(--border-color) !important;
    }}
    
    /* Metrics */
    .metric-container {{
        background-color: {'rgba(33, 37, 41, 0.05)' if not dark_mode else 'rgba(255, 255, 255, 0.05)'};
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        border: 1px solid var(--border-color);
    }}
    
    .metric-container h2 {{
        color: var(--metric-text) !important;
        font-weight: 600;
        font-size: 1.5rem;
        margin-bottom: 0;
    }}
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: var(--primary-color) !important;
    }}
    
    h1 {{
        font-weight: 700 !important;
    }}
    
    /* Form labels */
    .stForm label {{
        color: var(--text-color) !important;
        font-weight: 500;
    }}
    
    /* Buttons */
    .stButton>button {{
        background-color: var(--primary-color) !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 500;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    return primary_color

# Background image function
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
        background-color: rgba(0, 0, 0, {0.5 if st.session_state.dark_mode else 0.2});
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Toggle dark mode
def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Configure page
st.set_page_config(
    page_title="🩺 Insurance Claim Predictor", 
    layout="centered",
    page_icon="🩺"
)

# Apply theme and background
primary_color = apply_dark_mode(st.session_state.dark_mode)
set_background("insurance_bg.jpg")

# Sidebar with dark mode toggle
with st.sidebar:
    st.title("Settings")
    st.toggle("🌙 Dark Mode", 
              value=st.session_state.dark_mode, 
              on_change=toggle_dark_mode,
              key="dark_mode_toggle")
    
    st.markdown("---")
    st.info("""
    **Instructions:**
    1. Fill in patient details
    2. Enter claim information
    3. Click 'Predict Claim Amount'
    """)

# Main app
st.title("🩺 Insurance Claim Prediction")
st.markdown("Predict the claim amount based on patient and claim details.")

with st.form("claim_form", clear_on_submit=False):
    st.subheader("👤 Patient Information")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=40, step=1)
        income = st.number_input("Annual Income ($)", min_value=0, value=50000, step=1000)
        gender = st.selectbox("Gender", ["M", "F"], index=0)

    with col2:
        marital_status = st.selectbox("Marital Status", 
                                    ["Married", "Single", "Divorced", "Widowed"],
                                    index=0)
        employment_status = st.selectbox("Employment Status", 
                                       ["Employed", "Unemployed", "Retired", "Student"],
                                       index=0)
        claim_date = st.date_input("Claim Date", value=datetime.today())

    st.subheader("🏥 Claim Details")
    col3, col4 = st.columns(2)

    with col3:
        claim_type = st.selectbox("Claim Type", 
                                ["Routine", "Emergency", "Inpatient", "Outpatient"],
                                index=0)
        claim_status = st.selectbox("Claim Status", 
                                  ["Pending", "Approved", "Denied"],
                                  index=0)
        submission_method = st.selectbox("Submission Method", 
                                       ["Online", "Paper", "Phone"],
                                       index=0)

    with col4:
        specialty = st.selectbox("Provider Specialty", [
            "General Practice", "Cardiology", "Pediatrics", "Neurology", "Orthopedics"
        ], index=0)
        location = st.text_input("Provider Location", value="New York")
        st.write("")  # Spacer

    st.subheader("📝 Clinical Information")
    col5, col6 = st.columns(2)

    with col5:
        procedure_code = st.text_input("Procedure Code (e.g., HC219)", 
                                     value="HC219", 
                                     max_chars=5,
                                     help="Format: 2 letters followed by 3 numbers").upper()
    with col6:
        diagnosis_code = st.text_input("Diagnosis Code (e.g., HC219)", 
                                     value="HC219", 
                                     max_chars=5,
                                     help="Format: 2 letters followed by 3 numbers").upper()

    submitted = st.form_submit_button("🔍 Predict Claim Amount", use_container_width=True)

if submitted:
    # Validate input codes
    code_error = False
    if not (len(procedure_code) == 5 and procedure_code[:2].isalpha() and procedure_code[2:].isdigit()):
        st.error("Procedure code must be in format AA999 (2 letters, 3 numbers)")
        code_error = True
    if not (len(diagnosis_code) == 5 and diagnosis_code[:2].isalpha() and diagnosis_code[2:].isdigit()):
        st.error("Diagnosis code must be in format AA999 (2 letters, 3 numbers)")
        code_error = True
    
    if not code_error:
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

        API_URL = os.getenv("API_URL", "http://localhost:8000")

        with st.spinner("Predicting claim amount..."):
            try:
                response = requests.post(
                    f"{API_URL}/predict/", 
                    json=input_data, 
                    timeout=10
                )
                result = response.json()

                if response.status_code == 200 and result["status"] == "success":
                    preds = result["predictions"]
                    
                    st.success("✅ Prediction successful!")
                    st.balloons()
                    
                    # Display predictions in gold color
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        with st.container():
                            st.markdown("**Time-Series Prediction**")
                            st.markdown(f"<h2 style='color: #D4AF37;'>{preds['prophet']:,.2f}</h2>", 
                                        unsafe_allow_html=True)
                    with col2:
                        with st.container():
                            st.markdown("**Residual Adjustment**")
                            st.markdown(f"<h2 style='color: #D4AF37;'>{preds['residual']:,.2f}</h2>", 
                                        unsafe_allow_html=True)
                    with col3:
                        with st.container():
                            st.markdown("**Final Prediction**")
                            st.markdown(f"<h2 style='color: #D4AF37;'>{preds['final']:,.2f}</h2>", 
                                        unsafe_allow_html=True)

                    # Create pie chart of the ratio
                    pie_data = pd.DataFrame({
                        "Component": ["Time-Series", "Residual"],
                        "Value": [preds["prophet"], abs(preds["residual"])]
                    })
                    
                    fig = px.pie(
                        pie_data,
                        values="Value",
                        names="Component",
                        color_discrete_sequence=["#1a73e8", "#D4AF37"],  # Deep blue and gold
                        hole=0.3,
                        title="Prediction Components Ratio"
                    )
                    
                    # Update layout for transparent background
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color=st.session_state.dark_mode and "#F0F0F0" or "#212529",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.error(f"❌ Error: {result.get('message', 'Unknown error')}")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection error: {str(e)}")
                st.info(f"Please ensure the backend API is running at {API_URL}")