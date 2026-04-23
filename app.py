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

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_excel("drug_data.xlsx")
df.columns = df.columns.str.strip()
df["Drug_Name_Clean"] = df["Drug_Name"].astype(str).str.strip().str.lower()

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
# MEDICATIONS
# -------------------------
st.subheader("💉 Medications")

new_meds = []

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
    delete = col4.button("Delete 🗑️", key=f"delete{i}")

    # Detect changes → clear summary
    if drug != med["drug"] or dose != med["dose"] or unit != med["unit"]:
        st.session_state.show_summary = False

    # -------- DELETE LOGIC --------
    if delete:
        st.session_state.show_summary = False

        if i == 0:
            # reset only
            st.session_state.meds[0] = {
                "drug": "Select Drug",
                "dose": 0.0,
                "unit": ""
            }
        else:
            # delete row
            st.session_state.meds.pop(i)

        st.rerun()

    else:
        new_meds.append({"drug": drug, "dose": dose, "unit": unit})

# keep updated state
st.session_state.meds = new_meds if new_meds else [{"drug": "Select Drug", "dose": 0.0, "unit": "mgs"}]

# Add medication
if st.button("➕ Add Medication"):
    st.session_state.meds.append({"drug": "Select Drug", "dose": 0.0, "unit": "mgs"})
    st.session_state.show_summary = False
    st.rerun()

# -------------------------
# CALCULATE
# -------------------------
if st.button("Calculate"):

    total_cost = 0
    total_allowed = 0

    for entry in st.session_state.meds:

        if entry["drug"] == "Select Drug":
            st.error("Please select a drug")
            st.stop()

        if entry["dose"] <= 0:
            st.error("Invalid dose")
            st.stop()

        if entry["unit"] == "":
            st.error("Select units")
            st.stop()

        data = df[df["Drug_Name_Clean"] == entry["drug"].lower()].iloc[0]

        billing_unit = extract_number(data["Billing_Unit"])
        cost = extract_number(data["Cost_per_Unit"])
        allowable = extract_number(data[df.columns[4]])

        dose_mg = convert_to_mg(entry["dose"], entry["unit"])
        units = math.ceil(dose_mg / billing_unit)

        total_cost += units * cost
        total_allowed += units * allowable

    st.session_state.total_cost = total_cost
    st.session_state.total_allowed = total_allowed
    st.session_state.show_summary = True

# -------------------------
# SUMMARY
# -------------------------
if st.session_state.show_summary:

    st.subheader("💰 Financial Summary")

    st.metric("Total Cost", f"${st.session_state.total_cost:,.2f}")
    st.metric("Allowed Amount", f"${st.session_state.total_allowed:,.2f}")
