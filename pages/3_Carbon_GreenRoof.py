import matplotlib.pyplot as plt
import streamlit as st

from utils import calc_costs, calc_emissions, io

st.title("Carbon Impact & Rooftop Garden Potential")

sites = io.load_sites()

site_choice = st.selectbox("Select Site", sites["site"].tolist())
site = sites[sites["site"] == site_choice].iloc[0]

office_area = float(site["office_area_sqm"])
roof_area = float(site["roof_area_sqm"])
region = site["region"]

col1, col2 = st.columns(2)
baseline_kwh_per_sqm = col1.number_input(
    "Baseline Energy Use (kWh per sqm)", min_value=0.0, value=120.0
)
target_kwh_per_sqm = col2.number_input(
    "Target Energy Use (kWh per sqm)", min_value=0.0, value=80.0
)

baseline_energy = calc_costs.annual_kwh(office_area, baseline_kwh_per_sqm)
target_energy = calc_costs.annual_kwh(office_area, target_kwh_per_sqm)
energy_saved = calc_costs.energy_saved_kwh(baseline_energy, target_energy)

intensity = calc_emissions.grid_intensity(region)
carbon_saved = calc_emissions.emissions_saved_t(baseline_energy, target_energy, region)

st.subheader("Energy Impact")
c1, c2, c3 = st.columns(3)
c1.metric("Baseline Energy (kWh)", f"{baseline_energy:,.0f}")
c2.metric("Target Energy (kWh)", f"{target_energy:,.0f}")
c3.metric("Annual Energy Saved (kWh)", f"{energy_saved:,.0f}")

st.subheader("Carbon Reduction")
c1, c2 = st.columns(2)
c1.metric("Estimated CO₂e Reduction (t/year)", f"{carbon_saved:,.2f}")
c2.metric(f"Grid Factor — {region} (t CO₂e/kWh)", f"{intensity:.6f}")
st.caption(
    "Emission factors are location-based regional averages, so the same kWh saved "
    "is worth more carbon in a higher-intensity grid. Planning estimates, not a "
    "Scope 2 inventory."
)

st.subheader("Rooftop Garden Potential")
green_roof_percent = st.slider("Percent of roof converted to green roof", 0, 100, 50)
roof = calc_emissions.green_roof_summary(roof_area, green_roof_percent, region)

c1, c2, c3 = st.columns(3)
c1.metric("Green Roof Area (sqm)", f"{roof['green_roof_area_sqm']:,.0f}")
c2.metric("Sequestration (t CO₂e/year)", f"{roof['sequestration_t_per_year']:,.2f}")
c3.metric("Cooling Saving (kWh/year)", f"{roof['cooling_saving_kwh_per_year']:,.0f}")
st.caption(
    f"Cooling load avoided is credited a further "
    f"{roof['cooling_saving_t_per_year']:,.2f} t CO₂e/year at this region's grid factor."
)

st.subheader("Energy Comparison Chart")
fig, ax = plt.subplots()
ax.bar(["Baseline", "Target"], [baseline_energy, target_energy])
ax.set_ylabel("Energy Use (kWh)")
ax.set_title(f"Annual Energy Consumption — {site_choice}")
st.pyplot(fig)
