import streamlit as st
import pandas as pd
from google import genai
import time
import json
import re

# --- Page Configuration ---
st.set_page_config(page_title="FinAI Planner", page_icon="💎", layout="wide")

# --- High-End UI/UX Custom CSS ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* Background Image and Base Styles */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.95)), 
                    url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
        color: #F8FAFC;
    }
    
    /* Glassmorphism for Metrics and Containers */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #F8FAFC !important;
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #06B6D4;
    }
    
    /* Headers and Text */
    h1, h2, h3 {
        color: #E2E8F0 !important;
        font-weight: 600;
    }
    .glow-text {
        background: -webkit-linear-gradient(45deg, #06B6D4, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("<h2>⚙️ Settings</h2>", unsafe_allow_html=True)
    api_key = st.text_input("🔑 Gemini API Key", type="password", help="Required for AI features")
    st.divider()
    currency_choice = st.selectbox("Select Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "Custom"])
    if currency_choice == "Custom":
        currency_sym = st.text_input("Custom Symbol", value="¤")
    else:
        currency_sym = currency_choice.split("(")[1].replace(")", "")
    
    st.divider()
    st.caption("Built with Streamlit & Gemini 2.5 Flash")

# --- App Header ---
st.markdown('<div class="glow-text">💎 AI Wealth Dashboard</div>', unsafe_allow_html=True)
st.write("Manage your cash flow, automate allocations, and chat directly with your AI financial advisor.")

# --- State Management for Budget & Chat ---
if "expenses_df" not in st.session_state:
    st.session_state.expenses_df = pd.DataFrame([
        {"Category": "Housing", "Amount": 1500.0},
        {"Category": "Groceries", "Amount": 400.0},
        {"Category": "Utilities", "Amount": 200.0},
        {"Category": "Fun Money", "Amount": 300.0},
        {"Category": "Investments", "Amount": 300.0},
        {"Category": "Emergency Fund", "Amount": 100.0},
    ])
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI financial advisor. How can I help optimize your money today?"}]

# --- Navigation Tabs ---
tab_dashboard, tab_chat = st.tabs(["📊 Budget Dashboard", "💬 FinChat (AI Advisor)"])

# ==========================================
# TAB 1: DASHBOARD
# ==========================================
with tab_dashboard:
    col_inc, col_sav = st.columns(2)
    with col_inc:
        income = st.number_input(f"Monthly Income ({currency_sym})", min_value=0.0, value=5000.0, step=100.0)
    with col_sav:
        savings_goal = st.number_input(f"Monthly Savings Goal ({currency_sym})", min_value=0.0, value=1000.0, step=100.0)

    # Core Calculations
    total_allocated = st.session_state.expenses_df["Amount"].sum()
    unallocated = income - total_allocated
    savings_mask = st.session_state.expenses_df["Category"].str.contains("invest|sav|emergency", case=False, na=False)
    actual_savings = st.session_state.expenses_df.loc[savings_mask, "Amount"].sum() + (unallocated if unallocated > 0 else 0)

    # Metrics Display
    st.write("### 📈 Live Overview")
    met1, met2, met3 = st.columns(3)
    met1.metric("Total Allocated", f"{currency_sym}{total_allocated:,.2f}")
    met2.metric("Unallocated Balance", f"{currency_sym}{unallocated:,.2f}", "Aim for 0")
    met3.metric("Goal Progress", f"{(actual_savings / savings_goal * 100) if savings_goal > 0 else 0:.1f}%")

    st.divider()

    # Data & AI Allocation
    col_table, col_ai = st.columns([2, 1])
    
    with col_table:
        st.write("### 📝 Edit Expenses")
        edited_df = st.data_editor(st.session_state.expenses_df, num_rows="dynamic", use_container_width=True)
        st.session_state.expenses_df = edited_df

    with col_ai:
        st.write("### ✨ AI Auto-Allocator")
        st.write("Let Gemini calculate a balanced, zero-based budget for your income instantly.")
        if st.button("Auto-Allocate My Money", use_container_width=True):
            if not api_key:
                st.error("Please provide your API key in the sidebar.")
            else:
                with st.spinner("Calculating..."):
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Income: {income}. Create a realistic monthly budget balancing standard living costs with "Fun Money", "Investments", and "Emergency Fund". Total MUST equal exactly {income}. Return ONLY a raw JSON array.
                    Example: [{{"Category": "Housing", "Amount": 1500.0}}]
                    """
                    try:
                        res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                        raw = re.sub(r'```json|```', '', res.text).strip()
                        s, e = raw.find('['), raw.rfind(']') + 1
                        st.session_state.expenses_df = pd.DataFrame(json.loads(raw[s:e]))
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# ==========================================
# TAB 2: FINCHAT (AI ADVISOR)
# ==========================================
with tab_chat:
    st.write("### 💬 Ask FinAI")
    st.caption("Get extremely concise, instant advice based on your current budget data.")
    
    # Render chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("E.g., Where should I invest my emergency fund?"):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Assistant Response
        if not api_key:
            with st.chat_message("assistant"):
                st.error("Please enter your Gemini API Key in the sidebar to chat.")
        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                client = genai.Client(api_key=api_key)
                
                # Bundle current budget stats to give the AI context
                context = f"""
                User's Live Budget Context:
                Income: {currency_sym}{income} | Goal: {currency_sym}{savings_goal}
                Unallocated: {currency_sym}{unallocated}
                Current Expenses Breakdown:
                {st.session_state.expenses_df.to_string(index=False)}
                
                SYSTEM RULE: You are a direct, no-nonsense financial AI. You MUST answer the user's prompt using the ABSOLUTE MINIMUM number of sentences possible. Do not use fluff. Get straight to the point.
                """
                
                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash", 
                        contents=f"{context}\n\nUser Question: {prompt}"
                    )
                    message_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    message_placeholder.error(f"Failed to connect to AI: {e}")
