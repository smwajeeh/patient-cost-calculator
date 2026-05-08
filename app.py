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

st.markdown(
    '<div class="header">💊 Patient Treatment Cost Calculator</div>',
    unsafe_allow_html=True
)

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

    content.append(
        Paragraph("Patient Treatment Cost Report", styles["Title"])
    )

    content.append(Spacer(1, 12))

    for line in data:
        content.append(
            Paragraph(line, styles["Normal"])
        )

        content.append(Spacer(1, 8))

    doc.build(content)

    buffer.seek(0)

    return buffer


# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel("drug_data.xlsx")

df.columns = df.columns.str.strip()

df["Drug_Name_Clean"] = (
    df["Drug_Name"]
    .astype(str)
    .str.strip()
    .str.lower()
)

base_columns = [
    "J_Code",
    "Drug_Name",
    "Billing_Unit",
    "Cost_per_Unit",
    "Drug_Name_Clean"
]

payer_columns = sorted([
    c for c in df.columns
    if c not in base_columns
])

drug_list = ["Select Drug"] + sorted(
    df["Drug_Name"].dropna().unique()
)

unit_list = ["", "mgs", "mcgs", "units"]

# -------------------------
# SESSION STATE
# -------------------------
if "meds" not in st.session_state:
    st.session_state.meds = [
        {
            "drug": "Select Drug",
            "dose": 0.0,
            "unit": "mgs"
        }
    ]

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

c1, c2, c3 = st.columns(3)

with c1:
    patient_name = st.text_input("Patient Name")

    dob = st.date_input(
        "Date of Birth",
        max_value=date.today()
    )

with c2:
    provider = st.selectbox(
        "Provider",
        providers
    )

    treatment_date = st.date_input(
        "Date of Treatment",
        value=date.today()
    )

with c3:
    location = st.selectbox(
        "Clinic Location",
        [
            "Downtown",
            "Live Oak",
            "Mission Trail",
            "Stone Oak"
        ]
    )

# -------------------------
# INSURANCE
# -------------------------
st.subheader("🏥 Insurance")

payer = st.selectbox(
    "Primary Insurance",
    payer_columns
)

primary_pct = st.slider(
    "Primary Coverage %",
    0,
    100,
    80
)

copay = st.number_input(
    "Copay",
    min_value=0,
    step=1
)

has_secondary = st.checkbox(
    "Has Secondary Insurance"
)

secondary_selected = None
secondary_text = ""

if has_secondary:

    options = (
        ["Select"] +
        payer_columns +
        ["Other / Funding"]
    )

    secondary_selected = st.selectbox(
        "Secondary Insurance",
        options
    )

    if secondary_selected == "Other / Funding":
        secondary_text = st.text_input(
            "Other / Funding Details"
        )

# -------------------------
# MEDICATIONS
# -------------------------
st.subheader("💉 Medications")

any_selected = any(
    m["drug"] != "Select Drug"
    for m in st.session_state.meds
)

if st.button(
    "🔄 Reset Medications",
    disabled=not any_selected
):
    st.session_state.meds = [
        {
            "drug": "Select Drug",
            "dose": 0.0,
            "unit": "mgs"
        }
    ]

    st.session_state.show_summary = False

    st.rerun()

updated = []

for i, med in enumerate(st.session_state.meds):

    col1, col2, col3, col4 = st.columns([3,2,2,1.5])

    drug = col1.selectbox(
        "Drug",
        drug_list,
        index=drug_list.index(med["drug"])
        if med["drug"] in drug_list else 0,
        key=f"d{i}"
    )

    dose = col2.number_input(
        "Dose",
        min_value=0.0,
        value=med["dose"],
        key=f"ds{i}"
    )

    unit = col3.selectbox(
        "Units",
        unit_list,
        index=unit_list.index(med["unit"])
        if med["unit"] in unit_list else 1,
        key=f"u{i}"
    )

    col4.markdown("<br>", unsafe_allow_html=True)

    delete = col4.button(
        "Delete 🗑️",
        key=f"del{i}"
    )

    if (
        drug != med["drug"] or
        dose != med["dose"] or
        unit != med["unit"]
    ):
        st.session_state.show_summary = False

    if delete:

        st.session_state.show_summary = False

        if i == 0:
            updated.append({
                "drug": "Select Drug",
                "dose": 0.0,
                "unit": ""
            })

        else:
            continue

    else:
        updated.append({
            "drug": drug,
            "dose": dose,
            "unit": unit
        })

if len(updated) == 0:
    updated = [{
        "drug": "Select Drug",
        "dose": 0.0,
        "unit": "mgs"
    }]

st.session_state.meds = updated

if st.button("➕ Add Medication"):

    st.session_state.meds.append({
        "drug": "Select Drug",
        "dose": 0.0,
        "unit": "mgs"
    })

    st.session_state.show_summary = False

    st.rerun()

# -------------------------
# CALCULATE
# -------------------------
if st.button("Calculate"):

    total_cost = 0
    total_allowed = 0

    missing = []

    for entry in st.session_state.meds:

        if entry["drug"] == "Select Drug":
            st.error("Select drug")
            st.stop()

        if entry["dose"] <= 0:
            st.error("Invalid dose")
            st.stop()

        if entry["unit"] == "":
            st.error("Select units")
            st.stop()

        filtered = df[
            df["Drug_Name_Clean"] ==
            entry["drug"].lower()
        ]

        if filtered.empty:
            missing.append(entry["drug"])
            continue

        data = filtered.iloc[0]

        billing_unit = extract_number(
            data["Billing_Unit"]
        )

        cost = extract_number(
            data["Cost_per_Unit"]
        )

        allowable = extract_number(
            data[payer]
        )

        dose_mg = convert_to_mg(
            entry["dose"],
            entry["unit"]
        )

        units = math.ceil(
            dose_mg / billing_unit
        )

        total_cost += units * cost

        total_allowed += units * allowable

    if missing:
        st.warning(
            "Missing drugs: " +
            ", ".join(missing)
        )

    primary_payment = (
        total_allowed *
        (primary_pct / 100)
    )

    remaining = (
        total_allowed -
        primary_payment
    )

    if has_secondary:
        secondary_payment = remaining
        patient_payment = copay

    else:
        secondary_payment = 0
        patient_payment = remaining + copay

    st.session_state.summary = {
        "cost": total_cost,
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

    c1.metric(
        "Total Cost",
        f"${s['cost']:,.2f}"
    )

    c2.metric(
        "Primary Pays",
        f"${s['primary']:,.2f}"
    )

    c3.metric(
        "Patient Pays",
        f"${s['patient']:,.2f}"
    )

    if has_secondary:
        st.metric(
            "Secondary Pays",
            f"${s['secondary']:,.2f}"
        )

    st.subheader("🧾 Summary")

    st.markdown(f"""
**Provider:** {provider}  
**Treatment Date:** {format_date_us(treatment_date)}  
**Date of Birth:** {format_date_us(dob)}  

**Total Cost:** ${s['cost']:,.2f}  
**Primary Insurance Pays:** ${s['primary']:,.2f}  
**Secondary Insurance Pays:** ${s['secondary']:,.2f}  
**Patient Responsibility:** ${s['patient']:,.2f}
""")

    pdf = generate_pdf([
        f"Total Cost: ${s['cost']:,.2f}",
        f"Primary: ${s['primary']:,.2f}",
        f"Patient: ${s['patient']:,.2f}"
    ])

    st.download_button(
        "📄 Download PDF",
        pdf,
        "report.pdf"
    )
