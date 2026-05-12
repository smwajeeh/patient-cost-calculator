import streamlit as st
import pandas as pd
import math
import re
from datetime import date, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

# -----------------------------------
# SAMPLE PROVIDERS
# -----------------------------------
providers = [
    "Dr. Smith",
    "Dr. Raza",
    "Dr. Johnson",
    "Dr. Williams"
]

# -----------------------------------
# SESSION STATE
# -----------------------------------
if "meds" not in st.session_state:
    st.session_state.meds = [
        {
            "drug": "Select Drug",
            "dose": "",
            "units": 1
        }
    ]

# -----------------------------------
# PAGE TITLE
# -----------------------------------
st.title("Patient Cost Calculator")

# -----------------------------------
# DATE VARIABLES
# -----------------------------------
today = date.today()
max_dob = today - timedelta(days=1)
min_dob = date(1900, 1, 1)
default_dob = date(2000, 1, 1)

# -----------------------------------
# LAYOUT
# -----------------------------------
c1, c2, c3 = st.columns(3)

# -----------------------------------
# COLUMN 1
# -----------------------------------
with c1:
    patient_name = st.text_input("Patient Name")

    dob = st.date_input(
        "Date of Birth",
        value=default_dob,
        min_value=min_dob,
        max_value=max_dob,
        help="Select a birth date between 01-01-1900 and yesterday."
    )

# -----------------------------------
# COLUMN 2
# -----------------------------------
with c2:
    provider = st.selectbox("Provider", providers)

    treatment_date = st.date_input(
        "Date of Treatment",
        value=today
    )

# -----------------------------------
# COLUMN 3
# -----------------------------------
with c3:
    location = st.selectbox(
        "Clinic Location",
        ["Downtown", "Live Oak", "Mission Trail", "Stone Oak"]
    )

# -----------------------------------
# VALIDATION
# -----------------------------------
if dob is None:
    st.error("Select a valid date of birth.")
    st.stop()

if dob < min_dob or dob > max_dob:
    st.error("Date of birth must be between 01-01-1900 and yesterday.")
    st.stop()

# -----------------------------------
# MEDICATION SECTION
# -----------------------------------
st.subheader("Medications")

drug_options = [
    "Select Drug",
    "Opdivo",
    "Keytruda",
    "Tecentriq",
    "Yervoy"
]

total_allowed = 0
missing = []

for i, entry in enumerate(st.session_state.meds):

    st.markdown(f"### Medication {i + 1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        entry["drug"] = st.selectbox(
            "Drug",
            drug_options,
            index=drug_options.index(entry["drug"])
            if entry["drug"] in drug_options
            else 0,
            key=f"drug_{i}"
        )

    with col2:
        entry["dose"] = st.text_input(
            "Dose",
            value=entry["dose"],
            key=f"dose_{i}"
        )

    with col3:
        entry["units"] = st.number_input(
            "Units",
            min_value=1,
            value=entry["units"],
            step=1,
            key=f"units_{i}"
        )

    # Validation
    if entry["drug"] == "Select Drug":
        missing.append(f"Medication {i + 1}: Drug not selected")

    if str(entry["dose"]).strip() == "":
        missing.append(f"Medication {i + 1}: Dose missing")

# -----------------------------------
# ADD MED BUTTON
# -----------------------------------
if st.button("Add Medication"):
    st.session_state.meds.append(
        {
            "drug": "Select Drug",
            "dose": "",
            "units": 1
        }
    )
    st.rerun()

# -----------------------------------
# CALCULATE BUTTON
# -----------------------------------
if st.button("Calculate"):

    if patient_name.strip() == "":
        missing.append("Patient Name missing")

    if len(missing) > 0:
        st.error("Please fix the following issues:")

        for item in missing:
            st.write(f"- {item}")

        st.stop()

    # -----------------------------------
    # SAMPLE CALCULATION
    # -----------------------------------
    total_allowed = 0

    for entry in st.session_state.meds:

        # Dummy pricing logic
        if entry["drug"] == "Opdivo":
            total_allowed += 1500 * entry["units"]

        elif entry["drug"] == "Keytruda":
            total_allowed += 1800 * entry["units"]

        elif entry["drug"] == "Tecentriq":
            total_allowed += 1400 * entry["units"]

        elif entry["drug"] == "Yervoy":
            total_allowed += 2200 * entry["units"]

    # -----------------------------------
    # RESULTS
    # -----------------------------------
    st.success("Calculation Complete")

    st.write("### Patient Information")
    st.write(f"**Patient Name:** {patient_name}")
    st.write(f"**DOB:** {dob}")
    st.write(f"**Provider:** {provider}")
    st.write(f"**Treatment Date:** {treatment_date}")
    st.write(f"**Location:** {location}")

    st.write("### Total Allowed Amount")
    st.write(f"${total_allowed:,.2f}")

    # -----------------------------------
    # PDF GENERATION
    # -----------------------------------
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("Patient Cost Calculator Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Patient Name: {patient_name}", styles["BodyText"]))
    story.append(Paragraph(f"DOB: {dob}", styles["BodyText"]))
    story.append(Paragraph(f"Provider: {provider}", styles["BodyText"]))
    story.append(Paragraph(f"Treatment Date: {treatment_date}", styles["BodyText"]))
    story.append(Paragraph(f"Location: {location}", styles["BodyText"]))

    story.append(Spacer(1, 12))

    for entry in st.session_state.meds:
        story.append(
            Paragraph(
                f"Drug: {entry['drug']} | Dose: {entry['dose']} | Units: {entry['units']}",
                styles["BodyText"]
            )
        )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            f"Total Allowed Amount: ${total_allowed:,.2f}",
            styles["Heading2"]
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    st.download_button(
        label="Download PDF Report",
        data=pdf,
        file_name="patient_cost_report.pdf",
        mime="application/pdf"
    )
