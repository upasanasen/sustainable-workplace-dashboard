import streamlit as st
import pandas as pd

st.title("Standards & Compliance Dashboard")

st.write("Track program compliance across sites: sustainability standards, HSE, governance, and reporting readiness.")

# Load sites for context (optional)
try:
    sites = pd.read_csv("data/sites.csv")
    site_names = sites["site"].tolist() if "site" in sites.columns else []
except Exception:
    sites = None
    site_names = []

selected_site = st.selectbox("Select Site", ["All Sites"] + site_names)

st.divider()

# Demo compliance checklist
compliance = pd.DataFrame([
    {"standard": "ISO 14001 (Environmental Management)", "owner": "Sustainability", "status": "In Progress", "evidence": "Policy draft + training plan", "risk_if_failed": "Medium"},
    {"standard": "ISO 50001 (Energy Management)", "owner": "Operations", "status": "Planned", "evidence": "Baseline energy audit required", "risk_if_failed": "High"},
    {"standard": "HSE / Workplace Safety", "owner": "Facilities", "status": "Completed", "evidence": "HSE audit signed", "risk_if_failed": "High"},
    {"standard": "Supplier Code of Conduct", "owner": "Procurement", "status": "In Progress", "evidence": "Vendor onboarding checklist", "risk_if_failed": "Medium"},
    {"standard": "Data Privacy (for smart systems)", "owner": "IT/Security", "status": "Planned", "evidence": "DPIA template pending", "risk_if_failed": "High"},
    {"standard": "CSRD Readiness (reporting alignment)", "owner": "Finance/Sustainability", "status": "In Progress", "evidence": "Metrics mapping started", "risk_if_failed": "Medium"},
])

# KPIs
st.subheader("Compliance KPIs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Controls", f"{len(compliance)}")
c2.metric("Completed", f"{(compliance['status']=='Completed').sum()}")
c3.metric("In Progress", f"{(compliance['status']=='In Progress').sum()}")
c4.metric("High Risk Items", f"{(compliance['risk_if_failed']=='High').sum()}")

st.divider()

st.subheader("Compliance Register")
st.dataframe(compliance, use_container_width=True)

st.divider()

# Simple tracker: action plan table
st.subheader("Action Plan (Portfolio Demo)")
actions = pd.DataFrame([
    {"action": "Complete energy audit per site", "due": "2026-04-15", "owner": "Operations", "status": "Planned"},
    {"action": "Finalize Supplier Code onboarding checklist", "due": "2026-03-25", "owner": "Procurement", "status": "In Progress"},
    {"action": "Perform DPIA for smart monitoring systems", "due": "2026-04-05", "owner": "IT/Security", "status": "Planned"},
    {"action": "CSRD metrics mapping + evidence folder structure", "due": "2026-03-30", "owner": "Finance/Sustainability", "status": "In Progress"},
])
st.dataframe(actions, use_container_width=True)

st.divider()
st.caption("Standards dashboard helps demonstrate governance maturity: controls, evidence, owners, risks, and follow-up actions.")
