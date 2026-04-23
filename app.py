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
# STYLE
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
    if unit == "mcgs":
        return dose / 1000
    return dose

def format_date_us(d):
    return d.strftime("%m-%d-%Y")

def generate_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Patient Treatment Cost Report", styles["Title"]))
    content.append(Spacer(1, 12))

    for line in data:
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 8))

    doc.build(content)
    buffer.seek(0)
    return buffer

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel("drug_data.xlsx")
df.columns = df.columns.str.strip()
df["Drug_Name_Clean"] = df["Drug_Name"].astype(str).str.strip().str.lower()

base_columns = ["J_Code", "Drug_Name", "Billing_Unit", "Cost_per_Unit"]
payer_columns = sorted([c for c in df.columns if c not in base_columns])

drug_list = ["Select Drug"] + sorted(df["Drug_Name"].dropna().unique())
unit_list = ["", "mgs", "mcgs", "units"]

# -------------------------
# SESSION STATE
# -------------------------
if "meds" not in st.session_state:
    st.session_state.meds = [{"drug": "Select Drug", "dose": 0.0, "unit": "mgs"}]

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

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

updated_meds = []

for i, med in enumerate(st.session_state.meds):

    col1, col2, col3, col4 = st.columns([3,2,2,1.5])

    drug = col1.selectbox("Drug", drug_list,
        index=drug_list.index(med["drug"]) if med["drug"] in drug_list else 0,
        key=f"drug{i}"
    )

    dose = col2.number_input("Dose", min_value=0.0, value=med["dose"], key=f"dose{i}")

    unit = col3.selectbox("Units", unit_list,
        index=unit_list.index(med["unit"]) if med["unit"] in unit_list else 1,
        key=f"unit{i}"
    )

    col4.markdown("<br>", unsafe_allow_html=True)
    delete_clicked = col4.button("Delete 🗑️", key=f"delete{i}")

    # clear summary on change
    if drug != med["drug"] or dose != med["dose"] or unit != med["unit"]:
        st.session_state.show_summary = False

    if delete_clicked:
        st.session_state.show_summary = False

        if i == 0:
            updated_meds.append({
                "drug": "Select Drug",
                "dose": 0.0,
                "unit": ""
            })
        else:
            continue
    else:
        updated_meds.append({
            "drug": drug,
            "dose": dose,
            "unit": unit
        })

if len(updated_meds) == 0:
    updated_meds = [{"drug": "Select Drug", "dose": 0.0, "unit": "mgs"}]

st.session_state.meds = updated_meds

if st.button("➕ Add Medication"):
    st.session_state.meds.append({"drug": "Select Drug", "dose": 0.0, "unit": "mgs"})
    st.session_state.show_summary = False
    st.rerun()

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

    total_cost = 0
    total_allowed = 0
    missing_drugs = []

    for entry in st.session_state.meds:

        if entry["drug"] == "Select Drug":
            st.error("Please select a drug for all medications.")
            st.stop()

        if entry["dose"] <= 0:
            st.error(f"Invalid dose for {entry['drug']}")
            st.stop()

        if entry["unit"] == "":
            st.error(f"Select units for {entry['drug']}")
            st.stop()

        filtered = df[df["Drug_Name_Clean"] == entry["drug"].lower()]

        if filtered.empty:
            missing_drugs.append(entry["drug"])
            continue

        data = filtered.iloc[0]

        billing_unit = extract_number(data["Billing_Unit"])
        cost = extract_number(data["Cost_per_Unit"])
        allowable = extract_number(data[payer])

        dose_mg = convert_to_mg(entry["dose"], entry["unit"])
        units = math.ceil(dose_mg / billing_unit)

        total_cost += units * cost
        total_allowed += units * allowable

    if missing_drugs:
        st.warning("Missing drugs: " + ", ".join(missing_drugs))

    primary_payment = total_allowed * (primary_pct / 100)
    remaining = total_allowed - primary_payment

    if has_secondary:
        secondary_payment = remaining
        patient_payment = copay
    else:
        secondary_payment = 0
        patient_payment = remaining + copay

    st.session_state.summary = {
        "total_cost": total_cost,
        "primary": primary_payment,
        "secondary": secondary_payment,
        "patient": patient_payment
    }

    st.session_state.show_summary = True

# -------------------------
# SUMMARY
# -------------------------
if st.session_state.show_summary:

    s = st.session_state.summary

    st.subheader("💰 Financial Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Cost", f"${s['total_cost']:,.2f}")
    c2.metric("Primary Pays", f"${s['primary']:,.2f}")
    c3.metric("Patient Pays", f"${s['patient']:,.2f}")

    if has_secondary:
        st.metric("Secondary Pays", f"${s['secondary']:,.2f}")

    pdf = generate_pdf([
        f"Total Cost: ${s['total_cost']:,.2f}",
        f"Primary: ${s['primary']:,.2f}",
        f"Patient: ${s['patient']:,.2f}"
    ])

    st.download_button("📄 Download PDF", pdf, "report.pdf")
