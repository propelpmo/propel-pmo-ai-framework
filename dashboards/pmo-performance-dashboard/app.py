import os
import re
import json
import smtplib
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Propel PMO Command Center", layout="wide")

# =========================================================
# APP CONFIG
# =========================================================
USAGE_FILE = "chat_usage.json"
QUESTION_LIMIT = 1
CONTACT_URL = "https://propelpmo.com/contact/"

SYSTEM_PROMPT = """
You are the Propel PMO AI Assistant.

Your purpose is to answer ONLY questions related to:
- AI PMO strategy
- PMO governance
- portfolio management
- delivery oversight
- risk monitoring
- executive reporting
- PMO modernization
- project/program governance
- Propel PMO services

Rules:
1. Stay strictly within Propel PMO, AI PMO, PMO governance, portfolio analytics, delivery oversight, executive reporting, and consulting-related topics.
2. Do not answer general knowledge questions.
3. Do not provide coding help, homework help, legal advice, medical advice, financial advice, personal advice, or unrelated business advice.
4. If a question is outside scope, politely refuse and redirect the user to ask about AI PMO, PMO governance, portfolio reporting, delivery oversight, or Propel PMO services.
5. Keep answers concise, professional, and business-focused.
6. When appropriate, encourage the visitor to contact Propel PMO for a tailored consultation.
7. If company-specific knowledge is provided in context, use it. If not, answer conservatively and do not invent offerings.
"""

OUT_OF_SCOPE_MESSAGE = """
I’m designed to answer questions about Propel PMO services, AI PMO strategy, portfolio governance, delivery oversight, risk monitoring, and executive reporting.

Please ask a PMO- or AI-governance-related question, or contact Propel PMO for a tailored discussion.
"""

LIMIT_MESSAGE = f"""
You’ve reached the {QUESTION_LIMIT}-question limit for this AI PMO chatbot.

For a deeper discussion on AI PMO strategy, portfolio governance, executive reporting, or PMO transformation, please contact Propel PMO.
"""

