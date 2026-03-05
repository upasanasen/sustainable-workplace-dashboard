import streamlit as st

st.set_page_config(
    page_title="Sustainable Workplace Transformation Program Dashboard",
    page_icon="🏢",
    layout="wide",
)

st.title("🏢 Sustainable Workplace Transformation Program Dashboard")

st.markdown(
    """
### What this project is
A portfolio-grade, **EY-style workplace transformation program** prototype that demonstrates:

- **Budget & ROI simulation** (CAPEX/OPEX, payback)
- **Carbon impact screening** (energy/emissions + rooftop garden proxies)
- **Procurement & vendor scorecards**
- **Program governance** (RAID + change control)
- **Design standards compliance** across sites

### Multi-site scenario
- Barcelona (EU)
- Singapore (APAC)

Use the **sidebar pages** to explore each module.
"""
)

st.info("Next step: we will paste the full page modules and load data from your CSV files.")
