import streamlit as st
import pandas as pd

st.title("Governance & Program Management Dashboard")

st.subheader("Program Status Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Active Projects", 12)
col2.metric("Projects On Track", 9)
col3.metric("Projects At Risk", 3)

st.divider()

st.subheader("Program Risk Register")

data = {
    "Risk": [
        "Energy retrofit delays",
        "CAPEX approval delays",
        "Supply chain constraints",
        "Regulatory compliance risk"
    ],
    "Impact": ["High", "Medium", "Medium", "High"],
    "Likelihood": ["Medium", "Medium", "Low", "Low"],
    "Owner": [
        "Operations",
        "Finance",
        "Procurement",
        "Sustainability"
    ]
}

df = pd.DataFrame(data)

st.dataframe(df)

st.divider()

st.subheader("Program Timeline")

timeline_data = pd.DataFrame({
    "Phase": [
        "Assessment",
        "Design",
        "Implementation",
        "Monitoring"
    ],
    "Status": [
        "Completed",
        "In Progress",
        "Planned",
        "Planned"
    ]
})

st.table(timeline_data)

st.caption("This governance dashboard helps track sustainability transformation programs across multiple offices.")
