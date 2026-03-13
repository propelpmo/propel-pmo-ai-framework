import streamlit as st
import pandas as pd

st.set_page_config(page_title="Propel PMO Dashboard", layout="wide")

st.title("Propel PMO – PMO Performance Dashboard")
st.markdown("Sample executive dashboard for portfolio health, delivery status, and risk visibility.")

data = {
    "Project Name": ["AI Governance Setup", "PMO Dashboard Build", "Risk Framework Rollout", "Portfolio Reporting Automation"],
    "Status": ["On Track", "On Track", "At Risk", "Delayed"],
    "Completion": [80, 65, 50, 40],
    "Risk Level": ["Medium", "Low", "High", "High"]
}

df = pd.DataFrame(data)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Projects", len(df))
col2.metric("On Track", len(df[df["Status"] == "On Track"]))
col3.metric("At Risk", len(df[df["Status"] == "At Risk"]))
col4.metric("Avg Completion %", f'{int(df["Completion"].mean())}%')

st.subheader("Project Portfolio Overview")
st.dataframe(df, use_container_width=True)

st.subheader("Projects by Status")
st.bar_chart(df["Status"].value_counts())

st.subheader("Completion by Project")
st.bar_chart(df.set_index("Project Name")["Completion"])

st.subheader("Risk Summary")
st.bar_chart(df["Risk Level"].value_counts())
