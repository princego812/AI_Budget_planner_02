import streamlit as st
import pandas as pd
from google import genai
import time
import json

# --- Page Configuration ---
st.set_page_config(page_title="FinAI | Smart Wealth", page_icon="🟢", layout="wide")

# --- Custom High UI/UX CSS (Sleek Dark & Vibrant Green Theme) ---
st.markdown("""
<style>
    /* Global Theme: Deep Black Background, White Text */
    .stApp {
        background-color: #121212; 
        color: #FFFFFF; 
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar Background matching */
    [data-testid="stSidebar"] {
        background-color: #000000;
    }
    
    /* Headers: Pure White, Bold, Tight Tracking */
    h1, h2, h3 {
        color: #FFFFFF !important; 
        font-weight: 700 !important;
        letter-spacing: -0.04em;
    }
    
    /* Secondary Text / Captions */
    .stMarkdown p, .stCaption {
        color: #B3B3B3 !important;
    }
    
    /* Buttons: Vibrant Green, Pill-shaped, Bold Black Text */
    .stButton>button {
        background-color: #1DB954 !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 500px !important; /* Pill shape */
        font-weight: 700 !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #1ed760 !important;
        transform: scale(1.04);
        box-shadow: none !important;
    }

    /* DataFrame / Data Editor: Dark cards */
    [data-testid="stDataFrame"] {
        background-color: #181818;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }

    /* Glowing Green Globe for Savings */
    .globe-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        margin: 3rem 0;
    }
    .globe {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #1ed760, #1DB954, #121212);
        box-shadow: 0 0 40px rgba(29, 185, 84, 0.3), inset -15px -15px 30px rgba(0,0,0,0.7);
        animation: pulse 4s infinite alternate;
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
        font-weight: 900;
        text-shadow: 0px 2px 10px rgba(0,0,0,0.8);
        z-index: 2;
    }
    .globe-label {
        margin-top: 20px;
        font-size: 1rem;
        color: #B3B3B3;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 30px rgba(29, 185, 84, 0.2); transform: scale(1); }
        100% { box-shadow: 0 0 50px rgba(29, 185, 84, 0.5); transform: scale(1.02); }
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
st.sidebar.title("FinAI System")

st.sidebar.subheader("About the App")
st.sidebar.info(
    "A sleek, high-contrast personal finance hub. Allocate funds intelligently, "
    "track daily expenses, and chat with an AI advisor to optimize your wealth."
)

st.sidebar.subheader("Tech Stack")
st.sidebar.code("""
- Frontend: Streamlit
- UI/UX: Dark Mode Custom CSS
- Engine: Pandas
- AI: Gemini 3.5 Flash
""", language="markdown")

st.sidebar.divider()
api_key = st.sidebar.text_input("Gemini API Key", type="password")

# Currency Selector
currency_choice = st.sidebar.selectbox("Select Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "Custom"])
currency_sym = st.text_input("Custom Symbol", value="¤") if currency_choice == "Custom" else currency_choice.split("(")[1].replace(")", "")

# --- 1. Core Inputs ---
st.title("AI Budget Terminal")

col1, col2 = st.columns(2)
with col1:
    income = st.number_input(f"Monthly Income ({currency_sym})", min_value=0.0, value=5000.0, step=100.0)
with col2:
    savings_goal = st.number_input(f"Savings Target ({currency_sym})", min_value=0.0, value=1000.0, step=100.0)

# Initialize DataFrame with 'Traveling' expense included
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
st.subheader("AI Auto-Allocator")
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
                response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
                
                # SAFELY parse the JSON response (fixed the SyntaxError here)
                raw_text = response.text.replace("```json", "").replace("```", "").strip()
                start = raw_text.find('[')
                end = raw_text.rfind(']') + 1
                
                st.session_state.expenses_df = pd.DataFrame(json.loads(raw_text[start:end]))
                st.rerun()
            except Exception as e:
                st.error(f"Failed to auto-allocate: {e}")

# --- 3. Interactive Data Grid ---
st.subheader("Expense Breakdown")
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
st.subheader("Quick Chat with FinAI")
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
