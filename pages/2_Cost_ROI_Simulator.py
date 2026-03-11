import streamlit as st
import pandas as pd

st.title("Cost & ROI Simulator")

sites = pd.read_csv("data/sites.csv")
scenarios = pd.read_csv("data/scenarios.csv")

st.subheader("Select Site and Scenario")

col1, col2 = st.columns(2)
site_choice = col1.selectbox("Site", sites["site"].tolist())
scenario_choice = col2.selectbox("Scenario", scenarios["scenario"].tolist())

site = sites[sites["site"] == site_choice].iloc[0]
scenario = scenarios[scenarios["scenario"] == scenario_choice].iloc[0]

st.divider()
st.subheader("Assumptions (editable)")

colA, colB, colC = st.columns(3)
capex_per_sqm = colA.number_input("CAPEX (€) per sqm", min_value=50, max_value=2000, value=300)

baseline_kwh_per_sqm = colB.number_input(
    "Baseline kWh per sqm (annual)",
    value=st.session_state.get("baseline_kwh_per_sqm", 120),
    key="baseline_kwh_per_sqm"
)

target_kwh_per_sqm = colC.number_input(
    "Target kWh per sqm (annual)",
    value=st.session_state.get("target_kwh_per_sqm", 80),
    key="target_kwh_per_sqm"
)
st.divider()
st.subheader("Results")

office_area = float(site["office_area_sqm"])
electricity_price = 0.25

capex_total = office_area * capex_per_sqm
baseline_kwh = office_area * baseline_kwh_per_sqm
target_kwh = office_area * target_kwh_per_sqm

annual_kwh_saved = max(0, baseline_kwh - target_kwh)
annual_cost_saved = annual_kwh_saved * electricity_price

if annual_cost_saved > 0:
    payback_years = capex_total / annual_cost_saved
else:
    payback_years = None

c1, c2, c3 = st.columns(3)
c1.metric("Total CAPEX (€)", f"{capex_total:,.0f}")
c2.metric("Annual Energy Saved (kWh)", f"{annual_kwh_saved:,.0f}")
c3.metric("Annual Cost Saved (€)", f"{annual_cost_saved:,.0f}")

if payback_years is None:
    st.warning("Payback cannot be calculated because annual savings are 0.")
else:
    st.success(f"Estimated Payback Period: **{payback_years:.1f} years**")

st.caption("This is a portfolio simulator. Values are illustrative and can be replaced with real project data later.")
