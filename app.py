import streamlit as st
import pandas as pd
import math
import re
from datetime import date, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(
    page_title="Treatment Cost Calculator",
    page_icon="💊",
    layout="wide"
)

# ---------------------------------------------------
# MODERN HEALTHCARE THEME
# ---------------------------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f4f7fc;
    --card: rgba(255,255,255,0.92);
    --card-strong: #ffffff;
    --text: #172b4d;
    --muted: #6b7a90;
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-light: #dbeafe;
    --success: #16a34a;
    --danger: #dc2626;
    --border: rgba(148, 163, 184, 0.25);

    --shadow:
        0 10px 30px rgba(15, 23, 42, 0.08);

    --radius: 20px;
}

/* Hide Streamlit junk */

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
        radial-gradient(circle at top left,
            rgba(37,99,235,0.08),
            transparent 28%),

        radial-gradient(circle at top right,
            rgba(14,165,233,0.10),
            transparent 24%),

        linear-gradient(
            180deg,
            #f8fbff 0%,
            #eef4ff 100%
        );
}

/* Container */

[data-testid="stAppViewContainer"] > .main {
    background: transparent;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1250px;
}

/* Header */

.main-header {
    background:
        linear-gradient(
            135deg,
            #2563eb 0%,
            #1d4ed8 100%
        );

    padding: 32px;
    border-radius: 28px;

    color: white;

    margin-bottom: 1.5rem;

    box-shadow:
        0 18px 40px rgba(37,99,235,0.25);

    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: "";
    position: absolute;

    width: 280px;
    height: 280px;

    background: rgba(255,255,255,0.08);

    border-radius: 50%;

    top: -120px;
    right: -80px;
}

.main-title {
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -0.04em;
    position: relative;
    z-index: 2;
}

.main-subtitle {
    margin-top: 8px;
    opacity: 0.92;
    font-size: 15px;
    position: relative;
    z-index: 2;
}

/* Cards */

[data-testid="stVerticalBlock"] > div {
    background: var(--card);

    border: 1px solid var(--border);

    border-radius: var(--radius);

    padding: 1.35rem;

    margin-bottom: 1rem;

    box-shadow: var(--shadow);

    backdrop-filter: blur(10px);
}

/* Remove card from first element */

[data-testid="stVerticalBlock"] > div:first-child {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
}

/* Typography */

h1,
h2,
h3,
.stSubheader {
    color: var(--text);
    font-weight: 700;
    letter-spacing: -0.03em;
}

label,
p,
span,
li {
    color: var(--text);
}

/* Inputs */

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
.stDateInput > div > div,
.stNumberInput > div > div {

    background: var(--card-strong);

    border: 1px solid #dbe3f0;

    border-radius: 14px;

    transition: all 0.18s ease;
}

div[data-baseweb="input"] input,
.stDateInput input,
.stNumberInput input {
    color: var(--text);
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:focus-within,
.stDateInput > div > div:focus-within,
.stNumberInput > div > div:focus-within {

    border-color: var(--primary);

    box-shadow:
        0 0 0 4px rgba(37,99,235,0.12);
}

/* Buttons */

.stButton > button,
.stDownloadButton > button {

    background:
        linear-gradient(
            135deg,
            var(--primary) 0%,
            var(--primary-dark) 100%
        );

    color: white;

    border: none;

    border-radius: 14px;

    padding: 0.72rem 1.2rem;

    font-weight: 700;

    transition: all 0.18s ease;

    box-shadow:
        0 10px 24px rgba(37,99,235,0.24);
}

.stButton > button:hover,
.stDownloadButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 16px 30px rgba(37,99,235,0.30);
}

/* Delete Button */

button[kind="secondary"] {

    background:
        linear-gradient(
            135deg,
            #ef4444,
            #dc2626
        ) !important;

    color: white !important;
}

/* Metrics */

[data-testid="stMetric"] {

    background:
        linear-gradient(
            180deg,
            #ffffff 0%,
            #f8fbff 100%
        );

    border: 1px solid #e5edf8;

    border-radius: 20px;

    padding: 1rem;

    box-shadow:
        0 8px 20px rgba(15,23,42,0.05);
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: var(--primary-dark);
    font-weight: 800;
    letter-spacing: -0.04em;
}

/* Alerts */

.stAlert {
    border-radius: 16px;
    border: 1px solid rgba(148,163,184,0.2);
}

/* Slider */

.stSlider [data-baseweb="slider"] [role="slider"] {
    background-color: var(--primary);
}

.stSlider [data-baseweb="slider"] > div > div {
    background-color: rgba(37,99,235,0.2);
}

/* Scrollbar */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 20px;
}

::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <div class="main-title">
        💊 Patient Treatment Cost Calculator
    </div>

    <div class="main-subtitle">
        Modern healthcare financial estimation dashboard
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def extract_number(value):

    if pd.isna(value):
        return 0.0

    number = re.findall(r"[\d\.]+", str(value))

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

updated = []

for i, med in enumerate(
    st.session_state.meds
):

    col1, col2, col3, col4 = st.columns(
        [3, 2, 2, 1.5]
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
        "Delete 🗑️",
        key=f"del{i}"
    )

    if (
        drug != current_drug
        or float(dose) != float(current_dose)
        or unit != current_unit
    ):
        st.session_state.show_summary = False

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

if st.button("➕ Add Medication"):

    st.session_state.meds.append({
        "drug": "Select Drug",
        "dose": float(0.0),
        "unit": "mgs"
    })

    st.session_state.show_summary = False

    st.rerun()

# ---------------------------------------------------
# CALCULATE
# ---------------------------------------------------

if st.button("Calculate"):

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
**Patient Name:** {patient_name}

**Provider:** {provider}

**Treatment Date:** {format_date_us(treatment_date)}

**Date of Birth:** {format_date_us(dob)}

**Location:** {location}

**Primary Insurance:** {payer}

**Total Cost:** ${s['cost']:,.2f}

**Primary Insurance Pays:** ${s['primary']:,.2f}

**Secondary Insurance Pays:** ${s['secondary']:,.2f}

**Patient Responsibility:** ${s['patient']:,.2f}
""")

    pdf = generate_pdf([
        f"Patient Name: {patient_name}",
        f"Provider: {provider}",
        f"Treatment Date: {format_date_us(treatment_date)}",
        f"Date of Birth: {format_date_us(dob)}",
        f"Location: {location}",
        f"Primary Insurance: {payer}",
        f"Total Cost: ${s['cost']:,.2f}",
        f"Primary Insurance Pays: ${s['primary']:,.2f}",
        f"Secondary Insurance Pays: ${s['secondary']:,.2f}",
        f"Patient Responsibility: ${s['patient']:,.2f}"
    ])

    st.download_button(
        "📄 Download PDF",
        pdf,
        "report.pdf"
    )
