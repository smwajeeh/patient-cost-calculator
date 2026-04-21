import streamlit as st
import pandas as pd
import math
import re
from datetime import date

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Treatment Cost Calculator", layout="centered")

# -------------------------
# THEME (Based on your image)
# -------------------------
st.markdown("""
<style>

/* Background */
body {
    background-color: #f3f4f6;
}

/* Top bar */
.topbar {
    background-color: #8b9a77;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-weight: 600;
    margin-bottom: 30px;
}

/* Main Card */
.main-card {
    background-color: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
}

/* Headers */
h1 {
    color: #2f3e46;
    text-align: center;
}

h2, h3 {
    color: #344e41;
}

/* Inputs */
.stTextInput, .stNumberInput, .stSelectbox {
    background-color: #f9fafb;
}

/* Button */
.stButton>button {
    background-color: #6b7f4e;
    color: white;
    border-radius: 10px;
    height: 45px;
    width: 100%;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #55663c;
}

/* Metrics */
.stMetric {
    background-color: #f9fafb;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
}

/* Section spacing */
.section {
    margin-top: 25px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER BAR
# -------------------------
st.markdown('<div class="topbar">Patient Cost Analysis Tool</div>', unsafe_allow_html=True)

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel("drug_data.xlsx")
df.columns = df.columns.str.strip()
df = df.dropna(subset=["Drug_Name"])

base_columns = ["J_Code", "Drug_Name", "Billing_Unit", "Cost_per_Unit"]
payer_columns = sorted([col for col in df.columns if col not in base_columns])

# -------------------------
# HELPERS
# -------------------------
def extract_number(value):
    try:
        if pd.isna(value):
            return None
        number = re.findall(r"[\d\.]+", str(value))
        if number:
            return float(number[0])
        return None
    except:
        return None

def format_date_us(d):
    return d.strftime("%m-%d-%Y")

# -------------------------
# MAIN CARD
# -------------------------
st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.header("Treatment Cost Calculator")

# -------------------------
# PATIENT INFO
# -------------------------
st.subheader("Patient Information")

col1, col2 = st.columns(2)

with col1:
    patient_name = st.text_input("Patient Name")
    dob = st.date_input("Date of Birth", min_value=date.today().replace(year=date.today().year - 100))

with col2:
    doctor = st.text_input("Doctor Name")
    treatment_date = st.date_input("Date of Treatment")

st.caption(f"DOB: {format_date_us(dob)} | Treatment: {format_date_us(treatment_date)}")

location = st.selectbox("Clinic Location", ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"])

# -------------------------
# INSURANCE
# -------------------------
st.subheader("Insurance")

payer = st.selectbox("Primary Insurance", payer_columns)
primary_coverage = st.slider("Primary Coverage %", 0, 100, 80) / 100

has_secondary = st.checkbox("Add Secondary Insurance")

secondary_coverage = 0
secondary_dropdown = None
secondary_text = ""

if has_secondary:
    col1, col2 = st.columns(2)

    with col1:
        secondary_dropdown = st.selectbox("Secondary Insurance", payer_columns)

    with col2:
        secondary_text = st.text_input("Or type insurance")

    secondary_coverage = st.slider("Secondary Coverage %", 0, 100, 20) / 100

copay = st.number_input("Copay ($)", min_value=0.0)

# -------------------------
# MEDICATIONS
# -------------------------
st.subheader("Medications")

num_drugs = st.number_input("Number of Drugs", 1, 10, 1)

drug_entries = []

for i in range(int(num_drugs)):
    col1, col2 = st.columns(2)

    with col1:
        drug = st.selectbox(f"Drug {i+1}", df["Drug_Name"].unique(), key=f"d{i}")

    with col2:
        dose = st.number_input(f"Dose {i+1}", min_value=0.0, key=f"dose{i}")

    drug_entries.append({"drug": drug, "dose": dose})

# -------------------------
# CALCULATE
# -------------------------
if st.button("Calculate"):

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
    secondary_payment = remaining * secondary_coverage
    patient = remaining - secondary_payment + copay

    st.subheader("Financial Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cost", f"${total_cost:,.2f}")
    col2.metric("Primary Pays", f"${primary_payment:,.2f}")
    col3.metric("Patient Pays", f"${patient:,.2f}")

    st.metric("Secondary Pays", f"${secondary_payment:,.2f}")

    st.success("Calculation Complete")

st.markdown('</div>', unsafe_allow_html=True)
