import streamlit as st

from utils import io, scoring

st.title("Standards & Compliance Dashboard")
st.write(
    "Track program compliance across sites: sustainability standards, HSE, "
    "governance, and reporting readiness."
)

sites = io.load_sites()
site_choice = st.selectbox("Select Site", ["All Sites"] + sites["site"].tolist())
selected_site = None if site_choice == "All Sites" else site_choice

register = io.compliance_register(selected_site)

st.divider()
st.subheader("Compliance KPIs")

rate = scoring.compliance_rate(register["status"])
rag = scoring.rag_status(rate)
rag_icon = {"Green": "🟢", "Amber": "🟡", "Red": "🔴"}[rag]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Controls", f"{len(register)}")
c2.metric("Completed", f"{int((register['status'] == 'Completed').sum())}")
c3.metric("Completion Rate", f"{rate:.0f}%")
c4.metric("RAG Status", f"{rag_icon} {rag}")

high_risk_open = register[
    (register["risk_if_failed"] == "High") & (register["status"] != "Completed")
]
if not high_risk_open.empty:
    st.warning(
        f"{len(high_risk_open)} high-risk control(s) not yet complete: "
        + ", ".join(sorted(high_risk_open["standard"].unique()))
    )

st.divider()
st.subheader("Compliance Register")
st.caption(
    "Controls from `data/standards_checklist.csv` joined to per-site status in "
    "`data/site_standards_status.csv`."
)
display = register if selected_site is None else register.drop(columns=["site"])
st.dataframe(
    display.rename(
        columns={
            "site": "Site", "standard": "Standard", "category": "Category",
            "owner": "Owner", "status": "Status", "evidence": "Evidence",
            "risk_if_failed": "Risk if failed", "last_reviewed": "Last reviewed",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.divider()
st.subheader("Completion by Site")
by_site = (
    io.compliance_register()
    .groupby("site")["status"]
    .apply(scoring.compliance_rate)
    .reset_index(name="completion_percent")
)
by_site["rag"] = by_site["completion_percent"].apply(scoring.rag_status)
st.dataframe(
    by_site.rename(
        columns={"site": "Site", "completion_percent": "Completion %", "rag": "RAG"}
    ).style.format({"Completion %": "{:.0f}%"}),
    width="stretch",
    hide_index=True,
)

st.caption(
    "Demonstrates governance maturity: controls, owners, evidence, risk and "
    "per-site follow-up. RAG bands are Green ≥80%, Amber ≥50%, Red below."
)
