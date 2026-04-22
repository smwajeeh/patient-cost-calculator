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

.stMetric {
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
    text-align: center;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
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
        return float(number[0]) if number else None
    except:
        return None

def convert_to_mg(dose, unit):
    if unit == "mcgs":
        return dose / 1000
    return dose

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

providers = sorted([
    "Sreecharan Mavuram MD",
    "Syed Raza MD",
    "Navneet Mittal MD"
])

col1, col2, col3 = st.columns(3)

with col1:
    patient_name = st.text_input("Patient Name")
    dob = st.date_input("Date of Birth", min_value=date.today().replace(year=date.today().year - 100))
    st.caption(f"📅 {format_date_us(dob)}")

with col2:
    provider = st.selectbox("Provider", providers)
    treatment_date = st.date_input("Date of Treatment", value=date.today())
    st.caption(f"📅 {format_date_us(treatment_date)}")

with col3:
    location = st.selectbox("Clinic Location", ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"])

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
secondary_dropdown = ""
secondary_text = ""

if has_secondary:
    col1, col2 = st.columns(2)

    secondary_options = [""] + payer_columns + ["Other / Funding"]

    with col1:
        secondary_dropdown = st.selectbox("Secondary Insurance", secondary_options)

    with col2:
        secondary_text = st.text_input("Other / Funding", disabled=(secondary_dropdown != "Other / Funding"))

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
        dose = st.number_input("Dose", min_value=0, step=1, format="%d", key=f"dose{i}")

    with col3:
        unit = st.selectbox("Units", ["mgs", "mcgs"], key=f"u{i}")

    drug_entries.append({
        "drug": drug,
        "dose": dose,
        "unit": unit
    })

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# CALCULATION
# -------------------------
if st.button("Calculate"):

    error = False

    if has_secondary:
        if secondary_dropdown == "":
            st.error("Please select a Secondary Insurance option.")
            error = True

        if secondary_dropdown == "Other / Funding" and secondary_text.strip() == "":
            st.error("Please enter details for Other / Funding.")
            error = True

    if error:
        st.stop()

    total_cost = 0
    total_allowed = 0

    for entry in drug_entries:
        drug_data = df[df["Drug_Name"] == entry["drug"]].iloc[0]

        billing_unit = extract_number(drug_data["Billing_Unit"])
        cost = extract_number(drug_data["Cost_per_Unit"])
        allowable = extract_number(drug_data[payer])

        dose_mg = convert_to_mg(entry["dose"], entry["unit"])

        units = math.ceil(dose_mg / billing_unit)

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
    # FINANCIAL SUMMARY
    # -------------------------
    st.subheader("💰 Financial Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cost", f"${total_cost:,.2f}")
    col2.metric("Primary Pays", f"${primary_payment:,.2f}")
    col3.metric("Patient Pays", f"${patient:,.2f}")

    if has_secondary:
        st.metric("Secondary Pays", f"${secondary_payment:,.2f}")
    else:
        st.info(f"Patient responsible: ${remaining:,.2f}")

    # -------------------------
    # SUMMARY (ADDED BACK)
    # -------------------------
    st.subheader("🧾 Summary")

    if has_secondary:
        st.write(f"""
        **Provider:** {provider}  
        **Treatment Date:** {format_date_us(treatment_date)}  
        **Date of Birth:** {format_date_us(dob)}  

        **Total Cost:** ${total_cost:,.2f}  
        **Primary Insurance Pays:** ${primary_payment:,.2f}  
        **Secondary Insurance Pays:** ${secondary_payment:,.2f}  
        **Patient Responsibility:** ${patient:,.2f}
        """)
    else:
        st.write(f"""
        **Provider:** {provider}  
        **Treatment Date:** {format_date_us(treatment_date)}  
        **Date of Birth:** {format_date_us(dob)}  

        **Total Cost:** ${total_cost:,.2f}  
        **Primary Insurance Pays:** ${primary_payment:,.2f}  

        Patient does not have secondary insurance.  
        **Patient Responsibility:** ${patient:,.2f}
        """)
