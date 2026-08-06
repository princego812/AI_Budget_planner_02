import streamlit as st
import pandas as pd
from google import genai
import time
import json
import re

# --- Page Configuration ---
st.set_page_config(page_title="AI Budget Planner", page_icon="🌍", layout="wide")

# --- Custom CSS for Black/Green/White Theme & Green Globe ---
st.markdown("""
<style>
    /* Global Theme Overrides */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #ffffff !important;
    }
    
    /* Green Accents for Buttons and Inputs */
    .stButton>button {
        background-color: #16a34a !important;
        color: #ffffff !important;
        border: 1px solid #22c55e !important;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #15803d !important;
        box-shadow: 0 0 15px #22c55e;
    }
    
    /* The Animated Green Globe */
    .globe-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
    }
    .green-globe {
        width: 280px;
        height: 280px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #4ade80, #064e3b);
        box-shadow: 0 0 40px #22c55e, inset 0 0 30px #022c22;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        animation: pulse 3s infinite alternate;
        border: 2px solid #bbf7d0;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 30px #16a34a, inset 0 0 20px #022c22; }
        100% { box-shadow: 0 0 70px #4ade80, inset 0 0 40px #064e3b; }
    }
    .globe-label {
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #bbf7d0 !important;
        margin-bottom: 5px;
    }
    .globe-value {
        font-size: 3rem;
        font-weight: 900;
        text-shadow: 0 4px 10px rgba(0,0,0,0.8);
        color: #ffffff !important;
        line-height: 1.1;
    }
    .globe-subtext {
        font-size: 0.9rem;
        color: #dcfce7 !important;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/22c55e/globe.png", width=60)
    st.title("Settings")
    api_key = st.text_input("🔑 Gemini API Key", type="password", help="Required for AI features")
    
    st.divider()
    currency_choice = st.selectbox("Select Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "Custom"])
    if currency_choice == "Custom":
        currency_sym = st.text_input("Custom Symbol", value="¤")
    else:
        currency_sym = currency_choice.split("(")[1].replace(")", "")

# --- Main Dashboard Header ---
st.title("🌍 AI Wealth Dashboard")
st.write("Track expenses, auto-allocate funds, and chat with your AI advisor.")

# --- 1. Income & Goals ---
col1, col2 = st.columns(2)
with col1:
    income = st.number_input(f"Monthly Income ({currency_sym})", min_value=0.0, value=5000.0, step=100.0)
with col2:
    savings_goal = st.number_input(f"Monthly Savings Goal ({currency_sym})", min_value=0.0, value=1000.0, step=100.0)

# Initialize DataFrame
if "expenses_df" not in st.session_state:
    st.session_state.expenses_df = pd.DataFrame([
        {"Category": "Housing", "Amount": 1500.0},
        {"Category": "Groceries", "Amount": 400.0},
        {"Category": "Utilities", "Amount": 200.0},
        {"Category": "Fun Money", "Amount": 300.0},
        {"Category": "Investments", "Amount": 300.0},
        {"Category": "Emergency Fund", "Amount": 100.0},
    ])

# Calculate Live Savings for the Globe
current_df = st.session_state.expenses_df
total_allocated = current_df["Amount"].sum()
unallocated_balance = income - total_allocated
savings_mask = current_df["Category"].str.contains("invest|sav|emergency", case=False, na=False)
actual_savings = current_df.loc[savings_mask, "Amount"].sum() + (unallocated_balance if unallocated_balance > 0 else 0)
progress_pct = (actual_savings / savings_goal * 100) if savings_goal > 0 else 0

# --- 2. The Green Globe (Savings Visualizer) ---
st.markdown(f"""
<div class="globe-container">
    <div class="green-globe">
        <div class="globe-label">Total Saved</div>
        <div class="globe-value">{currency_sym}{actual_savings:,.0f}</div>
        <div class="globe-subtext">{progress_pct:.1f}% of Goal</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. Interactive Budget Table & AI Allocator ---
st.subheader("📊 Your Allocations")

if st.button("✨ Auto-Allocate with AI"):
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar.")
    else:
        with st.spinner("Optimizing your budget..."):
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Based on an income of {income}, create a zero-based budget.
            Include: "Housing", "Groceries", "Utilities", "Fun Money", "Investments", and "Emergency Fund".
            Total must equal {income}. Respond ONLY with a raw JSON array of objects.
            Example: [{{"Category": "Housing", "Amount": 1500.0}}]
            """
            try:
                # Using gemini-3.5-flash as requested
                response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
                raw_text = re.sub(r'```json|```', '', response.text).strip()
                start, end = raw_text.find('['), raw_text.rfind(']') + 1
                st.session_state.expenses_df = pd.DataFrame(json.loads(raw_text[start:end]))
                st.rerun()
            except Exception as e:
                st.error(f"Allocation Failed: {e}")

edited_df = st.data_editor(st.session_state.expenses_df, num_rows="dynamic", use_container_width=True)
st.session_state.expenses_df = edited_df

# Summary Metrics
col3, col4 = st.columns(2)
col3.metric("Total Allocated", f"{currency_sym}{edited_df['Amount'].sum():,.2f}")
col4.metric("Unallocated Balance", f"{currency_sym}{income - edited_df['Amount'].sum():,.2f}")

st.divider()

# --- 4. Chat with AI (Concise Mode) ---
st.subheader("💬 Chat with AI Advisor")
st.write("Ask any financial question. The AI is trained to answer in the absolute minimum sentences required.")

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Display previous messages
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if user_question := st.chat_input("E.g., Where should I invest my emergency fund?"):
    # Add user message to UI and state
    st.session_state.chat_messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please enter your Gemini API Key in the sidebar to chat.")
    else:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            client = genai.Client(api_key=api_key)
            
            # System instructions forcing minimum sentences + budget context
            expense_context = edited_df.to_string(index=False)
            full_prompt = f"""
            You are a hyper-concise financial advisor. 
            Rules: Give the absolute minimum number of sentences possible to answer the question. Do not exceed 3 sentences under any circumstances. Be direct and blunt.
            
            User's Current Context:
            - Income: {currency_sym}{income}
            - Savings: {currency_sym}{actual_savings}
            - Budget: \n{expense_context}
            
            User Question: {user_question}
            """
            
            try:
                # Using gemini-3.5-flash as requested
                response = client.models.generate_content(
                    model="gemini-3.5-flash", 
                    contents=full_prompt
                )
                message_placeholder.markdown(response.text)
                st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                message_placeholder.error(f"Error communicating with AI: {e}")
