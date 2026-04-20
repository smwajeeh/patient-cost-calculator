import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Treatment Cost Calculator", layout="centered")

st.title("💊 Patient Treatment Cost Calculator")

# Load Drug Data
try:
    df = pd.read_excel("drug_data.xlsx")
except:
    st.error("❌ drug_data.xlsx not found. Please upload it to your repository.")
    st.stop()

# -------------------------
# Patient Info
# -------------------------
st.subheader("🧑 Patient & Treatment Info")

col1, col2 = st.columns(2)

with col1:
    patient_name = st.text_input("Patient Name")
    dob = st.date_input("Date of Birth")

with col2:
    doctor = st.text_input("Doctor Name")
    location = st.text_input("Clinic Location")

# -------------------------
# Drug Selection
# -------------------------
st.subheader("💉 Drug Information")

drug = st.selectbox("Select Drug", df["Drug_Name"].unique())
dose = st.number_input("Dose (mg / mcg / units)", min_value=0.0)

drug_data = df[df["Drug_Name"] == drug].iloc[0]

cost_per_unit = drug_data["Cost_per_Unit"]
reimbursement_per_unit = drug_data["Reimbursement_per_Unit"]

# -------------------------
# Insurance Info
# -------------------------
st.subheader("🏥 Insurance Information")

primary_coverage = st.slider("Primary Coverage %", 0, 100, 80) / 100

has_secondary = st.checkbox("Has Secondary Insurance")

secondary_coverage = 0
if has_secondary:
    secondary_coverage = st.slider("Secondary Coverage %", 0, 100, 20) / 100

copay = st.number_input("Copay ($)", min_value=0.0)

# -------------------------
# Calculate
# -------------------------
if st.button("Calculate"):

    if dose <= 0:
        st.error("❌ Dose must be greater than 0")
        st.stop()

    # Calculations
    total_cost = dose * cost_per_unit
    allowed = dose * reimbursement_per_unit

    primary_payment = allowed * primary_coverage
    remaining = allowed - primary_payment

    secondary_payment = remaining * secondary_coverage
    patient_responsibility = remaining - secondary_payment + copay

    # -------------------------
    # Results
    # -------------------------
    st.subheader("💰 Financial Breakdown")

    st.metric("Total Drug Cost", f"${total_cost:,.2f}")
    st.metric("Allowed Amount", f"${allowed:,.2f}")
    st.metric("Primary Insurance Pays", f"${primary_payment:,.2f}")
    st.metric("Secondary Insurance Pays", f"${secondary_payment:,.2f}")
    st.metric("Patient Responsibility", f"${patient_responsibility:,.2f}")

    # -------------------------
    # Summary
    # -------------------------
    st.subheader("🧾 Summary")

    st.write(f"""
    Total treatment cost is **${total_cost:,.2f}**.

    Insurance allows **${allowed:,.2f}** for this treatment.

    Primary insurance covers **{primary_coverage*100:.0f}%** and pays **${primary_payment:,.2f}**.
    """)

    if has_secondary:
        st.write(f"Secondary insurance pays **${secondary_payment:,.2f}**.")

    st.write(f"""
    The patient is responsible for **${patient_responsibility:,.2f}**, including any copay.
    """)

    # -------------------------
    # Patient Info Display
    # -------------------------
    st.subheader("📋 Patient Record")

    st.write(f"""
    **Patient:** {patient_name}  
    **DOB:** {dob}  
    **Doctor:** {doctor}  
    **Location:** {location}  
    **Drug:** {drug}  
    **Dose:** {dose}  
    """)
