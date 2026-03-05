import streamlit as st
import pandas as pd

st.title("Executive Program Overview")

sites = pd.read_csv("data/sites.csv")

st.subheader("Site Portfolio")

st.dataframe(sites)

st.subheader("Total Program Metrics")

total_area = sites["office_area_sqm"].sum()
total_employees = sites["employees"].sum()
total_roof = sites["roof_area_sqm"].sum()

col1, col2, col3 = st.columns(3)

col1.metric("Total Office Area (sqm)", total_area)
col2.metric("Total Employees Impacted", total_employees)
col3.metric("Rooftop Garden Potential (sqm)", total_roof)

st.subheader("Strategic Objective")

st.markdown("""
This workplace transformation program aims to:

• Reduce operational carbon emissions  
• Improve energy efficiency of office operations  
• Introduce rooftop biodiversity infrastructure  
• Ensure design standards across global offices  
• Deliver cost-effective workplace modernization
""")
st.divider()
st.subheader("Site Map (Portfolio View)")

import pydeck as pdk

if "lat" in sites.columns and "lon" in sites.columns:
    map_df = sites.copy()

    # Make sure lat/lon are numbers
    map_df["lat"] = map_df["lat"].astype(float)
    map_df["lon"] = map_df["lon"].astype(float)

    # Bubble size (still tied to employees)
    # We'll convert to pixels using radius_scale + radius_min_pixels
    map_df["radius"] = map_df["employees"].fillna(0).astype(float) / 8

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[lon, lat]",
        get_radius="radius",
        radius_scale=30,          # scales your "radius" values
        radius_min_pixels=6,      # key: always visible
        radius_max_pixels=60,
        get_fill_color=[0, 180, 120, 160],   # green-ish with alpha
        get_line_color=[255, 255, 255],
        line_width_min_pixels=1,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=float(map_df["lat"].mean()),
        longitude=float(map_df["lon"].mean()),
        zoom=1.2,
        pitch=0,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
        tooltip={
    "text": "{site}\nEmployees: {employees}\nOffice area: {office_area_sqm} sqm\nRoof area: {roof_area_sqm} sqm"   
	 },
        )
    )
else:
    st.warning("Add 'lat' and 'lon' columns to data/sites.csv to show the site map.")
