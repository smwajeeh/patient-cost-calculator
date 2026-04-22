import streamlit as st
import pandas as pd
import math
import re
from datetime import date

st.set_page_config(page_title="Treatment Cost Calculator", layout="wide")

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
st.header("Patient Information")

providers = sorted([
    "Navneet Mittal MD",
    "Sreecharan Mavuram MD",
    "Syed Raza MD"
])

patient_name = st.text_input("Patient Name")
provider = st.selectbox("Provider", providers)
dob = st.date_input("DOB", min_value=date.today().replace(year=date.today().year - 100))
treatment_date = st.date_input("Treatment Date", value=date.today())
location = st.selectbox("Location", ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"])

# -------------------------
# INSURANCE
# -------------------------
st.header("Insurance")

payer = st.selectbox("Primary Insurance", payer_columns)
primary_pct = st.slider("Primary Coverage %", 0, 100, 80)

has_secondary = st.checkbox("Has Secondary Insurance")

secondary_selected = None

if has_secondary:
    options = ["Select"] + payer_columns + ["Other / Funding"]
    secondary_selected = st.selectbox("Secondary Insurance", options)

    if secondary_selected == "Other / Funding":
        secondary_text = st.text_input("Other / Funding Details")

copay = st.number_input("Copay", min_value=0, step=1)

# -------------------------
# MEDICATIONS
# -------------------------
st.header("Medications")

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
    dose = col2.number_input("Dose", min_value=0.0, key=f"dose{i}")  # decimals allowed
    unit = col3.selectbox("Units", ["mgs", "mcgs", "grams"], key=f"u{i}")

    drug_entries.append({"drug": drug, "dose": dose, "unit": unit})

# -------------------------
# CALCULATE
# -------------------------
if st.button("Calculate"):

    # -------- VALIDATION --------
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

    # -------- CALCULATION --------
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

    # -------- OUTPUT --------
    st.header("Financial Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Cost", f"${total_cost:,.2f}")
    c2.metric("Primary Pays", f"${primary_payment:,.2f}")
    c3.metric("Patient Pays", f"${patient_payment:,.2f}")

    if has_secondary:
        st.metric("Secondary Pays", f"${secondary_payment:,.2f}")

    # -------- SUMMARY --------
    st.header("Summary")

    st.write(f"""
    Provider: {provider}  
    Treatment Date: {format_date_us(treatment_date)}  
    DOB: {format_date_us(dob)}  

    Total Cost: ${total_cost:,.2f}  
    Primary Pays: ${primary_payment:,.2f}  
    Secondary Pays: ${secondary_payment:,.2f}  
    Patient Pays: ${patient_payment:,.2f}
    """)
