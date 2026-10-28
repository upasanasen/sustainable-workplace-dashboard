import pandas as pd
import streamlit as st

from utils import io, scoring

st.title("Governance & Program Management Dashboard")

raid = io.load_raid_log()
changes = io.load_change_log()

severity = raid.apply(
    lambda r: scoring.risk_severity(r["impact"], r["likelihood"]), axis=1, result_type="expand"
)
raid = pd.concat([raid, severity[["score", "band"]]], axis=1)

st.subheader("Program Status Overview")
open_items = raid[raid["status"] != "Closed"]
c1, c2, c3, c4 = st.columns(4)
c1.metric("RAID Items", f"{len(raid)}")
c2.metric("Open", f"{len(open_items)}")
c3.metric("Critical / High", f"{int(open_items['band'].isin(['Critical', 'High']).sum())}")
c4.metric("Change Requests", f"{len(changes)}")

st.divider()
st.subheader("RAID Log")
st.caption(
    "Risks, Assumptions, Issues and Dependencies from `data/raid_log.csv`. "
    "Severity is impact × likelihood on a 1–3 scale."
)

type_filter = st.multiselect(
    "Filter by type",
    options=sorted(raid["type"].unique().tolist()),
    default=sorted(raid["type"].unique().tolist()),
)
view = raid[raid["type"].isin(type_filter)] if type_filter else raid

st.dataframe(
    view.sort_values(["score", "type"], ascending=[False, True])[
        ["id", "type", "title", "impact", "likelihood", "band", "owner",
         "status", "mitigation", "due_date"]
    ].rename(
        columns={
            "id": "ID", "type": "Type", "title": "Item", "impact": "Impact",
            "likelihood": "Likelihood", "band": "Severity", "owner": "Owner",
            "status": "Status", "mitigation": "Mitigation / action", "due_date": "Due",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.divider()
st.subheader("Change Control")

approved = changes[changes["status"] == "Approved"]
net_cost = float(approved["cost_impact_eur"].sum())
net_weeks = int(approved["schedule_impact_weeks"].sum())

c1, c2, c3 = st.columns(3)
c1.metric("Approved Changes", f"{len(approved)}")
c2.metric("Net CAPEX Impact (€)", f"{net_cost:,.0f}")
c3.metric("Net Schedule Impact (weeks)", f"{net_weeks:+d}")

st.dataframe(
    changes.sort_values("date", ascending=False).rename(
        columns={
            "id": "ID", "date": "Date", "title": "Change", "requested_by": "Requested by",
            "cost_impact_eur": "Cost impact (€)",
            "schedule_impact_weeks": "Schedule impact (weeks)",
            "status": "Status", "decision": "Decision", "notes": "Notes",
        }
    ),
    width="stretch",
    hide_index=True,
)

st.caption(
    "A negative cost impact is a rephasing or descope that releases budget — "
    "CR-03 defers New York HVAC works, which is why the net figure can fall."
)
