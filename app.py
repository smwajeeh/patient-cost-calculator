import streamlit as st
import pandas as pd
import math
import re
from datetime import date

# -------------------------
# PAGE CONFIG + STYLE
# -------------------------
st.set_page_config(page_title="Treatment Cost Calculator", layout="wide")

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
h1, h2, h3 {
    color: #1f4e79;
}
.stMetric {
    background-color: #ffffff;
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0px 1px 5px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.title("💊 Patient Treatment Cost Calculator")

# -------------------------
# Helper
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
# Load Data
# -------------------------
try:
    df = pd.read_excel("drug_data.xlsx")
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Drug_Name"])
except Exception as e:
    st.error(f"❌ Error loading Excel file: {e}")
    st.stop()

base_columns = ["J_Code", "Drug_Name", "Billing_Unit", "Cost_per_Unit"]
payer_columns = sorted([col for col in df.columns if col not in base_columns])

# -------------------------
# PATIENT INFO
# -------------------------
st.subheader("🧑 Patient Information")

col1, col2, col3 = st.columns(3)

with col1:
    patient_name = st.text_input("Patient Name")
    dob = st.date_input(
        "Date of Birth",
        min_value=date.today().replace(year=date.today().year - 100),
        max_value=date.today()
    )

with col2:
    doctor = st.text_input("Doctor Name")
    treatment_date = st.date_input("Date of Treatment", value=date.today())

with col3:
    location = st.selectbox(
        "Clinic Location",
        ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"]
    )

# -------------------------
# INSURANCE
# -------------------------
st.subheader("🏥 Insurance Information")

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

# -------------------------
# MEDICATIONS
# -------------------------
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

# -------------------------
# CALCULATION
# -------------------------
if st.button("Calculate"):

    total_cost = 0
    total_allowed_primary = 0
    total_allowed_secondary = 0

    rows = []

    for entry in drug_entries:
        drug_data = df[df["Drug_Name"] == entry["drug"]].iloc[0]

        billing_unit = extract_number(drug_data["Billing_Unit"])
        cost = extract_number(drug_data["Cost_per_Unit"])
        primary_allowable = extract_number(drug_data[payer])
        dose_val = extract_number(entry["dose"])

        if None in [billing_unit, cost, primary_allowable, dose_val]:
            st.error(f"❌ Invalid data for {entry['drug']}")
            st.stop()

        units = math.ceil(dose_val / billing_unit)

        drug_cost = units * cost
        primary_allowed = units * primary_allowable

        total_cost += drug_cost
        total_allowed_primary += primary_allowed

        # Secondary logic
        if has_secondary:
            if secondary_text.strip() != "":
                secondary_allowed = primary_allowed  # fallback
            else:
                secondary_allowable = extract_number(drug_data[secondary_dropdown])
                secondary_allowed = units * secondary_allowable
        else:
            secondary_allowed = 0

        total_allowed_secondary += secondary_allowed

        rows.append({
            "Drug": entry["drug"],
            "Units": units,
            "Cost": round(drug_cost, 2),
            "Primary Allowed": round(primary_allowed, 2)
        })

    primary_payment = total_allowed_primary * primary_coverage
    remaining = total_allowed_primary - primary_payment

    secondary_payment = remaining * secondary_coverage
    patient = remaining - secondary_payment + copay

    # -------------------------
    # OUTPUT
    # -------------------------
    st.subheader("📊 Medication Breakdown")
    st.dataframe(pd.DataFrame(rows))

    st.subheader("💰 Financial Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Cost", f"${total_cost:,.2f}")
    c2.metric("Primary Pays", f"${primary_payment:,.2f}")
    c3.metric("Patient Pays", f"${patient:,.2f}")

    st.metric("Secondary Pays", f"${secondary_payment:,.2f}")

    # -------------------------
    # SUMMARY
    # -------------------------
    st.subheader("🧾 Summary")

    st.write(f"""
    Treatment Date: **{treatment_date.strftime('%m/%d/%Y')}**  
    DOB: **{dob.strftime('%m/%d/%Y')}**

    Total Cost: **${total_cost:,.2f}**  
    Primary Pays: **${primary_payment:,.2f}**  
    Secondary Pays: **${secondary_payment:,.2f}**  
    Patient Pays: **${patient:,.2f}**
    """)
