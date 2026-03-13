import streamlit as st
import pandas as pd

st.set_page_config(page_title="Propel PMO | Executive Dashboard", layout="wide")

st.title("Propel PMO – Executive PMO Dashboard")
st.caption("Sample dashboard for portfolio visibility, delivery health, and risk monitoring.")

data = [
    ["AI Governance Setup", "On Track", 82, "Medium", "Strategy", "Kinjal"],
    ["PMO Dashboard Build", "On Track", 68, "Low", "Delivery", "Kinjal"],
    ["Risk Framework Rollout", "At Risk", 54, "High", "Governance", "Team A"],
    ["Portfolio Reporting Automation", "Delayed", 41, "High", "Operations", "Team B"],
    ["Resource Planning Model", "On Track", 76, "Medium", "Operations", "Team C"],
    ["Stakeholder Communication Plan", "At Risk", 59, "Medium", "Delivery", "Team D"],
]

df = pd.DataFrame(
    data,
    columns=["Project", "Status", "Completion", "Risk", "Workstream", "Owner"]
)

total_projects = len(df)
on_track = (df["Status"] == "On Track").sum()
at_risk = (df["Status"] == "At Risk").sum()
delayed = (df["Status"] == "Delayed").sum()
avg_completion = int(df["Completion"].mean())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Projects", total_projects)
c2.metric("On Track", on_track)
c3.metric("At Risk", at_risk)
c4.metric("Avg Completion", f"{avg_completion}%")

st.markdown("---")

left, right = st.columns([1.5, 1])

with left:
    st.subheader("Portfolio Overview")
    st.dataframe(df, use_container_width=True)

    st.subheader("Completion by Project")
    st.bar_chart(df.set_index("Project")["Completion"])

with right:
    st.subheader("Projects by Status")
    st.bar_chart(df["Status"].value_counts())

    st.subheader("Risk Distribution")
    st.bar_chart(df["Risk"].value_counts())

    st.subheader("Projects by Workstream")
    st.bar_chart(df["Workstream"].value_counts())

st.markdown("---")
st.subheader("Executive Summary")

high_risk = df[df["Risk"] == "High"]["Project"].tolist()
high_risk_text = ", ".join(high_risk) if high_risk else "None"

st.write(f"""
- Portfolio currently includes **{total_projects} active initiatives**.
- **{on_track} projects** are on track, **{at_risk}** are at risk, and **{delayed}** are delayed.
- Average completion across the portfolio is **{avg_completion}%**.
- Highest-risk initiatives: **{high_risk_text}**.
""")
