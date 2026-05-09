import os
import streamlit as st
import pandas as pd
import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from engine import analyze_symbol
from signal_memory import (
    init_db,
    log_signal,
    recent_signals,
    win_rate
)

# ---------------------------------------------------
# PAGE CONFIG

st.set_page_config(
    page_title="Kishore's Trading AI Assistant",
    layout="wide"
)

# ---------------------------------------------------
# LOAD CSS

def load_css():

    css_path = (
        Path(__file__).parent
        / "static"
        / "broker.css"
    )

    if css_path.exists():

        st.markdown(
            f"<style>{css_path.read_text()}</style>",
            unsafe_allow_html=True
        )

load_css()

# ---------------------------------------------------
# AI SETUP

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# ---------------------------------------------------
# DATABASE

init_db()

# ---------------------------------------------------
# SESSION STATE

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

# ---------------------------------------------------
# AI CHAT

def call_gemini(messages, analysis):

    system_prompt = f"""
You are Kishore's Trading AI Assistant.

Current Market:
Pair: {analysis.get('symbol')}
Trend: {analysis.get('trend')}
Signal: {analysis.get('signal')}
Confidence: {analysis.get('confidence')}%

Give professional forex trading assistant replies.
"""

    formatted_messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    for m in messages:

        formatted_messages.append({
            "role": m.get("role", "user"),
            "content": m.get("content", "")
        })

    try:

        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=formatted_messages
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"AI Error: {e}"

# ---------------------------------------------------
# BUTTON STYLE

st.markdown("""
<style>

div.stButton > button {

    background: linear-gradient(
        135deg,
        #00ff99,
        #00cc88
    ) !important;

    color: white !important;

    -webkit-text-fill-color: white !important;

    font-weight: 900 !important;

    font-size: 20px !important;

    border-radius: 16px !important;

    border: none !important;

    height: 56px !important;

    width: 260px !important;

    box-shadow:
        0 0 30px rgba(0,255,153,0.55) !important;
}

div.stButton > button p {

    color: white !important;

    font-weight: 900 !important;

    font-size: 20px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE

st.title("📈 Kishore's Trading AI Assistant")

# ---------------------------------------------------
# ASSISTANT BUTTON

if st.button("💬 Assistant"):

    st.session_state.show_chat = (
        not st.session_state.show_chat
    )

# ---------------------------------------------------
# SIDEBAR

pairs = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "USDCHF",
    "NZDUSD",
    "EURJPY",
    "GBPJPY",
    "XAUUSD"
]

selected_pair = st.sidebar.selectbox(
    "Select Forex Pair",
    pairs
)

# ---------------------------------------------------
# EXPIRY

def suggest_expiry(confidence):

    if confidence >= 85:
        return "30 Seconds"

    if confidence >= 70:
        return "1 Minute"

    if confidence >= 55:
        return "5 Minutes"

    return "15 Minutes"

# ---------------------------------------------------
# SIGNAL CARD

def generate_signal_card(
    signal,
    confidence,
    trend,
    price
):

    entry = (
        "NOW"
        if confidence >= 75
        else "WAIT"
    )

    signal_color = "#00ff99"

    emoji = "🟢"

    title = "TAKE BUY POSITION"

    reason = (
        "EMA crossover + bullish momentum + RSI confirmation"
    )

    if "SELL" in signal.upper():

        signal_color = "#ff4d6d"

        emoji = "🔴"

        title = "TAKE SELL POSITION"

        reason = (
            "EMA crossover + bearish momentum + RSI confirmation"
        )

    elif "HOLD" in signal.upper():

        signal_color = "#a1a1aa"

        emoji = "⚪"

        title = "WAIT FOR ENTRY"

    return f"""
<div style="
background:linear-gradient(
135deg,
rgba(15,23,42,0.95),
rgba(30,41,59,0.95)
);
padding:30px;
border-radius:24px;
border:2px solid {signal_color};
box-shadow:0 0 30px {signal_color};
margin-top:20px;
">

<h1 style="
color:{signal_color};
font-size:34px;
margin-bottom:20px;
text-align:center;
">
{emoji} {title}
</h1>

<div style="
font-size:18px;
line-height:2;
color:white;
">

<b>Confidence:</b> {confidence}%<br>

<b>Price Scale:</b> {price:.5f}<br>

<b>Trend:</b> {trend}<br>

<b>Entry:</b> {entry}<br>

<b>Expiry:</b> {suggest_expiry(confidence)}<br><br>

<b>Reason:</b><br>
{reason}

</div>

</div>
"""

# ---------------------------------------------------
# ANALYSIS

analysis = analyze_symbol(
    selected_pair,
    interval="5min"
)

confidence = analysis["confidence"]

trend = analysis["trend"]

signal = analysis["signal"]

ai_label = analysis["ai_label"]

price = analysis["price"]

# ---------------------------------------------------
# LOG SIGNAL

log_signal(
    pair=selected_pair,
    interval="5min",
    signal=signal,
    confidence=confidence,
    trend=trend,
    expiry=suggest_expiry(confidence),
    result=None
)

# ---------------------------------------------------
# MAIN SIGNAL

emoji = "⚪"

if "BUY" in ai_label.upper():
    emoji = "🟢"

elif "SELL" in ai_label.upper():
    emoji = "🔴"

st.success(
    f"""
{emoji} SIGNAL: {ai_label}

Confidence: {confidence}%

Trend: {trend}

Suggested Expiry:
{suggest_expiry(confidence)}
"""
)

# ---------------------------------------------------
# COUNTDOWN

now = datetime.datetime.utcnow()

interval_seconds = 300

seconds_left = int(
    interval_seconds -
    (
        now.timestamp()
        % interval_seconds
    )
)

st.caption(
    f"🕒 Next candle in {seconds_left}s"
)

# ---------------------------------------------------
# LIVE SIGNAL GENERATOR

st.markdown(
    "## 🚀 Live Signal Generator"
)

if st.button("⚡ Generate AI Signal"):

    signal_html = generate_signal_card(
        signal,
        confidence,
        trend,
        price
    )

    st.markdown(
        signal_html,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# ANALYTICS

st.markdown("## 📊 Signal Analytics")

recent = recent_signals(10)

wr = win_rate(
    pair=selected_pair
)

st.metric(
    "Win Rate",
    f"{round(wr * 100, 2)}%"
)

if recent:

    df_recent = pd.DataFrame(recent)

    st.dataframe(
        df_recent,
        use_container_width=True
    )

# ---------------------------------------------------
# TRADINGVIEW CHART

chart_url = (
    f"https://s.tradingview.com/widgetembed/"
    f"?symbol=FX:{selected_pair}"
    f"&interval=5"
    f"&theme=dark"
    f"&style=1"
)

st.components.v1.iframe(
    chart_url,
    height=520
)

# ---------------------------------------------------
# CHAT

if st.session_state.show_chat:

    st.subheader("🤖 Assistant Chat")

    for msg in st.session_state.chat_history:

        role = msg.get(
            "role",
            "assistant"
        )

        content = msg.get(
            "content",
            ""
        )

        if role == "user":

            st.markdown(
                f"**You:** {content}"
            )

        else:

            st.markdown(
                f"**Assistant:** {content}"
            )

    user_input = st.text_input(
        "Ask a question"
    )

    if st.button("Send") and user_input:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        response = call_gemini(
            st.session_state.chat_history,
            analysis
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        st.rerun()