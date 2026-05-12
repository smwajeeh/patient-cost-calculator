import streamlit as st
import pandas as pd
import math
import re
from datetime import date, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Patient Treatment Cost Calculator",
    page_icon="💊",
    layout="wide"
)

# ---------------------------------------------------
# MODERN MEDICAL UI THEME
# ---------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {

    --bg: #f4f7fc;

    --card: rgba(255,255,255,0.90);

    --white: #ffffff;

    --text: #14213d;

    --muted: #6b7280;

    --primary: #4f7cff;

    --primary-dark: #3b63dd;

    --primary-soft: #eef3ff;

    --success: #18b368;

    --danger: #ff5c5c;

    --purple: #8b5cf6;

    --border: rgba(226,232,240,0.95);

    --shadow:
        0 10px 35px rgba(15,23,42,0.06);

    --radius: 24px;
}

/* Hide Streamlit Branding */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    display: none !important;
}

/* Global */

html,
body,
[class*="css"] {

    font-family: 'Inter', sans-serif;

    color: var(--text);
}

.stApp {

    background:
        linear-gradient(
            180deg,
            #f8fbff 0%,
            #edf3ff 100%
        );
}

/* Layout */

.block-container {

    max-width: 1280px;

    padding-top: 2rem !important;

    padding-bottom: 4rem !important;
}

/* Main Header */

.hero {

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.96),
            rgba(255,255,255,0.82)
        );

    border-radius: 32px;

    padding: 34px;

    border: 1px solid rgba(255,255,255,0.75);

    box-shadow: var(--shadow);

    position: relative;

    overflow: hidden;

    margin-bottom: 1.6rem;

    backdrop-filter: blur(12px);
}

.hero::before {

    content: "";

    position: absolute;

    width: 420px;

    height: 420px;

    background:
        radial-gradient(
            circle,
            rgba(79,124,255,0.12),
            transparent 70%
        );

    top: -180px;

    right: -120px;
}

.hero-title {

    font-size: 44px;

    font-weight: 800;

    color: var(--text);

    letter-spacing: -0.05em;

    position: relative;

    z-index: 2;
}

.hero-sub {

    margin-top: 10px;

    color: var(--muted);

    font-size: 16px;

    position: relative;

    z-index: 2;
}

/* Cards */

[data-testid="stVerticalBlock"] > div {

    background: rgba(255,255,255,0.80);

    backdrop-filter: blur(14px);

    border-radius: 26px;

    border: 1px solid rgba(255,255,255,0.75);

    padding: 1.6rem;

    box-shadow: var(--shadow);

    margin-bottom: 1.2rem;
}

/* Remove card from first element */

[data-testid="stVerticalBlock"] > div:first-child {

    background: transparent;

    border: none;

    box-shadow: none;

    padding: 0;
}

/* Section Headers */

h1,
h2,
h3,
.stSubheader {

    color: var(--text);

    font-weight: 700;

    letter-spacing: -0.03em;
}

/* Inputs */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
.stDateInput > div > div,
.stNumberInput > div > div {

    background: rgba(255,255,255,0.92);

    border: 1px solid #dfe7f5;

    border-radius: 16px;

    min-height: 52px;

    transition: all 0.18s ease;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:focus-within,
.stDateInput > div > div:focus-within,
.stNumberInput > div > div:focus-within {

    border-color: var(--primary);

    box-shadow:
        0 0 0 4px rgba(79,124,255,0.12);
}

div[data-baseweb="input"] input,
.stNumberInput input,
.stDateInput input {

    color: var(--text);
}

/* Buttons */

.stButton > button,
.stDownloadButton > button {

    background:
        linear-gradient(
            135deg,
            var(--primary),
            var(--primary-dark)
        );

    color: white;

    border: none;

    border-radius: 16px;

    padding: 0.72rem 1.4rem;

    font-weight: 700;

    transition: all 0.18s ease;

    box-shadow:
        0 12px 24px rgba(79,124,255,0.22);
}

.stButton > button:hover,
.stDownloadButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 18px 32px rgba(79,124,255,0.28);
}

/* Delete Buttons */

button[kind="secondary"] {

    background:
        linear-gradient(
            135deg,
            #ff7a7a,
            #ff5c5c
        ) !important;

    color: white !important;
}

