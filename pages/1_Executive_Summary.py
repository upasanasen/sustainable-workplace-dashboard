import streamlit as st

try:
    import pydeck as pdk
except ImportError:  # optional: the map is decoration, the metrics are the page
    pdk = None

from utils import calc_emissions, io

st.title("Executive Program Overview")

sites = io.load_sites()

st.subheader("Total Program Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Sites", f"{len(sites)}")
col2.metric("Total Office Area (sqm)", f"{int(sites['office_area_sqm'].sum()):,}")
col3.metric("Total Employees Impacted", f"{int(sites['employees'].sum()):,}")
col4.metric("Rooftop Garden Potential (sqm)", f"{int(sites['roof_area_sqm'].sum()):,}")

st.subheader("Site Portfolio")
st.dataframe(sites, width="stretch", hide_index=True)

st.subheader("Portfolio by Region")
by_region = (
    sites.groupby("region")
    .agg(
        sites=("site", "count"),
        employees=("employees", "sum"),
        office_area_sqm=("office_area_sqm", "sum"),
        roof_area_sqm=("roof_area_sqm", "sum"),
    )
    .reset_index()
)
by_region["grid_factor_t_per_kwh"] = by_region["region"].apply(calc_emissions.grid_intensity)
st.dataframe(
    by_region.rename(
        columns={
            "region": "Region", "sites": "Sites", "employees": "Employees",
            "office_area_sqm": "Office area (sqm)", "roof_area_sqm": "Roof area (sqm)",
            "grid_factor_t_per_kwh": "Grid factor (t CO₂e/kWh)",
        }
    ).style.format({"Grid factor (t CO₂e/kWh)": "{:.6f}"}),
    width="stretch",
    hide_index=True,
)
st.caption(
    "Grid factors drive the carbon page: the same efficiency measure saves more "
    "CO₂e in a higher-intensity grid."
)

st.subheader("Strategic Objective")
st.markdown(
    """
This workplace transformation program aims to:

- Reduce operational carbon emissions
- Improve energy efficiency of office operations
- Introduce rooftop biodiversity infrastructure
- Ensure design standards across global offices
- Deliver cost-effective workplace modernization
"""
)

st.divider()
st.subheader("Site Map (Portfolio View)")

if pdk is None:
    st.info(
        "Install `pydeck` (it is in requirements.txt) to see the portfolio map. "
        "Everything else on this page works without it."
    )
    st.stop()

map_df = sites.copy()
map_df["lat"] = map_df["lat"].astype(float)
map_df["lon"] = map_df["lon"].astype(float)
map_df["radius"] = map_df["employees"].fillna(0).astype(float) / 8

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position="[lon, lat]",
    get_radius="radius",
    radius_scale=30,
    radius_min_pixels=6,
    radius_max_pixels=60,
    get_fill_color=[0, 180, 120, 160],
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
            "text": "{site}\nEmployees: {employees}\n"
                    "Office area: {office_area_sqm} sqm\nRoof area: {roof_area_sqm} sqm"
        },
    )
)
