import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI

st.set_page_config(page_title="Propel PMO Command Center", layout="wide")

# -----------------------------
# OPENAI CLIENT
# -----------------------------
api_key = st.secrets.get("OPENAI_API_KEY", "")

client = None
if api_key:
    client = OpenAI(api_key=api_key)

# -----------------------------
# PAGE HEADER
# -----------------------------
st.title("Propel PMO Command Center")
st.caption(
    "Executive dashboard for portfolio visibility, delivery health, risk monitoring, "
    "AI project scoring, PMO maturity, and AI-powered visitor support."
)

# -----------------------------
# SAMPLE DATA
# -----------------------------
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

# -----------------------------
# HELPERS
# -----------------------------
def build_portfolio_summary(dataframe: pd.DataFrame) -> str:
    avg_completion = round(dataframe["Completion"].mean(), 1)
    avg_ai_score = round(dataframe["AI Score"].mean(), 1)
    total_projects = len(dataframe)
    high_risk_count = len(dataframe[dataframe["Risk"] == "High"])
    medium_risk_count = len(dataframe[dataframe["Risk"] == "Medium"])

    return f"""
    Propel PMO snapshot:
    - Total projects: {total_projects}
    - Average completion: {avg_completion}%
    - Average AI score: {avg_ai_score} / 5
    - High-risk projects: {high_risk_count}
    - Medium-risk projects: {medium_risk_count}

    Current projects include AI Governance Setup, PMO Dashboard Build,
    Risk Framework Rollout, Portfolio Automation, and Resource Planning.
    """

def ask_propell_pmo_bot(user_question: str, portfolio_context: str, chat_history: list) -> str:
    if not client:
        return "AI chatbot is not active yet. Please add OPENAI_API_KEY in Streamlit secrets."

    history_text = ""
    for msg in chat_history[-6:]:
        role = msg["role"].upper()
        history_text += f"{role}: {msg['content']}\n"

    instructions = """
    You are the Propel PMO AI Assistant.

    Your purpose:
    - Answer visitor questions about Propel PMO services
    - Explain AI-driven PMO capabilities in simple, executive-friendly language
    - Help visitors understand portfolio governance, delivery oversight, PMO modernization,
      AI transformation support, staffing support, and advisory services
    - Stay concise, professional, and business-oriented
    - Do not make up pricing, case studies, or clients
    - If asked something unrelated to Propel PMO, politely redirect to Propel PMO capabilities

    Tone:
    - Executive
    - Clear
    - Professional
    - Helpful
    """

    prompt = f"""
    Portfolio context:
    {portfolio_context}

    Recent conversation:
    {history_text}

    Visitor question:
    {user_question}
    """

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=prompt
    )

    return response.output_text.strip()

portfolio_context = build_portfolio_summary(df)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["Dashboard", "AI PMO Chatbot"])

with tab1:
    # -----------------------------
    # TOP SCORECARDS
    # -----------------------------
    st.subheader("Executive Scorecard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Portfolio Health Score", "82 / 100")
    col2.metric("Total Projects", len(df))
    col3.metric("Average Completion", f"{int(df['Completion'].mean())}%")
    col4.metric("Average AI Score", round(df["AI Score"].mean(), 1))

    # -----------------------------
    # PROJECT PORTFOLIO
    # -----------------------------
    st.subheader("Project Portfolio")
    st.dataframe(
        df[["Project", "Completion", "AI Score", "Risk"]],
        use_container_width=True
    )

    # -----------------------------
    # DELIVERY TREND
    # -----------------------------
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

    # -----------------------------
    # AI PROJECT SCORING
    # -----------------------------
    st.subheader("AI Project Scoring")

    fig_score = px.bar(
        df,
        x="Project",
        y="AI Score",
        title="AI Priority Score by Project"
    )

    st.plotly_chart(fig_score, use_container_width=True)

    # -----------------------------
    # PORTFOLIO HEATMAP
    # -----------------------------
    st.subheader("Portfolio Heatmap")

    fig_heatmap = px.density_heatmap(
        df,
        x="Completion",
        y="Risk Score",
        z="AI Score",
        histfunc="avg",
        nbinsx=5,
        nbinsy=3,
        title="Portfolio Heatmap by Completion, Risk, and AI Score"
    )

    fig_heatmap.update_yaxes(
        tickmode="array",
        tickvals=[1, 2, 3],
        ticktext=["Low", "Medium", "High"]
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # -----------------------------
    # RISK RADAR
    # -----------------------------
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
            fill="toself",
            name="Portfolio Risk"
        )
    )

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=False
    )

    st.plotly_chart(fig_radar, use_container_width=True)

    # -----------------------------
    # PMO MATURITY INDICATOR
    # -----------------------------
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
        title="PMO Maturity by Dimension",
        range_y=[0, 5]
    )

    st.plotly_chart(fig_maturity, use_container_width=True)

with tab2:
    st.subheader("AI PMO Chatbot")
    st.caption("Ask about Propel PMO services, AI PMO strategy, governance, delivery, and modernization.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello — I’m the Propel PMO AI Assistant. "
                    "I can explain AI PMO services, portfolio governance, delivery oversight, "
                    "and PMO modernization."
                )
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    suggested_questions = [
        "What does an AI PMO do?",
        "How can Propel PMO improve portfolio governance?",
        "How does AI help executive reporting?",
        "What services does Propel PMO offer?"
    ]

    st.write("Try one of these questions:")
    cols = st.columns(len(suggested_questions))
    for i, question in enumerate(suggested_questions):
        if cols[i].button(question):
            st.session_state.pending_question = question

    user_input = st.chat_input("Ask a question about Propel PMO...")

    if "pending_question" in st.session_state and not user_input:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = ask_propell_pmo_bot(
                    user_question=user_input,
                    portfolio_context=portfolio_context,
                    chat_history=st.session_state.messages
                )
                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
