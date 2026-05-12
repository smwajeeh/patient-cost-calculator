import streamlit as st
import pandas as pd
import math
import re
from datetime import date, timedelta
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Patient Treatment Cost Calculator",
    page_icon="💊",
    layout="wide"
)

# ---------------------------------------------------
# PROFESSIONAL MODERN UI
# ---------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main Background */

.stApp {
    background: linear-gradient(
        180deg,
        #f4f7ff 0%,
        #edf3ff 100%
    );
}

/* Hide Streamlit */

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

/* Main Layout */

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* HERO */

.hero {

    background: linear-gradient(
        135deg,
        #ffffff 0%,
        #f7f9ff 100%
    );

    border-radius: 28px;

    padding: 45px;

    margin-bottom: 30px;

    border: 1px solid #e8eeff;

    box-shadow:
        0 10px 40px rgba(0,0,0,0.05);
}

.hero-title {

    font-size: 48px;

    font-weight: 800;

    color: #14213d;

    margin-bottom: 12px;
}

.hero-subtitle {

    font-size: 18px;

    color: #6b7280;
}

/* Sections */

.section {

    background: rgba(255,255,255,0.88);

    border-radius: 24px;

    padding: 30px;

    margin-bottom: 24px;

    border: 1px solid #e9efff;

    box-shadow:
        0 6px 24px rgba(0,0,0,0.04);
}

/* Headers */

.section h3 {

    color: #315eff;

    font-size: 32px;

    font-weight: 700;

    margin-bottom: 25px;
}

/* Labels */

label {
    color: #334155 !important;
    font-weight: 600 !important;
}

/* Inputs */

.stTextInput input,
.stNumberInput input,
.stDateInput input {

    background: white !important;

    color: #14213d !important;

    border: 1px solid #dbe4ff !important;

    border-radius: 14px !important;

    padding: 12px !important;
}

/* Select */

.stSelectbox > div > div {

    background: white !important;

    border: 1px solid #dbe4ff !important;

    border-radius: 14px !important;
}

/* Buttons */

.stButton > button,
.stDownloadButton > button {

    background: linear-gradient(
        135deg,
        #4c6fff,
        #315eff
    ) !important;

    color: white !important;

    border: none !important;

    border-radius: 14px !important;

    padding: 0.8rem 1.5rem !important;

    font-weight: 700 !important;

    box-shadow:
        0 8px 24px rgba(76,111,255,0.25);
}

.stButton > button:hover {

    transform: translateY(-2px);
}

/* Metrics */

[data-testid="metric-container"] {

    background: white;

    border-radius: 20px;

    padding: 22px;

    border: 1px solid #e8eeff;

    box-shadow:
        0 6px 24px rgba(0,0,0,0.04);
}

[data-testid="stMetricLabel"] {

    color: #64748b;

    font-weight: 600;
}

[data-testid="stMetricValue"] {

    color: #315eff;

    font-weight: 800;
}

/* Slider */

.stSlider > div > div > div > div {
    background-color: #4c6fff !important;
}

/* Remove weird dark controls */

