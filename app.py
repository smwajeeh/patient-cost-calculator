{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww28800\viewh13640\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
\
st.title("Patient Treatment Cost Calculator")\
\
# Upload Excel\
uploaded_file = st.file_uploader("Upload Drug Data Excel", type=["xlsx"])\
\
if uploaded_file:\
    df = pd.read_excel(uploaded_file)\
\
    st.success("File uploaded successfully")\
\
    # Select Drug\
    drug = st.selectbox("Select Drug", df["Drug_Name"].unique())\
\
    drug_data = df[df["Drug_Name"] == drug].iloc[0]\
\
    dose = st.number_input("Enter Dose", min_value=0.0)\
\
    cost_per_unit = drug_data["Cost_per_Unit"]\
    reimbursement_per_unit = drug_data["Reimbursement_per_Unit"]\
\
    # Insurance Inputs\
    st.subheader("Insurance Information")\
\
    primary_coverage = st.slider("Primary Coverage %", 0, 100, 80) / 100\
\
    has_secondary = st.checkbox("Has Secondary Insurance")\
\
    secondary_coverage = 0\
    if has_secondary:\
        secondary_coverage = st.slider("Secondary Coverage %", 0, 100, 20) / 100\
\
    copay = st.number_input("Copay ($)", min_value=0.0)\
\
    if st.button("Calculate"):\
\
        # Calculations\
        total_cost = dose * cost_per_unit\
        allowed = dose * reimbursement_per_unit\
\
        primary_payment = allowed * primary_coverage\
        remaining = allowed - primary_payment\
\
        secondary_payment = remaining * secondary_coverage\
        patient_responsibility = remaining - secondary_payment + copay\
\
        # Output\
        st.subheader("Results")\
\
        st.write(f"Total Drug Cost: $\{total_cost:,.2f\}")\
        st.write(f"Allowed Amount: $\{allowed:,.2f\}")\
        st.write(f"Primary Insurance Pays: $\{primary_payment:,.2f\}")\
        st.write(f"Secondary Insurance Pays: $\{secondary_payment:,.2f\}")\
        st.write(f"Patient Responsibility: $\{patient_responsibility:,.2f\}")}