import streamlit as st
import pandas as pd
import math
import re
from datetime import date

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

.stButton>button {
    background-color: #6B7F4E;
    color: white;
    border-radius: 6px;
    height: 35px;
    font-size: 13px;
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
    if unit == "mcg":
        return dose / 1000
    return dose

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
# MEDICATIONS
# -------------------------
st.subheader("💉 Medications")

# Reset button under heading
any_selected = any(m["drug"] != "Select Drug" for m in st.session_state.meds)

if st.button("🔄 Reset Medications", disabled=not any_selected):
    st.session_state.meds = [{"drug": "Select Drug", "dose": 0.0, "unit": "mg"}]
    st.rerun()

updated_meds = []

for i, med in enumerate(st.session_state.meds):

    title = "Medication" if len(st.session_state.meds) == 1 else f"Medication {i+1}"
    st.markdown(f"**{title}**")

    col1, col2, col3, col4 = st.columns([3,2,2,1.5])

    drug = col1.selectbox(
        "Drug",
        drug_list,
        index=drug_list.index(med["drug"]) if med["drug"] in drug_list else 0,
        key=f"drug{i}"
    )

    dose = col2.number_input(
        "Dose",
        min_value=0.0,
        value=med["dose"],
        key=f"dose{i}"
    )

    unit = col3.selectbox(
        "Units",
        ["mg", "mcg", "units"],
        index=["mg","mcg","units"].index(med["unit"]),
        key=f"unit{i}"
    )

    # 👇 ALIGN DELETE BUTTON WITH INPUT ROW
    col4.markdown("<br>", unsafe_allow_html=True)
    delete_clicked = col4.button("Delete 🗑️", key=f"delete{i}")

    if not delete_clicked:
        updated_meds.append({"drug": drug, "dose": dose, "unit": unit})

# Always keep at least 1 row
if len(updated_meds) == 0:
    updated_meds = [{"drug": "Select Drug", "dose": 0.0, "unit": "mg"}]

st.session_state.meds = updated_meds

# Add button (below meds)
if st.button("➕ Add Medication"):
    st.session_state.meds.append({"drug": "Select Drug", "dose": 0.0, "unit": "mg"})
    st.rerun()
