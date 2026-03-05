import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Carbon Impact & Rooftop Garden Potential")

sites = pd.read_csv("data/sites.csv")

site_choice = st.selectbox("Select Site", sites["site"].tolist())

site = sites[sites["site"] == site_choice].iloc[0]

office_area = float(site["office_area_sqm"])
roof_area = float(site["roof_area_sqm"])

baseline_kwh_per_sqm = st.number_input("Baseline Energy Use (kWh per sqm)", value=120)
target_kwh_per_sqm = st.number_input("Target Energy Use (kWh per sqm)", value=80)

baseline_energy = office_area * baseline_kwh_per_sqm
target_energy = office_area * target_kwh_per_sqm

energy_saved = baseline_energy - target_energy

co2_factor = 0.000233
carbon_saved = energy_saved * co2_factor

st.subheader("Energy Impact")

c1, c2 = st.columns(2)

c1.metric("Baseline Energy (kWh)", f"{baseline_energy:,.0f}")
c2.metric("Target Energy (kWh)", f"{target_energy:,.0f}")

st.metric("Annual Energy Saved (kWh)", f"{energy_saved:,.0f}")

st.subheader("Carbon Reduction")

st.metric("Estimated CO₂ Reduction (tons/year)", f"{carbon_saved:,.2f}")

st.subheader("Rooftop Garden Potential")

green_roof_percent = st.slider("Percent of roof converted to green roof", 0, 100, 50)

green_roof_area = roof_area * (green_roof_percent / 100)

st.metric("Green Roof Area (sqm)", f"{green_roof_area:,.0f}")

st.subheader("Energy Comparison Chart")

fig, ax = plt.subplots()

labels = ["Baseline", "Target"]
values = [baseline_energy, target_energy]

ax.bar(labels, values)
ax.set_ylabel("Energy Use (kWh)")
ax.set_title("Energy Consumption Comparison")

st.pyplot(fig)
