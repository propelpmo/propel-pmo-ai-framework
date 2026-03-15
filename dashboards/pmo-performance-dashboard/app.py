import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
st.set_page_config(page_title="Propel PMO Command Center", layout="wide")

st.title("Propel PMO Command Center")
st.caption(
    "Executive dashboard for portfolio visibility, delivery health, risk monitoring, "
    "AI project scoring, and PMO maturity."
)
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
st.subheader("Executive Scorecard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Portfolio Health Score", "82 / 100")
col2.metric("Total Projects", len(df))
col3.metric("Average Completion", f"{int(df['Completion'].mean())}%")
col4.metric("Average AI Score", round(df["AI Score"].mean(), 1))
st.subheader("Project Portfolio")

st.dataframe(
    df[["Project", "Completion", "AI Score", "Risk"]],
    use_container_width=True
)
st.subheader("Delivery Trend")

trend = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Score": [68, 72, 75, 79, 83, 87]
})

fig_trend = px.line(
    trend,
    x="Month",
    y="Score",
    markers=True,
    title="Delivery Performance Over Time"
)

st.plotly_chart(fig_trend, use_container_width=True)
st.subheader("AI Project Scoring")

fig_score = px.bar(
    df,
    x="Project",
    y="AI Score",
    title="AI Priority Score by Project"
)

st.plotly_chart(fig_score, use_container_width=True)
st.subheader("Portfolio Heatmap")

fig_heatmap = px.density_heatmap(
    df,
    x="Completion",
    y="Risk Score",
    z="AI Score",
    histfunc="avg",
    nbinsx=5,
    nbinsy=3
)

fig_heatmap.update_yaxes(
    tickmode="array",
    tickvals=[1, 2, 3],
    ticktext=["Low", "Medium", "High"]
)

st.plotly_chart(fig_heatmap, use_container_width=True)
st.subheader("Risk Radar")

radar_values = [
    df["Schedule Risk"].mean(),
    df["Budget Risk"].mean(),
    df["Delivery Risk"].mean(),
    df["Data Risk"].mean(),
    df["Schedule Risk"].mean()
]

radar_categories = ["Schedule", "Budget", "Delivery", "Data", "Schedule"]

fig_radar = go.Figure()

fig_radar.add_trace(
    go.Scatterpolar(
        r=radar_values,
        theta=radar_categories,
        fill="toself"
    )
)

fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
    showlegend=False
)

st.plotly_chart(fig_radar, use_container_width=True)
st.subheader("PMO Maturity Indicator")

maturity_df = pd.DataFrame({
    "Dimension": ["Governance", "Delivery", "Reporting", "Risk", "Automation"],
    "Score": [3.8, 4.1, 4.0, 3.6, 3.4]
})

overall_maturity = round(maturity_df["Score"].mean(), 1)

st.metric("Overall PMO Maturity", f"{overall_maturity} / 5")

fig_maturity = px.bar(
    maturity_df,
    x="Dimension",
    y="Score",
    range_y=[0, 5]
)

st.plotly_chart(fig_maturity, use_container_width=True)
