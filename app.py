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

/* Hide Streamlit UI */
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Header */
.header {
    background-color: #6B7F4E;
    padding: 12px;
    border-radius: 8px;
    color: white;
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 15px;
}

/* Smaller buttons */
.stButton>button {
    background-color: #6B7F4E;
    color: white;
    border-radius: 6px;
    height: 35px;
    font-size: 13px;
    padding: 0px 10px;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">💊 Patient Treatment ffdfefe Cost Calculator</div>', unsafe_allow_html=True)

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
df["Drug_Name_Clean"] = df["Drug_Name"].astype(str).str.strip().str.lower()

base_columns = ["J_Code", "Drug_Name", "Billing_Unit", "Cost_per_Unit"]
payer_columns = sorted([c for c in df.columns if c not in base_columns])

drug_list = ["Select Drug"] + sorted(df["Drug_Name"].dropna().unique())

# -------------------------
# SESSION INIT
# -------------------------
if "meds" not in st.session_state:
    st.session_state.meds = [{"drug": "Select Drug", "dose": 0.0, "unit": "mg"}]

# -------------------------
# MEDICATION SECTION
# -------------------------
st.subheader("💉 Medications")

new_meds = []

for i, med in enumerate(st.session_state.meds):

    st.markdown(f"**Medication {i+1}**")

    col1, col2, col3, col4 = st.columns([3,2,2,1])

    drug = col1.selectbox("Drug", drug_list, index=drug_list.index(med["drug"]) if med["drug"] in drug_list else 0, key=f"drug{i}")
    dose = col2.number_input("Dose", min_value=0.0, value=med["dose"], key=f"dose{i}")
    unit = col3.selectbox("Units", ["mg", "mcg", "units"], index=["mg","mcg","units"].index(med["unit"]), key=f"unit{i}")

    # Remove button only if more than 1 med
    remove_clicked = False
    if len(st.session_state.meds) > 1:
        remove_clicked = col4.button("❌", key=f"remove{i}")

    if not remove_clicked:
        new_meds.append({"drug": drug, "dose": dose, "unit": unit})

st.session_state.meds = new_meds

# -------------------------
# ADD BUTTON (moves down dynamically)
# -------------------------
if st.button("➕ Add Medication"):
    st.session_state.meds.append({"drug": "Select Drug", "dose": 0.0, "unit": "mg"})
    st.rerun()

# -------------------------
# RESET BUTTON (conditional enable)
# -------------------------
any_selected = any(m["drug"] != "Select Drug" for m in st.session_state.meds)

if st.button("🔄 Reset Medications", disabled=not any_selected):
    st.session_state.meds = [{"drug": "Select Drug", "dose": 0.0, "unit": "mg"}]
    st.rerun()