/* Metrics */

[data-testid="stMetric"] {

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.92),
            rgba(248,251,255,0.88)
        );

    border-radius: 22px;

    border: 1px solid rgba(226,232,240,0.9);

    padding: 1rem;

    box-shadow:
        0 8px 24px rgba(15,23,42,0.04);
}

[data-testid="stMetricLabel"] {

    color: var(--muted);

    font-weight: 600;
}

[data-testid="stMetricValue"] {

    color: var(--primary-dark);

    font-weight: 800;

    letter-spacing: -0.03em;
}

/* Slider */

.stSlider [data-baseweb="slider"] [role="slider"] {

    background-color: var(--primary);
}

.stSlider [data-baseweb="slider"] > div > div {

    background-color:
        rgba(79,124,255,0.20);
}

/* Alerts */

.stAlert {

    border-radius: 18px;

    border: 1px solid rgba(226,232,240,0.9);
}

/* Scrollbar */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {

    background: #cfd8ea;

    border-radius: 20px;
}

::-webkit-scrollbar-thumb:hover {

    background: #a8b6d6;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HERO SECTION
# ---------------------------------------------------

st.markdown("""
<div class="hero">

    <div class="hero-title">
        💊 Patient Treatment Cost Calculator
    </div>

    <div class="hero-sub">
        Accurate treatment estimates for informed healthcare decisions
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

    df = pd.read_excel(
        "drug_data.xlsx"
    )

except Exception as e:

    st.error(
        f"Unable to load drug_data.xlsx: {e}"
    )

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
        "dose": float(0.0),
        "unit": "mgs"
    }]

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

# ---------------------------------------------------
# PATIENT INFO
# ---------------------------------------------------

st.subheader("🧑 Patient Information")

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

# ---------------------------------------------------
# INSURANCE
# ---------------------------------------------------

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
    min_value=0.0,
    value=0.0,
    step=1.0
)

has_secondary = st.checkbox(
    "Has Secondary Insurance"
)

secondary_selected = None
secondary_text = ""

if has_secondary:

    options = (
        ["Select"]
        + payer_columns
        + ["Other / Funding"]
    )

    secondary_selected = st.selectbox(
        "Secondary Insurance",
        options
    )

    if secondary_selected == "Other / Funding":

        secondary_text = st.text_input(
            "Other / Funding Details"
        )

# ---------------------------------------------------
# MEDICATIONS
# ---------------------------------------------------

st.subheader("💉 Medications")

any_selected = any(
    m["drug"] != "Select Drug"
    for m in st.session_state.meds
)

colA, colB = st.columns([1,1])

with colA:

    if st.button(
        "🔄 Reset Medications",
        disabled=not any_selected
    ):

        st.session_state.meds = [{
            "drug": "Select Drug",
            "dose": float(0.0),
            "unit": "mgs"
        }]

        st.session_state.show_summary = False

        st.rerun()

with colB:

    if st.button("➕ Add Medication"):

        st.session_state.meds.append({
            "drug": "Select Drug",
            "dose": float(0.0),
            "unit": "mgs"
        })

        st.session_state.show_summary = False

        st.rerun()

updated = []

for i, med in enumerate(
    st.session_state.meds
):

    col1, col2, col3, col4 = st.columns(
        [4,2,2,1]
    )

    current_drug = str(
        med.get("drug", "Select Drug")
    )

    current_dose = float(
        med.get("dose", 0.0) or 0.0
    )

    current_unit = str(
        med.get("unit", "mgs")
    )

    if current_unit not in unit_list:
        current_unit = "mgs"

    drug = col1.selectbox(
        "Drug",
        drug_list,
        index=(
            drug_list.index(current_drug)
            if current_drug in drug_list
            else 0
        ),
        key=f"d{i}"
    )

    dose = col2.number_input(
        "Dose",
        min_value=0.0,
        value=float(current_dose),
        step=1.0,
        key=f"ds{i}"
    )

    unit = col3.selectbox(
        "Units",
        unit_list,
        index=(
            unit_list.index(current_unit)
            if current_unit in unit_list
            else 0
        ),
        key=f"u{i}"
    )

    col4.markdown("<br>", unsafe_allow_html=True)

    delete = col4.button(
        "🗑️",
        key=f"del{i}"
    )

    if delete:

        st.session_state.show_summary = False

        if i == 0:

            updated.append({
                "drug": "Select Drug",
                "dose": float(0.0),
                "unit": "mgs"
            })

        continue

    updated.append({
        "drug": drug,
        "dose": float(dose),
        "unit": unit
    })

if len(updated) == 0:

    updated = [{
        "drug": "Select Drug",
        "dose": float(0.0),
        "unit": "mgs"
    }]

st.session_state.meds = updated

# ---------------------------------------------------
# CALCULATE
# ---------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🧮 Calculate"):

    total_cost = 0.0

    total_allowed = 0.0

    missing = []

    for entry in st.session_state.meds:

        drug_name = str(
            entry.get("drug", "")
        ).strip()

        dose_value = float(
            entry.get("dose", 0.0) or 0.0
        )

        unit_value = str(
            entry.get("unit", "")
        ).strip()

        if drug_name == "Select Drug":

            st.error(
                "Please select a drug."
            )

            st.stop()

        if dose_value <= 0:

            st.error(
                f"Invalid dose for {drug_name}."
            )

            st.stop()

        filtered = df[
            df["Drug_Name_Clean"]
            == drug_name.lower()
        ]

        if filtered.empty:

            missing.append(drug_name)

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

        if billing_unit <= 0:

            st.error(
                f"Invalid billing unit for {drug_name}."
            )

            st.stop()

        dose_mg = convert_to_mg(
            dose_value,
            unit_value
        )

        units = math.ceil(
            dose_mg / billing_unit
        )

        total_cost += units * cost

        total_allowed += units * allowable

    if missing:

        st.warning(
            "Missing drugs: "
            + ", ".join(missing)
        )

    primary_payment = (
        total_allowed
        * (primary_pct / 100)
    )

    remaining = (
        total_allowed
        - primary_payment
    )

    if has_secondary:

        secondary_payment = remaining

        patient_payment = copay

    else:

        secondary_payment = 0.0

        patient_payment = (
            remaining + copay
        )

    st.session_state.summary = {
        "cost": float(total_cost),
        "primary": float(primary_payment),
        "secondary": float(secondary_payment),
        "patient": float(patient_payment)
    }

    st.session_state.show_summary = True

# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------

if st.session_state.show_summary:

    s = st.session_state.summary

    st.subheader(
        "💰 Financial Summary"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Cost",
        f"${s['cost']:,.2f}"
    )

    c2.metric(
        "Primary Pays",
        f"${s['primary']:,.2f}"
    )

    c3.metric(
        "Secondary Pays",
        f"${s['secondary']:,.2f}"
    )

    c4.metric(
        "Patient Pays",
        f"${s['patient']:,.2f}"
    )

    st.subheader("🧾 Summary Details")

    st.markdown(f"""
### Patient Information

- **Patient Name:** {patient_name}
- **Provider:** {provider}
- **Date of Birth:** {format_date_us(dob)}
- **Treatment Date:** {format_date_us(treatment_date)}
- **Clinic Location:** {location}

### Insurance

- **Primary Insurance:** {payer}
- **Coverage:** {primary_pct}%
- **Copay:** ${copay:,.2f}

### Financial Summary

- **Total Cost:** ${s['cost']:,.2f}
- **Primary Insurance Pays:** ${s['primary']:,.2f}
- **Secondary Insurance Pays:** ${s['secondary']:,.2f}
- **Patient Responsibility:** ${s['patient']:,.2f}
""")

    pdf = generate_pdf([
        f"Patient Name: {patient_name}",
        f"Provider: {provider}",
        f"Date of Birth: {format_date_us(dob)}",
        f"Treatment Date: {format_date_us(treatment_date)}",
        f"Clinic Location: {location}",
        f"Primary Insurance: {payer}",
        f"Coverage: {primary_pct}%",
        f"Copay: ${copay:,.2f}",
        f"Total Cost: ${s['cost']:,.2f}",
        f"Primary Pays: ${s['primary']:,.2f}",
        f"Secondary Pays: ${s['secondary']:,.2f}",
        f"Patient Pays: ${s['patient']:,.2f}"
    ])

    st.download_button(
        "📄 Download PDF Report",
        pdf,
        "patient_treatment_report.pdf"
    )
