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
# MODERN UI DESIGN
# -------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

.block-container {
    padding-top: 2rem;
}

h1 {
    color: #38bdf8;
    font-weight: 700;
}

h2, h3 {
    color: #e2e8f0;
}

.stTextInput, .stSelectbox, .stNumberInput {
    background-color: #1e293b;
}

.stMetric {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
    font-size: 18px;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("💊 Patient Treatment Cost Calculator")

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
# PATIENT INFO
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🧑 Patient Information")

col1, col2, col3 = st.columns(3)

with col1:
    patient_name = st.text_input("Patient Name")

    dob = st.date_input(
        "Date of Birth",
        min_value=date.today().replace(year=date.today().year - 100),
        max_value=date.today()
    )

    st.caption(f"📅 Selected: {format_date_us(dob)}")

with col2:
    doctor = st.text_input("Doctor Name")

    treatment_date = st.date_input("Date of Treatment", value=date.today())

    st.caption(f"📅 Selected: {format_date_us(treatment_date)}")

with col3:
    location = st.selectbox(
        "Clinic Location",
        ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"]
    )

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# INSURANCE
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🏥 Insurance")

payer = st.selectbox("Primary Insurance", payer_columns)
primary_coverage = st.slider("Primary Coverage %", 0, 100, 80) / 100

has_secondary = st.checkbox("Has Secondary Insurance")

secondary_coverage = 0
secondary_dropdown = None
secondary_text = ""

if has_secondary:
    col1, col2 = st.columns(2)

    with col1:
        secondary_dropdown = st.selectbox("Secondary Insurance", payer_columns)

    with col2:
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
# CALCULATION
# -------------------------
if st.button("Calculate"):

    total_cost = 0
    total_allowed = 0
    rows = []

    for entry in drug_entries:
        drug_data = df[df["Drug_Name"] == entry["drug"]].iloc[0]

        billing_unit = extract_number(drug_data["Billing_Unit"])
        cost = extract_number(drug_data["Cost_per_Unit"])
        allowable = extract_number(drug_data[payer])
        dose_val = extract_number(entry["dose"])

        units = math.ceil(dose_val / billing_unit)

        drug_cost = units * cost
        allowed = units * allowable

        total_cost += drug_cost
        total_allowed += allowed

        rows.append({
            "Drug": entry["drug"],
            "Units": units,
            "Cost": round(drug_cost, 2),
            "Allowed": round(allowed, 2)
        })

    primary_payment = total_allowed * primary_coverage
    remaining = total_allowed - primary_payment
    secondary_payment = remaining * secondary_coverage
    patient = remaining - secondary_payment + copay

    # RESULTS
    st.subheader("💰 Financial Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Cost", f"${total_cost:,.2f}")
    c2.metric("Primary Pays", f"${primary_payment:,.2f}")
    c3.metric("Patient Pays", f"${patient:,.2f}")

    st.metric("Secondary Pays", f"${secondary_payment:,.2f}")

    st.subheader("🧾 Summary")

    st.write(f"""
    **Treatment Date:** {format_date_us(treatment_date)}  
    **DOB:** {format_date_us(dob)}

    **Total Cost:** ${total_cost:,.2f}  
    **Primary Pays:** ${primary_payment:,.2f}  
    **Secondary Pays:** ${secondary_payment:,.2f}  
    **Patient Pays:** ${patient:,.2f}
    """)
