import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Propel PMO Executive Dashboard")

# Sample project data
data = {
    "Project": [
        "AI Governance Setup",
        "PMO Dashboard Build",
        "Risk Framework Rollout",
        "Portfolio Automation",
        "Resource Planning"
    ],
    "Completion": [82, 68, 54, 41, 76],
    "AI Score": [4.7, 4.5, 3.8, 3.5, 4.2]
}

df = pd.DataFrame(data)

# KPI numbers
st.subheader("Portfolio Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Projects", len(df))
col2.metric("Average Completion", f"{int(df['Completion'].mean())}%")
col3.metric("Average AI Score", round(df["AI Score"].mean(),1))

st.write("---")

# Project table
st.subheader("Project Portfolio")

st.dataframe(df)

# Delivery trend
st.subheader("Delivery Trend")

trend = pd.DataFrame({
    "Month": ["Jan","Feb","Mar","Apr","May","Jun"],
    "Score": [68,72,75,79,83,87]
})

fig = px.line(trend, x="Month", y="Score", markers=True)

st.plotly_chart(fig)

# AI Project Scoring
st.subheader("AI Project Scoring")

fig2 = px.bar(df, x="Project", y="AI Score")

st.plotly_chart(fig2)
