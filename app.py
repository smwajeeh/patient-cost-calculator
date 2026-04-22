import streamlit as st
import pandas as pd
import math
import re
from datetime import date

st.set_page_config(page_title="Treatment Cost Calculator", layout="wide")

# -------------------------
# STYLE (UPDATED DARK DIVIDERS)
# -------------------------
st.markdown("""
<style>
body {
    background-color: #F9FAFB;
}

/* Header */
.header {
    background-color: #6B7F4E;
    padding: 15px;
    border-radius: 8px;
    color: white;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
}

/* Cards */
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #374151; /* 🔥 DARK GREY */
    margin-bottom: 20px;
}

/* Remove white dividers */
hr {
    border: none;
    border-top: 1px solid #374151 !important;
}

/* Streamlit default blocks */
.css-1d391kg, .css-1v0mbdj {
    border-color: #374151 !important;
}

/* Button */
.stButton>button {
    background-color: #6B7F4E;
    color: white;
    border-radius: 8px;
    height: 45px;
    font-weight: 600;
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
        number = re.findall(r"[\d\.]+", str(value))
        return float(number[0]) if number else None
    except:
        return None

def convert_to_mg(dose, unit):
    if unit == "mcgs":
        return dose / 1000
    elif unit == "grams":
        return dose * 1000
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
    dob = st.date_input("Date of Birth", min_value=date.today().replace(year=date.today().year - 100))

with col2:
    provider = st.selectbox("Provider", providers)
    treatment_date = st.date_input("Date of Treatment", value=date.today())

with col3:
    location = st.selectbox("Clinic Location", ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"])

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# INSURANCE
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🏥 Insurance")

payer = st.selectbox("Primary Insurance", payer_columns)
primary_pct = st.slider("Primary Coverage %", 0, 100, 80)

has_secondary = st.checkbox("Has Secondary Insurance")

secondary_selected = None
secondary_text = ""

if has_secondary:
    options = ["Select"] + payer_columns + ["Other / Funding"]
    secondary_selected = st.selectbox("Secondary Insurance", options)

    if secondary_selected == "Other / Funding":
        secondary_text = st.text_input("Other / Funding Details")

copay = st.number_input("Copay", min_value=0, step=1)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# MEDICATIONS
# -------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("💉 Medications")

if "med_count" not in st.session_state:
    st.session_state.med_count = 1

col_add, col_remove = st.columns(2)

if col_add.button("➕ Add Medication"):
    st.session_state.med_count += 1

if col_remove.button("➖ Remove Medication") and st.session_state.med_count > 1:
    st.session_state.med_count -= 1

drug_entries = []

for i in range(st.session_state.med_count):

    title = "Medication" if st.session_state.med_count == 1 else f"Medication {i+1}"
    st.subheader(title)

    col1, col2, col3 = st.columns(3)

    drug = col1.selectbox("Drug", df["Drug_Name"].unique(), key=f"d{i}")
    dose = col2.number_input("Dose", min_value=0.0, key=f"dose{i}")
    unit = col3.selectbox("Units", ["mgs", "mcgs", "grams"], key=f"u{i}")

    drug_entries.append({"drug": drug, "dose": dose, "unit": unit})

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# CALCULATE
# -------------------------
if st.button("Calculate"):

    if not patient_name:
        st.error("Patient Name is required")
        st.stop()

    if has_secondary:
        if secondary_selected in [None, "Select"]:
            st.error("Please select Secondary Insurance")
            st.stop()

        if secondary_selected == "Other / Funding" and not secondary_text.strip():
            st.error("Please enter Other / Funding details")
            st.stop()

    for entry in drug_entries:
        if entry["dose"] == 0:
            st.error("Dose cannot be zero")
            st.stop()

    total_cost = 0
    total_allowed = 0

    for entry in drug_entries:
        data = df[df["Drug_Name"] == entry["drug"]].iloc[0]

        billing_unit = extract_number(data["Billing_Unit"])
        cost = extract_number(data["Cost_per_Unit"])
        allowable = extract_number(data[payer])

        dose_mg = convert_to_mg(entry["dose"], entry["unit"])
        units = math.ceil(dose_mg / billing_unit)

        total_cost += units * cost
        total_allowed += units * allowable

    primary_payment = total_allowed * (primary_pct / 100)
    remaining = total_allowed - primary_payment

    if has_secondary:
        secondary_payment = remaining
        patient_payment = copay
    else:
        secondary_payment = 0
        patient_payment = remaining + copay

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💰 Financial Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cost", f"${total_cost:,.2f}")
    col2.metric("Primary Pays", f"${primary_payment:,.2f}")
    col3.metric("Patient Pays", f"${patient_payment:,.2f}")

    if has_secondary:
        st.metric("Secondary Pays", f"${secondary_payment:,.2f}")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧾 Summary")

    st.write(f"""
    **Provider:** {provider}  
    **Treatment Date:** {format_date_us(treatment_date)}  
    **DOB:** {format_date_us(dob)}  

    **Total Cost:** ${total_cost:,.2f}  
    **Primary Pays:** ${primary_payment:,.2f}  
    **Secondary Pays:** ${secondary_payment:,.2f}  
    **Patient Pays:** ${patient_payment:,.2f}
    """)

    st.markdown('</div>', unsafe_allow_html=True)
