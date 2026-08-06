import streamlit as st
import pandas as pd
from google import genai
import time
import json
import re

# --- Page Configuration ---
st.set_page_config(page_title="FinAI | Smart Wealth", page_icon="🌍", layout="wide")

# --- Custom High UI/UX CSS (Green & Black Theme) ---
st.markdown("""
<style>
    /* Global Theme */
    .stApp {
        background-color: #050b07; /* Deep black with a hint of green */
        color: #a3e6b5; /* Soft green text */
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00ff66 !important; /* Neon green headers */
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #00ff66 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 10px rgba(0, 255, 102, 0.2);
    }
    .stButton>button:hover {
        background-color: #00cc52 !important;
        box-shadow: 0 0 20px rgba(0, 255, 102, 0.6);
        transform: translateY(-2px);
    }

    /* DataFrame / Data Editor */
    [data-testid="stDataFrame"] {
        background-color: #0a170f;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #1a3d24;
    }

    /* Glowing Green Globe for Savings */
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
        background: radial-gradient(circle at 30% 30%, #00ff66, #004d1f, #000000);
        box-shadow: 0 0 40px rgba(0, 255, 102, 0.5), inset -20px -20px 40px rgba(0,0,0,0.5);
        animation: pulse 4s infinite alternate;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        position: relative;
    }
    .globe-text {
        position: absolute;
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 900;
        text-shadow: 2px 2px 4px #000000;
        z-index: 2;
    }
    .globe-label {
        margin-top: 15px;
        font-size: 1.2rem;
        color: #00ff66;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 30px rgba(0, 255, 102, 0.4); transform: scale(1); }
        100% { box-shadow: 0 0 60px rgba(0, 255, 102, 0.8); transform: scale(1.02); }
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
st.sidebar.title("🌍 FinAI System")

st.sidebar.subheader("ℹ️ About the App")
st.sidebar.info(
    "A next-gen personal finance hub. Allocate funds intelligently, "
    "track daily expenses, and chat with an AI advisor to optimize your wealth."
)

st.sidebar.subheader("🛠️ Tech Stack")
st.sidebar.code("""
- Frontend: Streamlit
- Theme: Custom CSS (Green/Black)
- Engine: Pandas
- AI: Gemini 3.5 Flash
""", language="markdown")

st.sidebar.divider()
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")

# Currency Selector
currency_choice = st.sidebar.selectbox("Select Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "Custom"])
currency_sym = st.text_input("Custom Symbol", value="¤") if currency_choice == "Custom" else currency_choice.split("(")[1].replace(")", "")

# --- 1. Core Inputs ---
st.title("💸 AI Budget Terminal")

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
st.subheader("🤖 AI Auto-Allocator")
if st.button("Auto-Balance My Budget"):
    if not api_key:
        st.warning("API Key required.")
    else:
        with st.spinner("Calculating optimal zero-based budget..."):
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Income: {income}. Create a realistic budget. 
            MUST include "Traveling", "Fun Money", "Investments", and "Emergency Fund".
            Total must equal exactly {income}.
            Respond ONLY with a JSON array. Example: [{{"Category": "Housing", "Amount": 1500.0}}]
            """
            try:
                # Updated to request gemini-3.5-flash as per instructions
                response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
                raw_text = re.sub(r'```json|```', '', response.text).strip()
                start, end = raw_text.find('['), raw_text.rfind(']') + 1
                st.session_state.expenses_df = pd.DataFrame(json.loads(raw_text[start:end]))
                st.rerun()
            except Exception as e:
                st.error(f"Failed to auto-allocate: {e}")

# --- 3. Interactive Data Grid ---
st.subheader("📋 Expense Terminal")
edited_df = st.data_editor(st.session_state.expenses_df, num_rows="dynamic", use_container_width=True)
st.session_state.expenses_df = edited_df

# --- Calculations ---
total_allocated = edited_df["Amount"].sum()
unallocated_balance = income - total_allocated
savings_mask = edited_df["Category"].str.contains("invest|sav|emergency", case=False, na=False)
actual_savings = edited_df.loc[savings_mask, "Amount"].sum() + (unallocated_balance if unallocated_balance > 0 else 0)

# --- 4. The Green Globe Dashboard ---
st.markdown("---")
st.markdown(f"""
<div class="globe-container">
    <div class="globe">
        <div class="globe-text">{currency_sym}{actual_savings:,.0f}</div>
    </div>
    <div class="globe-label">Total Wealth Secured</div>
</div>
""", unsafe_allow_html=True)

col3, col4 = st.columns(2)
col3.metric("Total Allocated", f"{currency_sym}{total_allocated:,.2f}")
col4.metric("Unallocated (Zero-Based)", f"{currency_sym}{unallocated_balance:,.2f}")

# --- 5. Quick AI Chat Assistant ---
st.markdown("---")
st.subheader("💬 Quick Chat with FinAI")
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
            with st.spinner("Thinking..."):
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
