import streamlit as st
import pandas as pd

st.title("Procurement & Vendor Dashboard")

# -----------------------------
# Load sites (optional context)
# -----------------------------
try:
    sites = pd.read_csv("data/sites.csv")
    site_names = sites["site"].tolist() if "site" in sites.columns else []
except Exception:
    sites = None
    site_names = []

st.subheader("Select Context")
colA, colB = st.columns(2)
selected_site = colA.selectbox("Site (optional)", ["All Sites"] + site_names)
category_filter = colB.selectbox(
    "Vendor Category",
    ["All", "Energy Retrofit", "HVAC", "Lighting", "Solar/Green Roof", "Smart Systems", "Construction", "Consulting"]
)

st.divider()

# -----------------------------
# Vendor dataset (demo)
# -----------------------------
vendors = pd.DataFrame([
    {"vendor": "EcoBuild Partners", "category": "Construction", "region": "EU", "rating": 4.6, "lead_time_weeks": 10, "risk": "Medium", "certs": "ISO 9001, ISO 14001", "notes": "Strong fit-out delivery, good reporting"},
    {"vendor": "Nordic HVAC Co", "category": "HVAC", "region": "EU", "rating": 4.4, "lead_time_weeks": 12, "risk": "Medium", "certs": "ISO 9001", "notes": "Reliable delivery, higher CAPEX"},
    {"vendor": "BrightLite Systems", "category": "Lighting", "region": "Global", "rating": 4.7, "lead_time_weeks": 6, "risk": "Low", "certs": "ISO 9001, RoHS", "notes": "Fast rollout, good savings"},
    {"vendor": "GreenRoof Works", "category": "Solar/Green Roof", "region": "EU", "rating": 4.5, "lead_time_weeks": 8, "risk": "Low", "certs": "ISO 14001", "notes": "Excellent roof biodiversity packages"},
    {"vendor": "SmartOps Tech", "category": "Smart Systems", "region": "Global", "rating": 4.3, "lead_time_weeks": 7, "risk": "Medium", "certs": "SOC 2", "notes": "Good BMS + analytics, needs IT alignment"},
    {"vendor": "Retrofit Energy Group", "category": "Energy Retrofit", "region": "EU", "rating": 4.2, "lead_time_weeks": 14, "risk": "High", "certs": "ISO 14001", "notes": "Capacity constraints in peak season"},
    {"vendor": "Sustainability Advisory Lab", "category": "Consulting", "region": "Global", "rating": 4.8, "lead_time_weeks": 4, "risk": "Low", "certs": "ISO 14001", "notes": "Great governance + reporting templates"},
])

# Filter
filtered = vendors.copy()
if category_filter != "All":
    filtered = filtered[filtered["category"] == category_filter]

# -----------------------------
# KPIs
# -----------------------------
st.subheader("Vendor Portfolio KPIs")
c1, c2, c3, c4 = st.columns(4)

c1.metric("Vendors in View", f"{len(filtered)}")
c2.metric("Avg Rating", f"{filtered['rating'].mean():.2f}")
c3.metric("Avg Lead Time (weeks)", f"{filtered['lead_time_weeks'].mean():.1f}")
high_risk = int((filtered["risk"] == "High").sum())
c4.metric("High Risk Vendors", f"{high_risk}")

st.divider()

# -----------------------------
# Vendor table
# -----------------------------
st.subheader("Vendor Shortlist")
st.dataframe(
    filtered.sort_values(["risk", "rating"], ascending=[True, False]),
    use_container_width=True
)

st.divider()

# -----------------------------
# RFQ / Scorecard (simple)
# -----------------------------
st.subheader("Quick Vendor Scorecard (Portfolio Demo)")

score_col1, score_col2 = st.columns(2)
pick_vendor = score_col1.selectbox("Select vendor to score", filtered["vendor"].tolist() if len(filtered) else vendors["vendor"].tolist())

weight_cost = score_col2.slider("Cost Weight", 0, 100, 35)
weight_quality = st.slider("Quality Weight", 0, 100, 35)
weight_sustain = st.slider("Sustainability Weight", 0, 100, 30)

# Normalize weights
total_w = weight_cost + weight_quality + weight_sustain
if total_w == 0:
    st.warning("Set at least one weight above 0.")
else:
    w_cost = weight_cost / total_w
    w_quality = weight_quality / total_w
    w_sustain = weight_sustain / total_w

    vrow = vendors[vendors["vendor"] == pick_vendor].iloc[0]

    # Demo scoring logic
    cost_score = 1.0 - min(vrow["lead_time_weeks"] / 20.0, 1.0)          # faster = better
    quality_score = min(vrow["rating"] / 5.0, 1.0)
    sustain_score = 1.0 if "ISO 14001" in str(vrow["certs"]) else 0.7

    total_score = (w_cost * cost_score) + (w_quality * quality_score) + (w_sustain * sustain_score)

    st.success(f"Vendor Score (0–1): **{total_score:.2f}**")
    st.caption("This is a demo scorecard for portfolio presentation; replace scoring with real procurement criteria later.")

st.divider()
st.caption("Procurement view supports vendor shortlist, risk screening, and basic scoring to align with program governance.")
