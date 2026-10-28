import streamlit as st

from utils import io, scoring

st.title("Procurement & Vendor Dashboard")

sites = io.load_sites()
vendors = io.load_vendors()

st.subheader("Select Context")
colA, colB = st.columns(2)
colA.selectbox("Site (optional)", ["All Sites"] + sites["site"].tolist())
category_filter = colB.selectbox(
    "Vendor Category", ["All"] + sorted(vendors["category"].unique().tolist())
)

st.divider()

filtered = vendors.copy()
if category_filter != "All":
    filtered = filtered[filtered["category"] == category_filter]

st.subheader("Vendor Portfolio KPIs")
c1, c2, c3, c4 = st.columns(4)
if filtered.empty:
    c1.metric("Vendors in View", "0")
    c2.metric("Avg Rating", "—")
    c3.metric("Avg Lead Time (weeks)", "—")
    c4.metric("High Risk Vendors", "0")
    st.info("No vendors in this category.")
else:
    c1.metric("Vendors in View", f"{len(filtered)}")
    c2.metric("Avg Rating", f"{filtered['rating'].mean():.2f}")
    c3.metric("Avg Lead Time (weeks)", f"{filtered['lead_time_weeks'].mean():.1f}")
    c4.metric("High Risk Vendors", f"{int((filtered['risk'] == 'High').sum())}")

st.divider()
st.subheader("Vendor Shortlist")
shortlist = filtered.copy()
shortlist["risk_rank"] = shortlist["risk"].map(scoring.RISK_RANK)
st.dataframe(
    shortlist.sort_values(["risk_rank", "rating"], ascending=[True, False]).drop(
        columns=["risk_rank"]
    ),
    width="stretch",
    hide_index=True,
)

st.divider()
st.subheader("Vendor Scorecard")

pool = filtered if not filtered.empty else vendors
score_col1, score_col2 = st.columns(2)
pick_vendor = score_col1.selectbox("Select vendor to score", pool["vendor"].tolist())
weight_cost = score_col2.slider("Cost Weight", 0, 100, 35)
weight_quality = st.slider("Quality Weight", 0, 100, 35)
weight_sustain = st.slider("Sustainability Weight", 0, 100, 30)

vrow = vendors[vendors["vendor"] == pick_vendor].iloc[0]
result = scoring.vendor_score(vrow, weight_cost, weight_quality, weight_sustain)

if result is None:
    st.warning("Set at least one weight above 0.")
else:
    st.success(f"Vendor Score (0–1): **{result['total']:.2f}**")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cost / lead time", f"{result['cost_score']:.2f}",
              f"weight {result['weights']['cost']:.0%}")
    c2.metric("Quality / rating", f"{result['quality_score']:.2f}",
              f"weight {result['weights']['quality']:.0%}")
    c3.metric("Sustainability", f"{result['sustainability_score']:.2f}",
              f"weight {result['weights']['sustainability']:.0%}")
    st.caption(
        f"Cost score falls linearly to 0 at a "
        f"{scoring.LEAD_TIME_CEILING_WEEKS:.0f}-week lead time. Sustainability credits "
        f"holders of {scoring.SUSTAINABILITY_CERT}. Weights are normalised to sum to 1, "
        "so only their ratio matters."
    )

st.caption(
    "Demo criteria for portfolio presentation. Replace the weights and the "
    "scoring in `utils/scoring.py` with real procurement criteria before use."
)
