import streamlit as st
import pandas as pd
import math
import re

st.set_page_config(page_title="Treatment Cost Calculator", layout="wide")

st.title("💊 Patient Treatment Cost Calculator")

# -------------------------
# Helper: Extract numeric value from messy strings
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

# -------------------------
# Load Excel Data
# -------------------------
try:
    df = pd.read_excel("drug_data.xlsx")
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Drug_Name"])
except Exception as e:
    st.error(f"❌ Error loading Excel file: {e}")
    st.stop()

# -------------------------
# Detect Payer Columns
# -------------------------
base_columns = ["J_Code", "Drug_Name", "Billing_Unit", "Cost_per_Unit"]
payer_columns = [col for col in df.columns if col not in base_columns]

if not payer_columns:
    st.error("❌ No payer columns found in Excel file.")
    st.stop()

# -------------------------
# Patient Info
# -------------------------
st.subheader("🧑 Patient Information")

col1, col2 = st.columns(2)

with col1:
    patient_name = st.text_input("Patient Name")
    dob = st.date_input("Date of Birth")

with col2:
    doctor = st.text_input("Doctor Name")
    location = st.text_input("Clinic Location")

# -------------------------
# Insurance
# -------------------------
st.subheader("🏥 Insurance Information")

payer = st.selectbox("Select Insurance (Payer)", payer_columns)

primary_coverage = st.slider("Primary Coverage %", 0, 100, 80) / 100

has_secondary = st.checkbox("Has Secondary Insurance")

secondary_coverage = 0
if has_secondary:
    secondary_coverage = st.slider("Secondary Coverage %", 0, 100, 20) / 100

copay = st.number_input("Copay ($)", min_value=0.0)

# -------------------------
# Multi Drug Input
# -------------------------
st.subheader("💉 Medications")

num_drugs = st.number_input("Number of Medications", min_value=1, max_value=10, value=1)

drug_entries = []

for i in range(int(num_drugs)):
    st.markdown(f"### Medication {i+1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        drug = st.selectbox(
            f"Drug {i+1}",
            df["Drug_Name"].unique(),
            key=f"drug_{i}"
        )

    with col2:
        dose = st.number_input(
            f"Dose {i+1}",
            min_value=0.0,
            key=f"dose_{i}"
        )

    with col3:
        unit = st.selectbox(
            f"Unit {i+1}",
            ["mg", "mcg"],
            key=f"unit_{i}"
        )

    drug_entries.append({
        "drug": drug,
        "dose": dose,
        "unit": unit
    })

# -------------------------
# Calculation
# -------------------------
if st.button("Calculate"):

    total_cost = 0
    total_allowed = 0

    detailed_rows = []

    for entry in drug_entries:

        drug_df = df[df["Drug_Name"] == entry["drug"]]

        if drug_df.empty:
            st.error(f"❌ No data found for {entry['drug']}")
            st.stop()

        drug_data = drug_df.iloc[0]

        # -------------------------
        # Extract & Validate Data
        # -------------------------
        billing_unit = extract_number(drug_data["Billing_Unit"])
        cost_per_unit = extract_number(drug_data["Cost_per_Unit"])
        allowable_per_unit = extract_number(drug_data[payer])
        dose_value = extract_number(entry["dose"])

        if billing_unit is None:
            st.error(f"❌ Invalid Billing Unit for {entry['drug']} → {drug_data['Billing_Unit']}")
            st.stop()

        if cost_per_unit is None:
            st.error(f"❌ Invalid Cost for {entry['drug']}")
            st.stop()

        if allowable_per_unit is None:
            st.error(f"❌ Invalid Allowable for {entry['drug']} under {payer}")
            st.stop()

        if dose_value is None or dose_value <= 0:
            st.error(f"❌ Invalid Dose for {entry['drug']}")
            st.stop()

        if billing_unit <= 0:
            st.error(f"❌ Billing unit must be greater than 0 for {entry['drug']}")
            st.stop()

        # -------------------------
        # Billing Logic (CEIL)
        # -------------------------
        units_billed = math.ceil(dose_value / billing_unit)

        drug_cost = units_billed * cost_per_unit
        allowed = units_billed * allowable_per_unit

        total_cost += drug_cost
        total_allowed += allowed

        detailed_rows.append({
            "Drug": entry["drug"],
            "Dose": dose_value,
            "Billing Unit": billing_unit,
            "Units Billed": units_billed,
            "Cost": round(drug_cost, 2),
            "Allowed": round(allowed, 2)
        })

    # -------------------------
    # Insurance Calculations
    # -------------------------
    primary_payment = total_allowed * primary_coverage
    remaining = total_allowed - primary_payment

    secondary_payment = remaining * secondary_coverage
    patient_responsibility = remaining - secondary_payment + copay

    # -------------------------
    # Output
    # -------------------------
    st.subheader("📊 Medication Breakdown")
    st.dataframe(pd.DataFrame(detailed_rows))

    st.subheader("💰 Financial Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Drug Cost", f"${total_cost:,.2f}")
    col2.metric("Total Allowed", f"${total_allowed:,.2f}")
    col3.metric("Patient Responsibility", f"${patient_responsibility:,.2f}")

    st.metric("Primary Insurance Pays", f"${primary_payment:,.2f}")
    st.metric("Secondary Insurance Pays", f"${secondary_payment:,.2f}")

    # -------------------------
    # Summary
    # -------------------------
    st.subheader("🧾 Summary")

    st.write(f"""
    Total treatment cost is **${total_cost:,.2f}** across {int(num_drugs)} medication(s).

    Insurance allows **${total_allowed:,.2f}**.

    Primary insurance pays **${primary_payment:,.2f}** ({primary_coverage*100:.0f}%).
    """)

    if has_secondary:
        st.write(f"Secondary insurance pays **${secondary_payment:,.2f}**.")

    st.write(f"""
    Patient is responsible for **${patient_responsibility:,.2f}**, including copay.
    """)

    # -------------------------
    # Patient Record
    # -------------------------
    st.subheader("📋 Patient Record")

    st.write(f"""
    **Patient:** {patient_name}  
    **DOB:** {dob}  
    **Doctor:** {doctor}  
    **Location:** {location}  
    **Payer:** {payer}  
    """)
