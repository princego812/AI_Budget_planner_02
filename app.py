import streamlit as st
import pandas as pd
from google import genai
import time
import json
import re

# --- Page Configuration ---
st.set_page_config(page_title="FinAI | Budget Studio", page_icon="🎧", layout="wide")

# --- Custom High UI/UX CSS (Deep Black, White, & Vibrant Green Theme) ---
st.markdown("""
<style>
    /* Global Theme - Deep Black */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Text Readability (White and Light Gray) */
    p, .stMarkdown, label, .stMetric label {
        color: #B3B3B3 !important; /* Light gray for secondary text */
    }
    
    /* Headers (Stark White) */
    h1, h2, h3 {
        color: #FFFFFF !important; 
        font-weight: 700 !important;
        letter-spacing: -0.04em;
    }
    
    /* Accent Color - Vibrant Green */
    .accent-text {
        color: #1ED760 !important;
    }
    
    /* Buttons - Pill Shaped */
    .stButton>button {
        background-color: #1ED760 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 500px !important; /* Perfect pill shape */
        font-weight: 700 !important;
        padding: 0.5rem 2rem !important;
        transition: transform 0.2s ease, background-color 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #1fdf64 !important; /* Slightly lighter green on hover */
        transform: scale(1.04);
    }

    /* DataFrame / Data Editor Container */
    [data-testid="stDataFrame"] {
        background-color: #181818;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #282828;
    }

    /* Metric Values */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* Glowing Green Savings Ring (Record Vibe) */
    .globe-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        margin: 2rem 0;
    }
    .globe {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: #181818;
        border: 6px solid #1ED760;
        box-shadow: 0 0 30px rgba(30, 215, 96, 0.3);
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        position: relative;
    }
    .globe-text {
        position: absolute;
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: 800;
        z-index: 2;
    }
    .globe-label {
        margin-top: 15px;
        font-size: 0.9rem;
        color: #B3B3B3;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
st.sidebar.title("📻 FinAI Studio")

st.sidebar.subheader("ℹ️ About the App")
st.sidebar.info(
    "A sleek, high-fidelity personal finance hub. Allocate funds intelligently, "
    "track daily expenses, and chat with an AI advisor to optimize your rhythm of wealth. 🎶"
)

st.sidebar.subheader("🛠️ Tech Stack")
st.sidebar.code("""
- Frontend: Streamlit
- Theme: Deep Black & Vibrant Green
- Data Grid: Pandas
- AI Engine: Gemini 3.5 Flash
""", language="markdown")

st.sidebar.divider()
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")

# Currency Selector
currency_choice = st.sidebar.selectbox("Select Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "Custom"])
currency_sym = st.text_input("Custom Symbol", value="¤") if currency_choice == "Custom" else currency_choice.split("(")[1].replace(")", "")

# --- 1. Core Inputs ---
st.title("🎵 AI Budget Studio 🎧")

col1, col2 = st.columns(2)
with col1:
    income = st.number_input(f"Monthly Income ({currency_sym})", min_value=0.0, value=5000.0, step=100.0)
with col2:
    savings_goal = st.number_input(f"Savings Target ({currency_sym})", min_value=0.0, value=1000.0, step=100.0)

# Initialize DataFrame with 'Traveling' expense added
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
st.subheader("🎛️ AI Auto-Mixer (Allocator)")
if st.button("Auto-Balance My Budget"):
    if not api_key:
        st.warning("API Key required in the sidebar to remix your budget.")
    else:
        with st.spinner("Mixing the perfect zero-based budget..."):
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Income: {income}. Create a realistic budget. 
            MUST include "Traveling", "Fun Money", "Investments", and "Emergency Fund".
            Total must equal exactly {income}.
            Respond ONLY with a JSON array. Example: [{{"Category": "Housing", "Amount": 1500.0}}]
            """
            try:
                # Requesting gemini-3.5-flash
                response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
                raw_text = re.sub(r'```json|```', '', response.text).strip()
                start, end = raw_text.find('['), raw_text.rfind(']') + 1
                st.session_state.expenses_df = pd.DataFrame(json.loads(raw_text[start:end]))
                st.rerun()
            except Exception as e:
                st.error(f"Failed to auto-allocate: {e}")

# --- 3. Interactive Data Grid ---
st.subheader("🎚️ Expense Playlist")
edited_df = st.data_editor(st.session_state.expenses_df, num_rows="dynamic", use_container_width=True)
st.session_state.expenses_df = edited_df

# --- Calculations ---
total_allocated = edited_df["Amount"].sum()
unallocated_balance = income - total_allocated
savings_mask = edited_df["Category"].str.contains("invest|sav|emergency", case=False, na=False)
actual_savings = edited_df.loc[savings_mask, "Amount"].sum() + (unallocated_balance if unallocated_balance > 0 else 0)

# --- 4. The Glowing Savings Ring Dashboard ---
st.markdown("---")
st.markdown(f"""
<div class="globe-container">
    <div class="globe">
        <div class="globe-text">{currency_sym}{actual_savings:,.0f}</div>
    </div>
    <div class="globe-label">Total Wealth Secured</div>
</div>
""", unsafe_allow_html=True)

st.write("") # Spacer
col3, col4 = st.columns(2)
col3.metric("Total Allocated", f"{currency_sym}{total_allocated:,.2f}")
col4.metric("Unallocated (Zero-Based)", f"{currency_sym}{unallocated_balance:,.2f}")

# --- 5. Quick AI Chat Assistant ---
st.markdown("---")
st.subheader("🎙️ Live AI Chat Session")
st.caption("Ask quick financial questions. I will reply in the absolute minimum sentences needed.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about your budget, investments, or travel hacks..."):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to chat.")
    else:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare context for the AI
        expense_str = edited_df.to_string(index=False)
        system_context = f"""
        You are FinAI, a precise financial assistant.
        User's current budget data:
        Income: {currency_sym}{income} | Savings/Investments: {currency_sym}{actual_savings}
        Breakdown: {expense_str}
        
        CRITICAL INSTRUCTION: You must answer in the ABSOLUTE MINIMUM sentences needed. Be incredibly brief, direct, and ruthless with your word count.
        """

        # Call Gemini 3.5 Flash
        with st.chat_message("assistant"):
            with st.spinner("Tuning the response..."):
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
