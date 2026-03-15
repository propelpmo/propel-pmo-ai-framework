import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Propel PMO Dashboard", layout="wide")

st.title("Propel PMO Executive Dashboard")

data = {
    "Project": [
        "AI Governance Setup",
        "PMO Dashboard Build",
        "Risk Framework Rollout",
        "Portfolio Automation",
        "Resource Planning"
    ],
    "Completion": [82, 68, 54, 41, 76],
    "AI Score": [4.7, 4.5, 3.8, 3.5, 4.2],
    "Risk": ["Medium", "Low", "High", "High", "Medium"],
    "Schedule Risk": [3, 2, 5, 4, 3],
    "Budget Risk": [2, 2, 4, 5, 3],
    "Delivery Risk": [3, 2, 4, 5, 3],
    "Data Risk": [2, 1, 4, 3, 2]
}

df = pd.DataFrame(data)

risk_map = {"Low": 1, "Medium": 2, "High": 3}
df["Risk Score"] = df["Risk"].map(risk_map)

st.subheader("Portfolio Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Projects", len(df))
col2.metric("Average Completion", f"{int(df['Completion'].mean())}%")
col3.metric("Average AI Score", round(df["AI Score"].mean(), 1))

st.subheader("Project Portfolio")

st.dataframe(
    df[["Project", "Completion", "AI Score", "Risk"]],
    use_container_width=True
)

st.subheader("Delivery Trend")

trend = pd.DataFrame({
    "Month": ["Jan","Feb","Mar","Apr","May","Jun"],
    "Score": [68,72,75,79,83,87]
})

fig = px.line(trend, x="Month", y="Score", markers=True)

st.plotly_chart(fig, use_container_width=True)

st.subheader("AI Project Scoring")

fig2 = px.bar(df, x="Project", y="AI Score")

st.plotly_chart(fig2, use_container_width=True)

st.subheader("Portfolio Heatmap")

fig3 = px.density_heatmap(
    df,
    x="Completion",
    y="Risk Score",
    z="AI Score",
    histfunc="avg",
    nbinsx=5,
    nbinsy=3
)

fig3.update_yaxes(
    tickmode="array",
    tickvals=[1,2,3],
    ticktext=["Low","Medium","High"]
)

st.plotly_chart(fig3, use_container_width=True)

st.subheader("Risk Radar")

radar_values = [
    df["Schedule Risk"].mean(),
    df["Budget Risk"].mean(),
    df["Delivery Risk"].mean(),
    df["Data Risk"].mean(),
    df["Schedule Risk"].mean()
]

categories = ["Schedule","Budget","Delivery","Data","Schedule"]

fig4 = go.Figure()

fig4.add_trace(
    go.Scatterpolar(
        r=radar_values,
        theta=categories,
        fill="toself"
    )
)

fig4.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0,5])),
    showlegend=False
)

st.plotly_chart(fig4, use_container_width=True)
