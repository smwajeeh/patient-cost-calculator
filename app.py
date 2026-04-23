import streamlit as st
import pandas as pd
import math
import re
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(page_title="Treatment Cost Calculator", layout="wide")

# -------------------------
# STYLE (CLEAN UI)
# -------------------------
st.markdown("""
<style>
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

.header {
    background-color: #6B7F4E;
    padding: 15px;
    border-radius: 8px;
    color: white;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
}

.stButton>button {
    background-color: #6B7F4E;
    color: white;
    border-radius: 8px;
    height: 40px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">💊 Patient Treatment Cost Calculator</div>', unsafe_allow_html=True)

# -------------------------
# HELPERS
# -------------------------
def extract_number(value):
    number = re.findall(r"[\d\.]+", str(value))
    return float(number[0]) if number else 0

def convert_to_mg(dose, unit):
    if unit == "mcg":
        return dose / 1000
    return dose

def format_date_us(d):
    return d.strftime("%m-%d-%Y")

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel("drug_data.xlsx")
df.columns = df.columns.str.strip()

base_columns = ["J_Code", "Drug_Name", "Billing_Unit", "Cost_per_Unit"]
payer_columns = sorted([c for c in df.columns if c not in base_columns])

df["Drug_Name_Clean"] = df["Drug_Name"].astype(str).str.strip().str.lower()

drug_list = ["Select Drug"] + sorted(df["Drug_Name"].dropna().unique())

# -------------------------
# PATIENT INFO
# -------------------------
st.subheader("🧑 Patient Information")

providers = sorted([
    "Navneet Mittal MD",
    "Sreecharan Mavuram MD",
    "Syed Raza MD"
])

col1, col2, col3 = st.columns(3)

with col1:
    patient_name = st.text_input("Patient Name")
    dob = st.date_input(
        "Date of Birth",
        min_value=date.today().replace(year=date.today().year - 100),
        max_value=date.today()
    )

with col2:
    provider = st.selectbox("Provider", providers)
    treatment_date = st.date_input("Date of Treatment", value=date.today())

with col3:
    location = st.selectbox("Clinic Location", ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"])

# -------------------------
# INSURANCE
# -------------------------
st.subheader("🏥 Insurance")

payer = st.selectbox("Primary Insurance", payer_columns)
primary_pct = st.slider("Primary Coverage %", 0, 100, 80)

copay = st.number_input("Copay", min_value=0, step=1)

has_secondary = st.checkbox("Has Secondary Insurance")

secondary_selected = None
secondary_text = ""

if has_secondary:
    options = ["Select"] + payer_columns + ["Other / Funding"]
    secondary_selected = st.selectbox("Secondary Insurance", options)

    if secondary_selected == "Other / Funding":
        secondary_text = st.text_input("Other / Funding Details")

# -------------------------
# MEDICATIONS
# -------------------------
st.subheader("💉 Medications")

if "med_count" not in st.session_state:
    st.session_state.med_count = 1

col_add, col_remove, col_reset = st.columns(3)

if col_add.button("➕ Add Medication"):
    st.session_state.med_count += 1

if col_remove.button("➖ Remove Medication") and st.session_state.med_count > 1:
    st.session_state.med_count -= 1

# Reset button (enabled only if at least one drug selected)
any_selected = any(
    st.session_state.get(f"d{i}", "Select Drug") != "Select Drug"
    for i in range(st.session_state.med_count)
)

if col_reset.button("🔄 Reset Medications", disabled=not any_selected):
    st.session_state.med_count = 1
    for i in range(10):
        st.session_state[f"d{i}"] = "Select Drug"
        st.session_state[f"dose{i}"] = 0.0
        st.session_state[f"u{i}"] = "mg"
    st.rerun()

drug_entries = []

for i in range(st.session_state.med_count):
    title = "Medication" if st.session_state.med_count == 1 else f"Medication {i+1}"
    st.subheader(title)

    col1, col2, col3 = st.columns(3)

    drug = col1.selectbox("Drug", drug_list, key=f"d{i}")
    dose = col2.number_input("Dose", min_value=0.0, key=f"dose{i}")
    unit = col3.selectbox("Units", ["mg", "mcg", "units"], key=f"u{i}")

    drug_entries.append({"drug": drug, "dose": dose, "unit": unit})

# -------------------------
# CALCULATE
# -------------------------
if st.button("Calculate"):

    if not patient_name:
        st.error("Patient Name is required")
        st.stop()

    if dob >= date.today():
        st.error("Date of Birth must be in the past.")
        st.stop()

    for entry in drug_entries:
        if entry["drug"] == "Select Drug":
            st.error("Please select a drug for all medications.")
            st.stop()

        if entry["dose"] <= 0:
            st.error(f"Please enter a valid dose for {entry['drug']}.")
            st.stop()

    if has_secondary:
        if secondary_selected in [None, "Select"]:
            st.error("Please select Secondary Insurance")
            st.stop()

        if secondary_selected == "Other / Funding" and not secondary_text.strip():
            st.error("Please enter Other / Funding details")
            st.stop()

    total_cost = 0
    total_allowed = 0
    missing_drugs = []

    for entry in drug_entries:
        drug_clean = str(entry["drug"]).strip().lower()
        filtered = df[df["Drug_Name_Clean"] == drug_clean]

        if filtered.empty:
            missing_drugs.append(entry["drug"])
            continue

        data = filtered.iloc[0]

        billing_unit = extract_number(data["Billing_Unit"])
        cost = extract_number(data["Cost_per_Unit"])
        allowable = extract_number(data[payer])

        if billing_unit == 0:
            continue

        dose_mg = convert_to_mg(entry["dose"], entry["unit"])
        units = math.ceil(dose_mg / billing_unit)

        total_cost += units * cost
        total_allowed += units * allowable

    clean_missing = [str(d) for d in missing_drugs if pd.notna(d) and str(d).strip() != ""]

    if clean_missing:
        st.warning("Some drugs were not found and skipped: " + ", ".join(clean_missing))

    primary_payment = total_allowed * (primary_pct / 100)
    remaining = total_allowed - primary_payment

    if has_secondary:
        secondary_payment = remaining
        patient_payment = copay
    else:
        secondary_payment = 0
        patient_payment = remaining + copay

    st.subheader("💰 Financial Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Cost", f"${total_cost:,.2f}")
    c2.metric("Primary Pays", f"${primary_payment:,.2f}")
    c3.metric("Patient Pays", f"${patient_payment:,.2f}")

    if has_secondary:
        st.metric("Secondary Pays", f"${secondary_payment:,.2f}")

    st.subheader("🧾 Summary")

    st.markdown(f"""
    **Provider:** {provider}  
    **Treatment Date:** {format_date_us(treatment_date)}  
    **Date of Birth:** {format_date_us(dob)}  

    **Total Cost:** ${total_cost:,.2f}  
    **Primary Insurance Pays:** ${primary_payment:,.2f}  
    **Secondary Insurance Pays:** ${secondary_payment:,.2f}  
    **Patient Responsibility:** ${patient_payment:,.2f}
    """)
