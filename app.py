import streamlit as st
import pandas as pd
from google import genai
import time
import json
import re

# --- Page Configuration ---
st.set_page_config(page_title="FinAI | Smart Wealth", page_icon="🎵", layout="wide")

# --- Custom Spotify UI/UX CSS ---
st.markdown("""
<style>
    /* Spotify Core Palette */
    :root {
        --spotify-black: #000000;
        --spotify-bg: #121212;
        --spotify-surface: #181818;
        --spotify-surface-hover: #282828;
        --spotify-green: #1DB954;
        --spotify-green-hover: #1ED760;
        --spotify-text-primary: #FFFFFF;
        --spotify-text-secondary: #B3B3B3;
    }

    /* Main App Background */
    .stApp {
        background-color: var(--spotify-bg);
        color: var(--spotify-text-primary);
        font-family: 'Circular', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar (Pure Black like Spotify Desktop) */
    [data-testid="stSidebar"] {
        background-color: var(--spotify-black) !important;
    }
    
    /* Typography Overrides */
    h1, h2, h3, .st-emotion-cache-1629p8f h1 {
        color: var(--spotify-text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.04em;
    }
    p, label, .st-emotion-cache-1n76uvr {
        color: var(--spotify-text-secondary) !important;
    }
    
    /* Input Fields */
    .stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: var(--spotify-surface) !important;
        color: var(--spotify-text-primary) !important;
        border: 1px solid transparent !important;
        border-radius: 4px !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        border: 1px solid var(--spotify-text-secondary) !important;
    }
    
    /* Buttons (The Spotify Play/Action Button) */
    .stButton>button {
        background-color: var(--spotify-green) !important;
        color: var(--spotify-black) !important;
        border: none !important;
        border-radius: 500px !important; /* Fully rounded */
        font-weight: 700 !important;
        padding: 0.5rem 2rem !important;
        text-transform: none !important;
        transition: transform 0.1s ease, background-color 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: var(--spotify-green-hover) !important;
        transform: scale(1.04);
    }

    /* DataFrame / Data Editor (Like a Tracklist) */
    [data-testid="stDataFrame"] {
        background-color: var(--spotify-surface);
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    
    /* Divider Lines */
    hr {
        border-color: var(--spotify-surface-hover) !important;
    }

    /* Artist Profile Style Savings Visual */
    .artist-profile-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        margin: 3rem 0;
    }
    .artist-circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background-color: var(--spotify-surface);
        border: 4px solid var(--spotify-green);
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        transition: transform 0.3s ease;
    }
    .artist-circle:hover {
        transform: scale(1.02);
    }
    .artist-stat {
        color: var(--spotify-text-primary);
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .artist-label {
        margin-top: 15px;
        font-size: 0.9rem;
        color: var(--spotify-text-secondary);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Metrics overriding */
    [data-testid="stMetricValue"] {
        color: var(--spotify-text-primary) !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--spotify-text-secondary) !important;
    }
    
    /* Info Box */
    .stAlert {
        background-color: var(--spotify-surface) !important;
        color: var(--spotify-text-primary) !important;
        border: none !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
st.sidebar.title("FinAI Premium")

st.sidebar.subheader("ℹ️ About")
st.sidebar.info(
    "A next-gen personal finance hub tuned to your rhythm. Allocate funds, "
    "track daily expenses, and chat with an AI advisor to optimize your wealth."
)

st.sidebar.subheader("🛠️ Your Stack")
st.sidebar.code("""
- Frontend: Streamlit
- Theme: Spotify Dark Mode
- Engine: Pandas
- AI: Gemini 3.5 Flash
""", language="markdown")

st.sidebar.divider()
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")

# Currency Selector
currency_choice = st.sidebar.selectbox("Select Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "Custom"])
currency_sym = st.text_input("Custom Symbol", value="¤") if currency_choice == "Custom" else currency_choice.split("(")[1].replace(")", "")

# --- 1. Core Inputs ---
st.title("Your Financial Playlist")

col1, col2 = st.columns(2)
with col1:
    income = st.number_input(f"Monthly Income ({currency_sym})", min_value=0.0, value=5000.0, step=100.0)
with col2:
    savings_goal = st.number_input(f"Savings Target ({currency_sym})", min_value=0.0, value=1000.0, step=100.0)

# Initialize DataFrame
if "expenses_df" not in st.session_state:
    st.session_state.expenses_df = pd.DataFrame([
        {"Category": "Housing", "Amount": 1500.0},
        {"Category": "Groceries", "Amount": 400.0},
        {"Category": "Traveling", "Amount": 250.0},
        {"Category": "Utilities", "Amount": 200.0},
        {"Category": "Fun Money", "Amount": 300.0},
        {"Category": "Investments", "Amount": 300.0},
        {"Category": "Emergency Fund", "Amount": 100.0},
    ])

# --- 2. Auto-Allocate Button ---
st.subheader("Discover Weekly: AI Auto-Allocator")
if st.button("Auto-Balance My Budget", use_container_width=True):
    if not api_key:
        st.warning("API Key required in the sidebar.")
    else:
        with st.spinner("Curating your perfect zero-based budget..."):
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Income: {income}. Create a realistic budget. 
            MUST include "Traveling", "Fun Money", "Investments", and "Emergency Fund".
            Total must equal exactly {income}.
            Respond ONLY with a JSON array. Example: [{{"Category": "Housing", "Amount": 1500.0}}]
            """
            try:
                response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
                raw_text = re.sub(r'```json|```', '', response.text).strip()
                start, end = raw_text.find('['), raw_text.rfind(']') + 1
                st.session_state.expenses_df = pd.DataFrame(json.loads(raw_text[start:end]))
                st.rerun()
            except Exception as e:
                st.error(f"Failed to auto-allocate: {e}")

# --- 3. Interactive Data Grid (The Tracklist) ---
st.subheader("Your Expense Tracklist")
edited_df = st.data_editor(st.session_state.expenses_df, num_rows="dynamic", use_container_width=True)
st.session_state.expenses_df = edited_df

# --- Calculations ---
total_allocated = edited_df["Amount"].sum()
unallocated_balance = income - total_allocated
savings_mask = edited_df["Category"].str.contains("invest|sav|emergency", case=False, na=False)
actual_savings = edited_df.loc[savings_mask, "Amount"].sum() + (unallocated_balance if unallocated_balance > 0 else 0)

# --- 4. The Profile Dashboard ---
st.markdown("---")
st.markdown(f"""
<div class="artist-profile-container">
    <div class="artist-circle">
        <div class="artist-stat">{currency_sym}{actual_savings:,.0f}</div>
    </div>
    <div class="artist-label">Total Wealth Secured</div>
</div>
""", unsafe_allow_html=True)

col3, col4 = st.columns(2)
col3.metric("Total Allocated", f"{currency_sym}{total_allocated:,.2f}")
col4.metric("Unallocated (Zero-Based)", f"{currency_sym}{unallocated_balance:,.2f}")

# --- 5. Quick AI Chat Assistant ---
st.markdown("---")
st.subheader("Chat with FinAI")
st.caption("Drop a question. I'll answer in the absolute minimum sentences.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your budget, investments, or travel hacks..."):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to chat.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        expense_str = edited_df.to_string(index=False)
        system_context = f"""
        You are FinAI, a precise financial assistant.
        User's current budget data:
        Income: {currency_sym}{income} | Savings/Investments: {currency_sym}{actual_savings}
        Breakdown: {expense_str}
        
        CRITICAL INSTRUCTION: You must answer in the ABSOLUTE MINIMUM sentences needed. Be incredibly brief, direct, and ruthless with your word count.
        """

        with st.chat_message("assistant"):
            with st.spinner("Analyzing audio... I mean, finances..."):
                try:
                    client = genai.Client(api_key=api_key)
                    full_prompt = f"{system_context}\n\nUser Question: {prompt}"
                    
                    response = client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=full_prompt
                    )
                    
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Chat API Error: {e}")