# =========================================================
# EMAIL HELPER
# =========================================================
def send_prechat_email(name, email, company, role, interest):
    sender_email = st.secrets["EMAIL_SENDER"]
    sender_password = st.secrets["EMAIL_PASSWORD"]
    receiver_email = "support@propelpmo.com"

    subject = "New AI Chatbot Access Request - Propel PMO"

    body = f"""
A new visitor requested access to the Propel PMO AI Chatbot.

Name: {name}
Email: {email}
Company: {company}
Role / Title: {role}
Primary Interest: {interest}
Submitted At: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

# =========================================================
# HELPERS
# =========================================================
def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_usage(data):
    try:
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def normalize_email(email: str) -> str:
    return email.strip().lower()

def valid_email(email: str) -> bool:
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email.strip()))

def is_in_scope(user_text: str) -> bool:
    allowed_keywords = [
        "ai pmo", "pmo", "portfolio", "governance", "delivery",
        "risk", "executive reporting", "reporting", "modernization",
        "program management", "project management", "transformation",
        "dashboard", "portfolio health", "project risk",
        "propel pmo", "governance model", "operating model",
        "project governance", "portfolio governance", "ai governance",
        "executive summary", "pmo maturity", "rag", "delivery oversight"
    ]
    text = user_text.lower()
    return any(keyword in text for keyword in allowed_keywords)

def get_rag_context(user_query: str) -> str:
    """
    Placeholder for future RAG integration.
    """
    return ""

def get_openai_client():
    api_key = ""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key or OpenAI is None:
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None

def generate_chat_response(chat_history: list, user_question: str) -> str:
    client = get_openai_client()
    if client is None:
        return (
            "The AI service is not configured right now. Please add your OPENAI_API_KEY "
            "to Streamlit secrets and try again."
        )

    rag_context = get_rag_context(user_question)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if rag_context:
        messages.append(
            {
                "role": "system",
                "content": f"Relevant Propel PMO knowledge:\n{rag_context}"
            }
        )

    messages.extend(chat_history)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred while generating the response: {e}"

def rag_color(val):
    if val == "Green":
        return "background-color: #2ecc71; color: white;"
    elif val == "Amber":
        return "background-color: #f39c12; color: white;"
    elif val == "Red":
        return "background-color: #e74c3c; color: white;"
    return ""

# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "lead_verified" not in st.session_state:
    st.session_state.lead_verified = False

if "lead_name" not in st.session_state:
    st.session_state.lead_name = ""

if "lead_email" not in st.session_state:
    st.session_state.lead_email = ""

if "lead_company" not in st.session_state:
    st.session_state.lead_company = ""

if "lead_role" not in st.session_state:
    st.session_state.lead_role = ""

if "lead_interest" not in st.session_state:
    st.session_state.lead_interest = ""

if "show_post_chat_form" not in st.session_state:
    st.session_state.show_post_chat_form = False

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# =========================================================
# PAGE HEADER
# =========================================================
st.title("Propel PMO Command Center")
st.caption(
    "Executive dashboard for portfolio visibility, delivery health, risk monitoring, "
    "AI-assisted PMO insights, and modernization."
)

# =========================================================
# SAMPLE DATA
# =========================================================
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
    "RAG Status": ["Green", "Green", "Red", "Amber", "Amber"],
    "Schedule Risk": [3, 2, 5, 4, 3],
    "Budget Risk": [2, 2, 4, 5, 3],
    "Delivery Risk": [3, 2, 4, 5, 3],
    "Data Risk": [2, 1, 4, 3, 2]
}

df = pd.DataFrame(data)
df["RAG Status"] = df["RAG Status"].astype(str)

risk_map = {"Low": 1, "Medium": 2, "High": 3}
df["Risk Score"] = df["Risk"].map(risk_map)

# =========================================================
# TABS - ONLY 2
# =========================================================
tab1, tab2 = st.tabs(["Dashboard", "AI PMO Chatbot"])

# =========================================================
# TAB 1 - DASHBOARD
# =========================================================
with tab1:
    st.subheader("Executive Scorecard")

    red_count = int((df["RAG Status"] == "Red").sum())
    amber_count = int((df["RAG Status"] == "Amber").sum())
    green_count = int((df["RAG Status"] == "Green").sum())

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Portfolio Health Score", "82 / 100")
    col2.metric("Total Projects", len(df))
    col3.metric("Average Completion", f"{int(df['Completion'].mean())}%")
    col4.metric("Average AI Score", round(df["AI Score"].mean(), 1))
    col5.metric("Green Projects", green_count)
    col6.metric("Red Projects", red_count)

    st.subheader("Portfolio RAG Distribution")
    rag_counts = df["RAG Status"].value_counts()
    fig_rag = px.pie(
        values=rag_counts.values,
        names=rag_counts.index,
        color=rag_counts.index,
        color_discrete_map={
            "Green": "#2ecc71",
            "Amber": "#f39c12",
            "Red": "#e74c3c"
        },
        title="RAG Status Distribution"
    )
    st.plotly_chart(fig_rag, use_container_width=True)

    st.subheader("Project Portfolio")
    styled_df = df[["Project", "Completion", "AI Score", "Risk", "RAG Status"]].style.map(
        rag_color, subset=["RAG Status"]
    )
    st.dataframe(styled_df, use_container_width=True)

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

    st.subheader("Portfolio Risk Heatmap")
    fig_heatmap = px.scatter(
        df,
        x="Completion",
        y="Risk Score",
        size="AI Score",
        color="Risk",
        color_discrete_map={
            "Low": "#2ecc71",
            "Medium": "#f39c12",
            "High": "#e74c3c"
        },
        hover_name="Project",
        hover_data={
            "Completion": True,
            "Risk Score": False,
            "AI Score": True,
            "Risk": True
        },
        title="Portfolio Risk vs Completion"
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


# =========================================================
# TAB 2 - AI PMO CHATBOT
# =========================================================
with tab2:

    st.subheader("AI PMO Chatbot")
    st.caption(
        "This assistant is limited to AI PMO, PMO governance, portfolio delivery, "
        "risk monitoring, executive reporting, and Propel PMO services."
    )

    usage_db = load_usage()

    # -----------------------------------------------------
    # PRE-CHAT LEAD FORM
    # -----------------------------------------------------
    if not st.session_state.lead_verified:

        st.info("Please complete this short form to access the chatbot.")

        with st.form("pre_chat_lead_form"):

            name = st.text_input("Full Name")
            email = st.text_input("Business Email")
            company = st.text_input("Company")
            role = st.text_input("Role / Title")

            interest = st.selectbox(
                "Primary Interest",
                [
                    "AI PMO Strategy",
                    "PMO Governance",
                    "Portfolio Reporting",
                    "Delivery Oversight",
                    "Risk Monitoring",
                    "PMO Modernization",
                    "General Inquiry"
                ]
            )

            start_chat = st.form_submit_button("Start Chat")

        if start_chat:

            if not name.strip():
                st.error("Please enter your name.")

            elif not valid_email(email):
                st.error("Please enter a valid email address.")

            else:

                clean_email = normalize_email(email)

                st.session_state.lead_verified = True
                st.session_state.lead_name = name.strip()
                st.session_state.lead_email = clean_email
                st.session_state.lead_company = company.strip()
                st.session_state.lead_role = role.strip()
                st.session_state.lead_interest = interest
                st.session_state.messages = []

                if clean_email not in usage_db:

                    usage_db[clean_email] = {
                        "count": 0,
                        "first_seen": datetime.now().isoformat(),
                        "name": name.strip(),
                        "company": company.strip(),
                        "role": role.strip(),
                        "interest": interest
                    }

                    save_usage(usage_db)

                # Optional email notification
                # send_prechat_email(name, clean_email, company, role, interest)

                st.rerun()

        st.stop()

    # -----------------------------------------------------
    # CHATBOT ACTIVE
    # -----------------------------------------------------
    visitor_email = st.session_state.lead_email

    if visitor_email not in usage_db:

        usage_db[visitor_email] = {
            "count": 0,
            "first_seen": datetime.now().isoformat(),
            "name": st.session_state.lead_name,
            "company": st.session_state.lead_company,
            "role": st.session_state.lead_role,
            "interest": st.session_state.lead_interest
        }

        save_usage(usage_db)

    current_count = int(usage_db[visitor_email].get("count", 0))
    remaining = max(0, QUESTION_LIMIT - current_count)

    st.success("Chatbot unlocked.")

    st.write(f"**Visitor:** {st.session_state.lead_name}")
    st.write(f"**Email:** {st.session_state.lead_email}")

    st.caption(f"Questions remaining: {remaining} of {QUESTION_LIMIT}")

    # -----------------------------------------------------
    # LIMIT REACHED
    # -----------------------------------------------------
    if current_count >= QUESTION_LIMIT:

        st.warning(LIMIT_MESSAGE)
        st.markdown(f"[Go to Contact Form]({CONTACT_URL})")

        st.session_state.show_post_chat_form = True

    # -----------------------------------------------------
    # CHAT HISTORY
    # -----------------------------------------------------
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # -----------------------------------------------------
    # SUGGESTED QUESTIONS
    # -----------------------------------------------------
    suggested_questions = [

        "What does an AI PMO do?",
        "How can Propel PMO improve portfolio governance?",
        "How does AI help executive reporting?",
        "What PMO modernization services does Propel PMO offer?"

    ]

    st.write("Try one of these questions:")

    cols = st.columns(len(suggested_questions))

    for i, question in enumerate(suggested_questions):

        key = f"chatbot_question_{i}"

        if cols[i].button(question, key=key, disabled=current_count >= QUESTION_LIMIT):
            st.session_state.pending_question = question

    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------
    user_input = st.chat_input(
        "Ask about AI PMO, PMO governance, delivery oversight, risk monitoring, or Propel PMO services",
        disabled=current_count >= QUESTION_LIMIT
    )

    if st.session_state.pending_question and not user_input and current_count < QUESTION_LIMIT:

        user_input = st.session_state.pending_question
        st.session_state.pending_question = None

    # -----------------------------------------------------
    # PROCESS CHAT
    # -----------------------------------------------------
    if user_input and current_count < QUESTION_LIMIT:

        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        if not is_in_scope(user_input):

            assistant_reply = OUT_OF_SCOPE_MESSAGE

        else:

            assistant_reply = generate_chat_response(
                st.session_state.messages,
                user_input
            )

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })

        usage_db[visitor_email]["count"] = current_count + 1
        usage_db[visitor_email]["last_question_at"] = datetime.now().isoformat()

        save_usage(usage_db)

        new_remaining = max(0, QUESTION_LIMIT - usage_db[visitor_email]["count"])

        st.caption(f"Questions remaining: {new_remaining} of {QUESTION_LIMIT}")

        st.info(
            "Need a tailored discussion? Contact Propel PMO for a consultation."
        )

        st.markdown(f"[Contact Propel PMO]({CONTACT_URL})")

        if usage_db[visitor_email]["count"] >= QUESTION_LIMIT:
            st.session_state.show_post_chat_form = True

    # -----------------------------------------------------
    # POST CHAT LEAD FORM
    # -----------------------------------------------------
    if st.session_state.show_post_chat_form or current_count >= QUESTION_LIMIT:

        st.markdown("---")
        st.subheader("Request a Follow-Up")

        with st.form("post_chat_sales_form"):

            followup_name = st.text_input(
                "Name",
                value=st.session_state.lead_name
            )

            followup_email = st.text_input(
                "Email",
                value=st.session_state.lead_email
            )

            followup_company = st.text_input(
                "Company",
                value=st.session_state.lead_company
            )

            followup_role = st.text_input(
                "Role / Title",
                value=st.session_state.lead_role
            )

            service_interest = st.selectbox(
                "Service of Interest",
                [
                    "AI PMO Advisory",
                    "PMO Governance Design",
                    "Portfolio Dashboard / Reporting",
                    "Risk Monitoring Framework",
                    "PMO Modernization",
                    "Executive PMO Consulting"
                ]
            )

            timeline = st.selectbox(
                "Desired Timeline",
                [
                    "Immediately",
                    "This Month",
                    "This Quarter",
                    "Exploring Options"
                ]
            )

            notes = st.text_area(
                "How can Propel PMO help?",
                placeholder="Share your portfolio, PMO, governance, reporting, or AI transformation needs."
            )

            submit_followup = st.form_submit_button("Submit Inquiry")

        if submit_followup:

            st.success(
                "Thank you. Your interest has been captured for follow-up."
            )

            st.markdown(f"[Continue to Contact Form]({CONTACT_URL})")


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.caption(
    "Note: Email-based usage limits are enabled. IP-based control usually requires "
    "a backend or reverse proxy and is not reliably available in basic Streamlit deployments."
)
