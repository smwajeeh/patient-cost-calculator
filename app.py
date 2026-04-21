import streamlit as st
import pandas as pd
import math
import re
from datetime import date

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Treatment Cost Calculator", layout="wide")

# -------------------------
# CLEAN PROFESSIONAL THEME
# -------------------------
st.markdown("""
<style>

/* Background */
body {
    background-color: #F9FAFB;
}

/* Header */
.header {
    background-color: #6B7F4E;
    padding: 15px;
    border-radius: 8px;
    color: white;
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 20px;
}

/* Card */
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/* Section titles */
h2, h3 {
    color: #111827;
}

/* Button */
.stButton>button {
    background-color: #6B7F4E;
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
}

/* Metrics */
.stMetric {
    background-color: #F3F4F6;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown('<div class="header">💊 Patient Treatment Cost Calculator</div>', unsafe_allow_html=True)

# -------------------------
# HELPERS
# -------------------------
def extract_number(value):
    try:
        if pd.isna(value):
            return None
        number = re.findall(r"[\d\.]+", str(value))
        return float(number[0]) if number else None
    except:
        return None

def format_date_us(d):
    try:
        return d.strftime("%m-%d-%Y")
    except:
        return ""

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel("drug_data.xlsx")
df.columns = df.columns.str.strip()
df = df.dropna(subset=["Drug_Name"])

base_columns = ["J_Code", "Drug_Name", "Billing_Unit", "Cost_per_Unit"]
payer_columns = sorted([col for col in df.columns if col not in base_columns])

# -------------------------
# PATIENT INFO + INSURANCE (TOP ROW)
# -------------------------
colA, colB = st.columns(2)

with colA:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧑 Patient Information")

    patient_name = st.text_input("Patient Name")

    dob = st.date_input(
        "Date of Birth",
        min_value=date.today().replace(year=date.today().year - 100),
        max_value=date.today()
    )

    doctor = st.text_input("Doctor Name")

    treatment_date = st.date_input("Date of Treatment", value=date.today())

    location = st.selectbox(
        "Clinic Location",
        ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"]
    )

    st.markdown('</div>', unsafe_allow_html=True)

with colB:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🏥 Insurance")

    payer = st.selectbox("Primary Insurance", payer_columns)
    primary_coverage = st.slider("Primary Coverage %", 0, 100, 80) / 100

    has_secondary = st.checkbox("Has Secondary Insurance")

    secondary_coverage = 0

    if has_secondary:
        secondary_dropdown = st.selectbox("Secondary Insurance", payer_columns)
        secondary_text = st.text_input("Or Enter Secondary Insurance")
        secondary_coverage = st.slider("Secondary Coverage %", 0, 100, 20) / 100

    copay = st.number_input("Copay ($)", min_value=0.0)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# MEDICATIONS
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("💉 Medications")

num_drugs = st.number_input("Number of Drugs", 1, 10, 1)

drug_entries = []

for i in range(int(num_drugs)):
    col1, col2, col3 = st.columns(3)

    with col1:
        drug = st.selectbox(f"Drug {i+1}", df["Drug_Name"].unique(), key=f"d{i}")

    with col2:
        dose = st.number_input(f"Dose {i+1}", min_value=0.0, key=f"dose{i}")

    with col3:
        unit = st.selectbox(f"Unit {i+1}", ["mg", "mcg"], key=f"u{i}")

    drug_entries.append({"drug": drug, "dose": dose})

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# CALCULATE BUTTON
# -------------------------
if st.button("Calculate Treatment Cost"):

    total_cost = 0
    total_allowed = 0

    for entry in drug_entries:
        drug_data = df[df["Drug_Name"] == entry["drug"]].iloc[0]

        billing_unit = extract_number(drug_data["Billing_Unit"])
        cost = extract_number(drug_data["Cost_per_Unit"])
        allowable = extract_number(drug_data[payer])
        dose_val = extract_number(entry["dose"])

        units = math.ceil(dose_val / billing_unit)

        total_cost += units * cost
        total_allowed += units * allowable

    primary_payment = total_allowed * primary_coverage
    remaining = total_allowed - primary_payment

    if has_secondary:
        secondary_payment = remaining * secondary_coverage
        patient = remaining - secondary_payment + copay
    else:
        secondary_payment = 0
        patient = remaining + copay

    # -------------------------
    # RESULTS (DASHBOARD STYLE)
    # -------------------------
    st.subheader("💰 Financial Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cost", f"${total_cost:,.2f}")
    col2.metric("Primary Pays", f"${primary_payment:,.2f}")
    col3.metric("Patient Pays", f"${patient:,.2f}")

    if has_secondary:
        st.metric("Secondary Pays", f"${secondary_payment:,.2f}")
    else:
        st.info(f"Patient responsible for remaining: ${remaining:,.2f}")
