import streamlit as st

from utils import io

st.set_page_config(
    page_title="Sustainable Workplace Transformation Program Dashboard",
    page_icon="🏢",
    layout="wide",
)

st.title("🏢 Sustainable Workplace Transformation Program Dashboard")

sites = io.load_sites()

st.markdown(
    """
### What this project is
A portfolio-grade **workplace transformation program** prototype that demonstrates:

- **Budget & ROI simulation** (CAPEX from a measure catalogue, energy savings, payback)
- **Carbon impact screening** (region-specific grid factors, rooftop garden proxies)
- **Procurement & vendor scorecards** (weighted, with the components exposed)
- **Program governance** (RAID log and change control)
- **Design standards compliance** across sites

Use the **sidebar pages** to explore each module.
"""
)

st.subheader(f"Portfolio: {len(sites)} sites")
regions = (
    sites.groupby("region")["site"]
    .apply(lambda s: ", ".join(sorted(s)))
    .reset_index()
    .rename(columns={"region": "Region", "site": "Sites"})
)
st.dataframe(regions, width="stretch", hide_index=True)

st.info(
    "Every figure in this dashboard is computed from the CSVs in `data/` by the "
    "calculation modules in `utils/` — nothing is hardcoded in the pages. Swap the "
    "CSVs for real project data and the whole dashboard follows."
)

st.caption(
    "Illustrative unit costs, emission factors and vendor data. See the README for "
    "what each file drives."
)
