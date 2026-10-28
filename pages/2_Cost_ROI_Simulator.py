import streamlit as st

from utils import calc_costs, io

st.title("Cost & ROI Simulator")

sites = io.load_sites()
scenarios = io.load_scenarios()
catalog = io.load_cost_catalog()

st.subheader("Select Site and Scenario")

col1, col2 = st.columns(2)
site_choice = col1.selectbox("Site", sites["site"].tolist())
scenario_choice = col2.selectbox("Scenario", scenarios["scenario"].tolist())

site = sites[sites["site"] == site_choice].iloc[0]
scenario = scenarios[scenarios["scenario"] == scenario_choice].iloc[0]

st.divider()
st.subheader("Assumptions (editable)")

colA, colB, colC = st.columns(3)
baseline_kwh_per_sqm = colA.number_input(
    "Baseline kWh per sqm (annual)",
    min_value=0.0,
    value=float(calc_costs.DEFAULT_BASELINE_KWH_PER_SQM),
)
target_kwh_per_sqm = colB.number_input(
    "Target kWh per sqm (annual)",
    min_value=0.0,
    value=float(scenario["target_kwh_per_sqm"]),
    help="Defaults to the selected scenario's own target from data/scenarios.csv.",
)
electricity_price = colC.number_input(
    "Electricity price (€ per kWh)",
    min_value=0.0,
    step=0.01,
    value=float(calc_costs.DEFAULT_ELECTRICITY_PRICE_EUR_PER_KWH),
)

result = calc_costs.roi_summary(
    site=site,
    scenario=scenario,
    catalog=catalog,
    baseline_kwh_per_sqm=baseline_kwh_per_sqm,
    target_kwh_per_sqm=target_kwh_per_sqm,
    electricity_price=electricity_price,
)

st.divider()
st.subheader("Results")

c1, c2, c3 = st.columns(3)
c1.metric("Total CAPEX (€)", f"{result['capex_eur']:,.0f}")
c2.metric("Annual Energy Saved (kWh)", f"{result['annual_kwh_saved']:,.0f}")
c3.metric("Annual Cost Saved (€)", f"{result['annual_eur_saved']:,.0f}")

payback = result["payback_years"]
if payback is None:
    st.warning(
        "Payback cannot be calculated: this scenario has CAPEX but no modelled "
        "energy saving. Lower the target kWh per sqm, or pick a scenario that "
        "includes efficiency measures."
    )
elif payback == 0:
    st.info("No CAPEX in this scenario, so there is nothing to pay back.")
else:
    st.success(f"Estimated Payback Period: **{payback:.1f} years**")

st.divider()
st.subheader("What drives the CAPEX")

breakdown = result["capex_breakdown"]
if breakdown.empty:
    st.info(
        f"**{scenario_choice}** switches on no improvement measures, so CAPEX is €0. "
        "This is the do-nothing comparator."
    )
else:
    st.caption(
        "Each measure comes from `data/cost_catalog.csv`, selected by the 0/1 flags "
        "on this scenario in `data/scenarios.csv` and multiplied by the site area "
        "its cost basis refers to."
    )
    st.dataframe(
        breakdown.rename(
            columns={
                "measure": "Measure",
                "basis": "Cost basis",
                "quantity_sqm": "Quantity (sqm)",
                "unit_cost_eur": "Unit cost (€/sqm)",
                "capex_eur": "CAPEX (€)",
                "lifetime_years": "Lifetime (years)",
            }
        ),
        width="stretch",
        hide_index=True,
    )
    st.caption(f"Blended CAPEX: €{result['capex_per_sqm']:,.0f} per sqm of office area.")

st.caption(
    "Illustrative unit costs and tariffs. Replace `data/cost_catalog.csv` with "
    "tendered rates to turn this into a live business case."
)
