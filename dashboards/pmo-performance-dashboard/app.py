import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Propel PMO Command Center", layout="wide")

st.title("Propel PMO Command Center")
st.caption("Executive dashboard for portfolio visibility, delivery health, risk monitoring, AI scoring, and PMO maturity.")

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
c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio Health", "82 / 100")
c2.metric("Total Projects", len(df))
c3.metric("Avg Completion", f"{int(df['Completion'].mean())}%")
c4.metric("Avg AI Score", round(df["AI Score"].mean(), 1))

st.markdown("---")

st.subheader("Project Portfolio")
display_df = df[["Project", "Completion", "AI Score", "Risk"]].copy()

def risk_label(risk):
    if risk == "Low":
        return "🟢 Low"
    elif risk == "Medium":
        return "🟠 Medium"
    elif risk == "High":
        return "🔴 High"
    return risk

display_df["Risk"] = display_df["Risk"].apply(risk_label)

st.dataframe(display_df, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Delivery Trend")

    trend = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Score": [68, 72, 75, 79, 83, 87]
    })

    fig_trend = px.line(
        trend,
        x="Month",
        y="Score",
        markers=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("AI Project Scoring")

    fig_score = px.bar(
        df,
        x="Project",
        y="AI Score"
    )
    st.plotly_chart(fig_score, use_container_width=True)

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
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

with col4:
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
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5])
        ),
        showlegend=False
    )

    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

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
st.markdown("---")
st.subheader("Portfolio Health Gauge")

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=82,
    title={"text": "Portfolio Health"},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"thickness": 0.3},
        "steps": [
            {"range": [0, 50], "color": "lightgray"},
            {"range": [50, 75], "color": "gray"},
            {"range": [75, 100], "color": "darkgray"}
        ]
    }
))

st.plotly_chart(fig_gauge, use_container_width=True)
st.markdown("---")
st.subheader("Project Priority Ranking")

priority_df = df[["Project", "AI Score"]].sort_values(
    by="AI Score",
    ascending=False
)

st.dataframe(priority_df, use_container_width=True)
