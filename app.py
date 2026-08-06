import streamlit as st
import pandas as pd
from google import genai
import time
import json
import re

# --- Page Configuration ---
st.set_page_config(page_title="FinAI | Smart Wealth", page_icon="✨", layout="wide")

# --- Sidebar: Navigation & Info ---
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home (Landing Page)", "💻 Budget Planner"])

st.sidebar.divider()

# About the App & Tech Stack
st.sidebar.subheader("ℹ️ About the App")
st.sidebar.info(
    "FinAI is an intelligent personal finance manager. "
    "It uses artificial intelligence to auto-allocate your income into a zero-based budget "
    "and provides tailored investment strategies."
)

st.sidebar.subheader("🛠️ Tech Stack")
st.sidebar.code("""
- Frontend: Streamlit (Python)
- Data Grid: Pandas
- AI Engine: Google Gemini 2.5
- Logic: Rule-based calculations
""", language="markdown")

st.sidebar.divider()
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password", help="Required for the Budget Planner")


# ==========================================
# PAGE 1: LANDING PAGE
# ==========================================
if page == "🏠 Home (Landing Page)":
    # Advanced Custom CSS for the Landing Page
    st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .hero-container {
            text-align: center;
            padding: 5rem 2rem;
            background: linear-gradient(135deg, #1f2937 0%, #000000 100%);
            border-radius: 20px;
            margin-bottom: 3rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #4F46E5, #06B6D4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .hero-subtitle {
            font-size: 1.5rem;
            color: #9CA3AF;
            margin-bottom: 2.5rem;
        }
        .feature-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            height: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Take Control of Your Wealth</div>
        <div class="hero-subtitle">The first AI-powered personal budget planner that actively optimizes your financial future.</div>
    </div>
    """, unsafe_allow_html=True)

    st.info("👈 Open the sidebar and click **'💻 Budget Planner'** to launch the application.")

    st.divider()
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Why Choose FinAI?</h2>", unsafe_allow_html=True)

    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        st.markdown("""
        <div class="feature-card">
            <h1 style="margin:0;">🧠</h1>
            <h3>AI Auto-Allocation</h3>
            <p style="color:#9CA3AF;">Let Gemini automatically distribute your income into a perfectly balanced, zero-based budget.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_feat2:
        st.markdown("""
        <div class="feature-card">
            <h1 style="margin:0;">📊</h1>
            <h3>Real-Time Tracking</h3>
            <p style="color:#9CA3AF;">Adjust expenses on the fly in the data grid and instantly see the impact on your goals.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_feat3:
        st.markdown("""
        <div class="feature-card">
            <h1 style="margin:0;">📈</h1>
            <h3>Investment Advisory</h3>
            <p style="color:#9CA3AF;">Get smart recommendations on where to invest your savings (Index funds, Stocks, FDs, etc.).</p>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# PAGE 2: BUDGET PLANNER APP
# ==========================================
elif page == "💻 Budget Planner":
    st.title("💸 AI Personal Budget Planner")
    
    # Currency Selector
    col_curr, _ = st.columns([1, 3])
    with col_curr:
        currency_choice = st.selectbox("Select Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "Custom"])
        currency_sym = st.text_input("Custom Symbol", value="¤") if currency_choice == "Custom" else currency_choice.split("(")[1].replace(")", "")

    # --- 1. Income & Goals ---
    st.subheader("1. Income & Goals")
    col1, col2 = st.columns(2)
    with col1:
        income = st.number_input(f"Monthly Income ({currency_sym})", min_value=0.0, value=5000.0, step=100.0)
    with col2:
        savings_goal = st.number_input(f"Monthly Savings Goal ({currency_sym})", min_value=0.0, value=1000.0, step=100.0)

    # Initialize default dataframe in session state
    if "expenses_df" not in st.session_state:
        st.session_state.expenses_df = pd.DataFrame([
            {"Category": "Housing", "Amount": 1500.0},
            {"Category": "Groceries", "Amount": 400.0},
            {"Category": "Utilities", "Amount": 200.0},
            {"Category": "Fun Money", "Amount": 300.0},
            {"Category": "Investments", "Amount": 300.0},
            {"Category": "Emergency Fund", "Amount": 100.0},
        ])

    # --- 2. AI Auto-Allocator ---
    st.subheader("2. ✨ AI Budget Allocator")
    if st.button("Auto-Allocate My Budget"):
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("AI is calculating the optimal allocation..."):
                client = genai.Client(api_key=api_key)
                prompt = f"""
                Based on an income of {income}, create a realistic monthly budget. 
                Include standard categories but MUST include "Fun Money", "Investments", and "Emergency Fund".
                Ensure total equals exactly {income}.
                Respond STRICTLY with a raw JSON array of objects.
                Example: [{{"Category": "Housing", "Amount": 1500.0}}]
                """
                
                try:
                    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    raw_text = re.sub(r'```json|```', '', response.text).strip()
                    start, end = raw_text.find('['), raw_text.rfind(']') + 1
                    st.session_state.expenses_df = pd.DataFrame(json.loads(raw_text[start:end]))
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to auto-allocate. Error: {e}")

    # --- 3. Monthly Expenses (Interactive Table) ---
    st.subheader("3. Monthly Expenses")
    edited_df = st.data_editor(st.session_state.expenses_df, num_rows="dynamic", use_container_width=True)
    st.session_state.expenses_df = edited_df

    # --- 4. Budget Summary ---
    st.subheader("4. Budget Summary")
    total_allocated = edited_df["Amount"].sum()
    unallocated_balance = income - total_allocated

    savings_mask = edited_df["Category"].str.contains("invest|sav|emergency", case=False, na=False)
    actual_savings = edited_df.loc[savings_mask, "Amount"].sum() + (unallocated_balance if unallocated_balance > 0 else 0)
    
    col3, col4, col5 = st.columns(3)
    col3.metric("Total Allocated", f"{currency_sym}{total_allocated:,.2f}")
    col4.metric("Unallocated Balance", f"{currency_sym}{unallocated_balance:,.2f}", "Aim for $0 (Zero-Based)")
    col5.metric("Goal Progress", f"{(actual_savings / savings_goal * 100) if savings_goal > 0 else 0:.1f}%", f"{currency_sym}{actual_savings:,.2f} tracking to savings")

    # --- 5. AI Financial Advisor & Investment Guide ---
    st.subheader("5. 🤖 AI Financial Advisor & Investment Guide")
    if st.button("Generate Advisory Report"):
        if not api_key:
            st.warning("Please enter your Gemini API Key in the sidebar.")
        else:
            with st.spinner("Analyzing your finances and generating investment strategies..."):
                client = genai.Client(api_key=api_key)
                expense_str = edited_df.to_string(index=False)
                
                # UPDATED PROMPT: Now explicitly asks for Investment Advice based on currency
                prompt = f"""
                You are an expert financial advisor. Analyze this monthly budget:
                - Currency: {currency_sym}
                - Monthly Income: {currency_sym}{income}
                - Total Allocated: {currency_sym}{total_allocated}
                - Expenses:
                {expense_str}
                
                Please provide:
                1. **Budget Health Check:** Evaluate the allocation. Is it balanced?
                2. **Optimization Steps:** 3 actionable tips to improve this specific budget.
                3. **Investment Advisory:** Based on their budget size and currency ({currency_sym}), advise EXACTLY where they should put the money labeled 'Investments' or 'Emergency Fund' (e.g., specific asset classes like S&P 500 Index Funds, local Mutual Funds, Fixed Deposits, Gold, etc.).
                
                Format cleanly using markdown bullet points.
                """
                
                for attempt in range(3):
                    try:
                        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                        st.info("📈 Your Personal Financial Report")
                        st.write(response.text)
                        break
                    except Exception as e:
                        if "503" in str(e) and attempt < 2:
                            time.sleep(2 ** (attempt + 1))
                        else:
                            st.error(f"API Error: {e}")
                            break
