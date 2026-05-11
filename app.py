
import pandas as pd
import math
import re
from datetime import date
from datetime import date, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
])

c1, c2, c3 = st.columns(3)
today = date.today()
max_dob = today - timedelta(days=1)
min_dob = date(1900, 1, 1)
default_dob = date(2000, 1, 1)

with c1:
    patient_name = st.text_input("Patient Name")
    dob = st.date_input("Date of Birth", max_value=date.today())
    dob = st.date_input(
        "Date of Birth",
        value=default_dob,
        min_value=min_dob,
        max_value=max_dob,
        help="Select a birth date between 01-01-1900 and yesterday."
    )

with c2:
    provider = st.selectbox("Provider", providers)
    treatment_date = st.date_input("Date of Treatment", value=date.today())
    treatment_date = st.date_input("Date of Treatment", value=today)

with c3:
    location = st.selectbox("Clinic Location", ["Downtown","Live Oak","Mission Trail","Stone Oak"])
    total_allowed = 0
    missing = []

    if dob is None:
        st.error("Select a valid date of birth.")
        st.stop()

    if dob < min_dob or dob > max_dob:
        st.error("Date of birth must be between 01-01-1900 and yesterday.")
        st.stop()

    for entry in st.session_state.meds:

        if entry["drug"] == "Select Drug":
