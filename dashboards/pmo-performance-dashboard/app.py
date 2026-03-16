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
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None

# -----------------------------

# PAGE HEADER

# -----------------------------

st.title("Propel PMO Command Center")
st.caption(
"Executive dashboard for portfolio visibility, delivery health, risk monitoring, "
"AI project scoring, RAG status, PMO maturity, executive summary generation, "
"and AI-powered visitor support."
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

# -----------------------------

# DERIVED METRICS

# -----------------------------

risk_map = {"Low": 1, "Medium": 2, "High": 3}
df["Risk Score"] = df["Risk"].map(risk_map)

df["Overall Risk Score"] = (
df["Schedule Risk"]
+ df["Budget Risk"]
+ df["Delivery Risk"]
+ df["Data Risk"]
) / 4

def get_rag_status(row):
    if row["Completion"] < 60 or row["Overall Risk Score"] >= 4:
        return "Red"
    elif row["Completion"] < 75 or row["Overall Risk Score"] >= 3:
        return "Amber"
    else:
        return "Green"
        
df["RAG Status"] = df.apply(get_rag_status, axis=1)

# -----------------------------

# COLOR HELPER

# -----------------------------

def highlight_rag(val):
    if val == "Green":
        return "background-color:#d1fae5;color:#065f46;font-weight:bold"
    elif val == "Amber":
        return "background-color:#fef3c7;color:#92400e;font-weight:bold"
    elif val == "Red":
        return "background-color:#fee2e2;color:#991b1b;font-weight:bold"
    else:
        return ""

# -----------------------------

# HELPERS

# -----------------------------

def build_portfolio_summary(dataframe):
    avg_completion = round(dataframe["Completion"].mean(), 1)
    avg_ai_score = round(dataframe["AI Score"].mean(), 1)
    avg_risk_score = round(dataframe["Overall Risk Score"].mean(), 1)

    total_projects = len(dataframe)

    red_count = len(dataframe[dataframe["RAG Status"] == "Red"])
    amber_count = len(dataframe[dataframe["RAG Status"] == "Amber"])
    green_count = len(dataframe[dataframe["RAG Status"] == "Green"])

    return f"""
Propel PMO snapshot:
Total projects: {total_projects}
Average completion: {avg_completion}%
Average AI score: {avg_ai_score} / 5
Average overall risk score: {avg_risk_score} / 5
RAG distribution: Green={green_count}, Amber={amber_count}, Red={red_count}
"""

portfolio_context = build_portfolio_summary(df)

if "executive_summary" not in st.session_state:
    st.session_state.executive_summary = ""
# -----------------------------

# SESSION STATE

# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello — I’m the Propel PMO AI Assistant. "
                "I can explain AI PMO services, portfolio governance, delivery oversight, "
                "risk monitoring, RAG health, and PMO modernization."
            )
        }
    ]

# -----------------------------

# TABS

# -----------------------------

tab1, tab2 = st.tabs(["Dashboard", "AI PMO Chatbot"])

# -----------------------------

# DASHBOARD

# -----------------------------

with tab1:
    st.subheader("AI Executive Summary")
    st.caption("Click below to generate an AI summary for leadership.")

    if st.button("Generate Executive Summary", key="exec_summary_btn"):
        with st.spinner("Generating executive summary..."):
            st.session_state.executive_summary = generate_executive_summary(df)

    if st.session_state.executive_summary:
        st.info(st.session_state.executive_summary)
    
    rag_counts = df["RAG Status"].value_counts()
    red_count = int(rag_counts.get("Red", 0))
    amber_count = int(rag_counts.get("Amber", 0))
    green_count = int(rag_counts.get("Green", 0))

    st.subheader("Executive Scorecard")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("Portfolio Health Score", "82 / 100")
    col2.metric("Total Projects", len(df))
    col3.metric("Average Completion", f"{int(df['Completion'].mean())}%")
    col4.metric("Average AI Score", round(df["AI Score"].mean(), 1))
    col5.metric("Average Risk Score", round(df["Overall Risk Score"].mean(), 1))
    col6.metric("Red Projects", red_count)

    st.subheader("Project Portfolio")
    
    styled_df = df[
        [
            "Project",
            "Completion",
            "AI Score",
            "Risk",
            "Risk Score",
            "Overall Risk Score",
            "RAG Status",
        ]
    ].style.map(highlight_rag, subset=["RAG Status"])
    
    st.dataframe(styled_df, use_container_width=True)
    
    st.subheader("RAG Status Summary")
    
    rag_summary = pd.DataFrame(
        {
            "RAG Status": ["Green", "Amber", "Red"],
            "Count": [green_count, amber_count, red_count],
        }
    )
    
    fig_rag = px.bar(
        rag_summary,
        x="RAG Status",
        y="Count",
        color="RAG Status",
        category_orders={"RAG Status": ["Green", "Amber", "Red"]},
        color_discrete_map={
            "Green": "#22c55e",
            "Amber": "#f59e0b",
            "Red": "#ef4444",
        },
        title="Project Distribution by RAG Status",
    )
    
    st.plotly_chart(fig_rag, use_container_width=True)
    
    st.subheader("Delivery Trend")
    
    trend = pd.DataFrame(
        {
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Score": [68, 72, 75, 79, 83, 87],
        }
    )
    
    fig_trend = px.line(trend, x="Month", y="Score", markers=True)
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.subheader("AI Project Scoring")
    
    fig_score = px.bar(df, x="Project", y="AI Score")
    
    st.plotly_chart(fig_score, use_container_width=True)
    
    st.subheader("Risk Score by Project")
    
    fig_risk_score = px.bar(df, x="Project", y="Overall Risk Score", range_y=[0, 5])
    
    st.plotly_chart(fig_risk_score, use_container_width=True)

# -----------------------------

# CHATBOT

# -----------------------------

with tab2:

    st.subheader("AI PMO Chatbot")
    st.caption(
        "Ask about Propel PMO services, AI PMO strategy, governance, delivery, "
        "risk monitoring, RAG health, and modernization."
    )

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
        if cols[i].button(question, key=f"suggested_{i}"):
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
                reply = ask_propel_pmo_bot(
                    user_question=user_input,
                    portfolio_context=portfolio_context,
                    chat_history=st.session_state.messages
                )
                st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