button.step-up,
button.step-down {
    background: white !important;
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HERO
# ---------------------------------------------------

st.markdown("""
<div class="hero">

    <div class="hero-title">
        💊 Patient Treatment Cost Calculator
    </div>

    <div class="hero-subtitle">
        Accurate estimates for informed healthcare decisions
    </div>

</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def extract_number(value):

    if pd.isna(value):
        return 0.0

    number = re.findall(
        r"[\d\.]+",
        str(value)
    )

    return float(number[0]) if number else 0.0


def convert_to_mg(dose, unit):

    dose = float(dose)

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
        Paragraph(
            "Patient Treatment Cost Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 12))

    for line in data:

        content.append(
            Paragraph(
                str(line),
                styles["Normal"]
            )
        )

        content.append(Spacer(1, 8))

    doc.build(content)

    buffer.seek(0)

    return buffer

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

try:

    df = pd.read_excel("drug_data.xlsx")

except Exception as e:

    st.error(f"Unable to load drug_data.xlsx: {e}")

    st.stop()

df.columns = df.columns.str.strip()

required_cols = [
    "Drug_Name",
    "Billing_Unit",
    "Cost_per_Unit"
]

missing_cols = [
    c for c in required_cols
    if c not in df.columns
]

if missing_cols:

    st.error(
        f"Missing required columns: {', '.join(missing_cols)}"
    )

    st.stop()

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
    df["Drug_Name"]
    .dropna()
    .astype(str)
    .unique()
)

unit_list = [
    "mgs",
    "mcgs",
    "units"
]

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "meds" not in st.session_state:

    st.session_state.meds = [{
        "drug": "Select Drug",
        "dose": 0.0,
        "unit": "mgs"
    }]

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

# ---------------------------------------------------
# PATIENT INFO
# ---------------------------------------------------

st.markdown('<div class="section">', unsafe_allow_html=True)

st.markdown("<h3>🧑 Patient Information</h3>", unsafe_allow_html=True)

providers = sorted([
    "Navneet Mittal MD",
    "Sreecharan Mavuram MD",
    "Syed Raza MD"
])

today = date.today()

max_dob = today - timedelta(days=1)

min_dob = date(1900, 1, 1)

default_dob = date(2000, 1, 1)

c1, c2, c3 = st.columns(3)

with c1:

    patient_name = st.text_input(
        "Patient Name"
    )

    dob = st.date_input(
        "Date of Birth",
        value=default_dob,
        min_value=min_dob,
        max_value=max_dob
    )

with c2:

    provider = st.selectbox(
        "Provider",
        providers
    )

    treatment_date = st.date_input(
        "Date of Treatment",
        value=today
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

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# INSURANCE
# ---------------------------------------------------

st.markdown('<div class="section">', unsafe_allow_html=True)

st.markdown("<h3>🏥 Insurance</h3>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:

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

with c2:

    copay = st.number_input(
        "Copay",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# MEDICATIONS
# ---------------------------------------------------

st.markdown('<div class="section">', unsafe_allow_html=True)

st.markdown("<h3>💉 Medications</h3>", unsafe_allow_html=True)

if st.button("➕ Add Medication"):

    st.session_state.meds.append({
        "drug": "Select Drug",
        "dose": 0.0,
        "unit": "mgs"
    })

    st.rerun()

updated = []

for i, med in enumerate(
    st.session_state.meds
):

    c1, c2, c3 = st.columns([4,2,2])

    current_drug = str(
        med.get("drug", "Select Drug")
    )

    current_dose = float(
        med.get("dose", 0.0)
    )

    current_unit = str(
        med.get("unit", "mgs")
    )

    drug = c1.selectbox(
        "Drug",
        drug_list,
        index=(
            drug_list.index(current_drug)
            if current_drug in drug_list
            else 0
        ),
        key=f"d{i}"
    )

    dose = c2.number_input(
        "Dose",
        min_value=0.0,
        value=float(current_dose),
        step=1.0,
        key=f"ds{i}"
    )

    unit = c3.selectbox(
        "Units",
        unit_list,
        index=(
            unit_list.index(current_unit)
            if current_unit in unit_list
            else 0
        ),
        key=f"u{i}"
    )

    updated.append({
        "drug": drug,
        "dose": float(dose),
        "unit": unit
    })

st.session_state.meds = updated

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# CALCULATE
# ---------------------------------------------------

if st.button("🧮 Calculate"):

    total_cost = 0.0

    total_allowed = 0.0

    for entry in st.session_state.meds:

        drug_name = str(
            entry.get("drug", "")
        ).strip()

        dose_value = float(
            entry.get("dose", 0.0)
        )

        unit_value = str(
            entry.get("unit", "")
        ).strip()

        if drug_name == "Select Drug":
            continue

        filtered = df[
            df["Drug_Name_Clean"]
            == drug_name.lower()
        ]

        if filtered.empty:
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
            dose_value,
            unit_value
        )

        units = math.ceil(
            dose_mg / billing_unit
        )

        total_cost += units * cost

        total_allowed += units * allowable

    primary_payment = (
        total_allowed
        * (primary_pct / 100)
    )

    patient_payment = (
        total_allowed
        - primary_payment
        + copay
    )

    st.session_state.summary = {
        "cost": total_cost,
        "primary": primary_payment,
        "patient": patient_payment
    }

    st.session_state.show_summary = True

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------

if st.session_state.show_summary:

    s = st.session_state.summary

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.markdown("<h3>💰 Financial Summary</h3>", unsafe_allow_html=True)

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

    pdf = generate_pdf([
        f"Patient Name: {patient_name}",
        f"Provider: {provider}",
        f"Location: {location}",
        f"Total Cost: ${s['cost']:,.2f}",
        f"Primary Pays: ${s['primary']:,.2f}",
        f"Patient Pays: ${s['patient']:,.2f}"
    ])

    st.download_button(
        "📄 Download PDF Report",
        pdf,
        "patient_treatment_report.pdf"
    )

    st.markdown("</div>", unsafe_allow_html=True)
