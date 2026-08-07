import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google import genai
import json
import re
import time
from datetime import datetime
import numpy as np

# ==========================================
# 1. PAGE CONFIGURATION & SETUP
# ==========================================
st.set_page_config(
    page_title="FinAI | Smart Wealth OS", 
    page_icon="🟢", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. MASSIVE CUSTOM CSS OVERHAUL
# ==========================================
st.markdown("""
<style>
    /* Global Typography & Deep Dark Theme */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    :root {
        --primary: #1DB954;
        --primary-glow: rgba(29, 185, 84, 0.4);
        --bg-base: #090B0F;
        --bg-panel: rgba(22, 26, 37, 0.7);
        --text-main: #FAFAFA;
        --text-muted: #8B949E;
        --border-color: rgba(255, 255, 255, 0.08);
    }
    
    .stApp { 
        background-color: var(--bg-base); 
        color: var(--text-main); 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: #2A2F3D; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

    /* Headings */
    h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700 !important; letter-spacing: -0.03em; }
    
    /* Streamlit Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #0E1117 !important; 
        border-right: 1px solid var(--border-color);
    }
    
    /* Buttons - Primary & Secondary */
    .stButton>button {
        background: linear-gradient(135deg, #1DB954 0%, #118239 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.1) !important; 
        border-radius: 12px !important; 
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important; 
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 4px 15px var(--primary-glow);
    }
    .stButton>button:hover { 
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px var(--primary-glow);
        border: 1px solid #1DB954 !important;
    }
    
    /* Glassmorphism Metric Cards */
    [data-testid="metric-container"] {
        background: var(--bg-panel);
        border: 1px solid var(--border-color);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease, border-color 0.3s ease;
        animation: fade-in-up 0.6s ease-out forwards;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: rgba(29, 185, 84, 0.5);
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: var(--primary) !important;
        text-shadow: 0 0 20px rgba(29, 185, 84, 0.2);
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        color: var(--text-muted) !important;
        font-weight: 500 !important;
    }
    
    /* Data Editor / Dataframes */
    [data-testid="stDataFrame"] { 
        border-radius: 16px; 
        overflow: hidden;
        border: 1px solid var(--border-color);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Advanced Wealth Globe Animation */
    .globe-container { 
        display: flex; justify-content: center; align-items: center; 
        flex-direction: column; margin: 2rem 0; 
        padding: 2rem; background: var(--bg-panel);
        border-radius: 24px; border: 1px solid var(--border-color);
    }
    .globe {
        width: 220px; height: 220px; border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #24E269, #1DB954, #0A421D, #000000);
        box-shadow: 0 0 40px rgba(29, 185, 84, 0.3), inset -15px -15px 30px rgba(0,0,0,0.6);
        animation: float-pulse 6s ease-in-out infinite; 
        display: flex; justify-content: center; align-items: center; 
        text-align: center; position: relative; cursor: pointer;
    }
    .globe::after {
        content: ''; position: absolute; top: -5%; left: -5%; right: -5%; bottom: -5%;
        border-radius: 50%; border: 2px dashed rgba(29, 185, 84, 0.3);
        animation: spin 20s linear infinite;
    }
    .globe-text { 
        position: absolute; color: #FFFFFF; font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem; font-weight: 800; text-shadow: 0px 4px 15px rgba(0,0,0,0.8); z-index: 2; 
    }
    .globe-label { 
        margin-top: 20px; font-size: 1rem; color: var(--text-muted); 
        font-weight: 700; text-transform: uppercase; letter-spacing: 3px; 
    }

    /* Keyframes */
    @keyframes float-pulse { 
        0% { box-shadow: 0 0 20px rgba(29, 185, 84, 0.2); transform: translateY(0) scale(1); } 
        50% { box-shadow: 0 0 60px rgba(29, 185, 84, 0.6); transform: translateY(-10px) scale(1.02); }
        100% { box-shadow: 0 0 20px rgba(29, 185, 84, 0.2); transform: translateY(0) scale(1); } 
    }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes fade-in-up { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
    
    /* Tabs styling */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 8px; background-color: var(--bg-panel); padding: 8px;
        border-radius: 12px; border: 1px solid var(--border-color);
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px; padding: 10px 24px; color: var(--text-muted);
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background-color: rgba(29, 185, 84, 0.1); color: var(--primary); font-weight: 600;
    }

    /* Chat Elements */
    [data-testid="stChatMessage"] { background: var(--bg-panel); border-radius: 12px; padding: 15px; border: 1px solid var(--border-color); }
    [data-testid="stChatInput"] { background-color: #0E1117 !important; border: 1px solid rgba(255,255,255,0.2) !important; border-radius: 16px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. STATE INITIALIZATION & LOGIC
# ==========================================
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

if "expenses_df" not in st.session_state:
    # Richer default dataset for better initial chart rendering
    st.session_state.expenses_df = pd.DataFrame([
        {"Category": "Housing", "Amount": 0.0},
        {"Category": "Food & Dining", "Amount": 0.0},
        {"Category": "Transportation", "Amount": 0.0},
        {"Category": "Utilities", "Amount": 0.0},
        {"Category": "Entertainment", "Amount": 0.0},
        {"Category": "Investments", "Amount": 0.0}
    ])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 **Welcome to FinAI OS!** Let's build your financial fortress. Tell me your monthly income and detail your expenses. I'll automatically generate your zero-based budget."}
    ]

# Core Financial State
if "income" not in st.session_state: st.session_state.income = 5000.0
if "savings_goal" not in st.session_state: st.session_state.savings_goal = 1500.0

# ==========================================
# 4. SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='color: #1DB954; font-size: 2.5rem; margin-bottom: 0;'>FinAI OS</h1>
            <p style='color: #8B949E; font-size: 0.9rem;'>Smart Wealth Engine v2.0</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔑 Authentication")
    api_key = st.text_input("Gemini API Key", type="password", help="Required to activate the AI Advisor")
    
    st.markdown("### ⚙️ Preferences")
    currency_choice = st.selectbox("Base Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)", "Custom"])
    currency_sym = st.text_input("Custom Symbol", value="¤") if currency_choice == "Custom" else currency_choice.split("(")[1].replace(")", "")
    
    st.divider()
    
    # Financial Inputs in Sidebar for global access
    st.markdown("### 💰 Core Income")
    st.session_state.income = st.number_input(f"Monthly Income ({currency_sym})", min_value=0.0, value=st.session_state.income, step=100.0)
    st.session_state.savings_goal = st.number_input(f"Savings Target ({currency_sym})", min_value=0.0, value=st.session_state.savings_goal, step=100.0)

    st.divider()
    if api_key:
        st.success("🟢 AI Engine Online")
    else:
        st.warning("🔴 AI Engine Offline (Key needed)")

# ==========================================
# 5. CORE CALCULATIONS
# ==========================================
df = st.session_state.expenses_df
total_allocated = df["Amount"].sum()
unallocated_balance = st.session_state.income - total_allocated

# Intelligent Savings Identification
savings_keywords = ["invest", "sav", "emergency", "stock", "crypto", "401k", "ira"]
savings_mask = df["Category"].str.contains('|'.join(savings_keywords), case=False, na=False)
actual_savings = df.loc[savings_mask, "Amount"].sum() + (unallocated_balance if unallocated_balance > 0 else 0)

health_score = min(100, max(0, int((actual_savings / st.session_state.income) * 333))) if st.session_state.income > 0 else 0

# ==========================================
# 6. MAIN APPLICATION LAYOUT (TABS)
# ==========================================
st.markdown("<h2 style='text-align: center; color: #8B949E; font-weight: 300;'>Welcome to your <span style='color: #1DB954; font-weight: 700;'>Command Center</span></h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Dashboard", "📝 Budget Editor", "📈 Wealth Analytics", "🤖 AI Advisor"])

# ------------------------------------------
# TAB 1: EXECUTIVE DASHBOARD
# ------------------------------------------
with tab1:
    col_g1, col_g2, col_g3 = st.columns([1, 1.2, 1])
    
    with col_g1:
        st.metric("Total Income", f"{currency_sym}{st.session_state.income:,.2f}")
        st.metric("Total Allocated", f"{currency_sym}{total_allocated:,.2f}")
        st.metric("Financial Health Score", f"{health_score}/100")
        
    with col_g2:
        st.markdown(f"""
        <div class="globe-container">
            <div class="globe">
                <div class="globe-text">{currency_sym}{actual_savings:,.0f}</div>
            </div>
            <div class="globe-label">Total Monthly Wealth Gen</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Gamified progress bar
        if st.session_state.savings_goal > 0:
            progress = min(actual_savings / st.session_state.savings_goal, 1.0)
            st.markdown(f"**Goal Trajectory:** {progress*100:.1f}%")
            st.progress(progress)
            
    with col_g3:
        st.metric("Unallocated Capital", f"{currency_sym}{unallocated_balance:,.2f}")
        
        if unallocated_balance > 0:
            st.info(f"💡 You have {currency_sym}{unallocated_balance:,.2f} sitting idle. Put it to work.")
            if st.button("🚀 Sweep to Investments", key="dash_sweep"):
                if "Investments" in df["Category"].values:
                    st.session_state.expenses_df.loc[st.session_state.expenses_df["Category"] == "Investments", "Amount"] += unallocated_balance
                else:
                    new_row = pd.DataFrame([{"Category": "Investments", "Amount": unallocated_balance}])
                    st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, new_row], ignore_index=True)
                st.rerun()
        elif unallocated_balance < 0:
            st.error(f"⚠️ Deficit: {currency_sym}{abs(unallocated_balance):,.2f}. Adjust budget immediately.")
        else:
            st.success("🎯 Zero-Based Budget Optimized.")

# ------------------------------------------
# TAB 2: BUDGET EDITOR
# ------------------------------------------
with tab2:
    st.subheader("Interactive Ledger")
    st.caption("Double click cells to edit. Changes reflect instantly across the ecosystem.")
    
    col_t1, col_t2 = st.columns([2, 1])
    
    with col_t1:
        edited_df = st.data_editor(
            st.session_state.expenses_df, 
            num_rows="dynamic", 
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": st.column_config.TextColumn("Expense Category", required=True),
                "Amount": st.column_config.NumberColumn(f"Amount ({currency_sym})", min_value=0.0, format="%.2f")
            }
        )
        st.session_state.expenses_df = edited_df
        
    with col_t2:
        st.markdown("### Ledger Rules")
        st.markdown("""
        * **Zero-Based:** Every dollar must have a specific job. 
        * **Pay Yourself First:** Try to allocate at least 20% to the 'Investments' category.
        * **Dynamic Sync:** Updating this table updates the AI's context window automatically.
        """)
        
        if unallocated_balance != 0:
            st.warning(f"Balance constraint violated. Offset: {currency_sym}{unallocated_balance:,.2f}")

# ------------------------------------------
# TAB 3: WEALTH ANALYTICS (PLOTLY)
# ------------------------------------------
with tab3:
    st.subheader("Deep Data Visualization")
    
    if total_allocated > 0:
        c1, c2 = st.columns(2)
        
        with c1:
            # High-end Donut Chart
            fig_donut = px.pie(
                df[df["Amount"] > 0], 
                names="Category", 
                values="Amount", 
                hole=0.6,
                color_discrete_sequence=px.colors.sequential.Greens_r
            )
            fig_donut.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FAFAFA'),
                title="Capital Allocation Breakdown",
                title_font=dict(size=20),
                margin=dict(t=50, b=20, l=20, r=20),
                showlegend=True
            )
            fig_donut.add_annotation(text=f"{currency_sym}{total_allocated:,.0f}", x=0.5, y=0.5, font_size=25, showarrow=False)
            st.plotly_chart(fig_donut, use_container_width=True)
            
        with c2:
            # Cash Flow Waterfall/Bar
            categories = ['Income', 'Expenses', 'Savings', 'Unallocated']
            values = [st.session_state.income, -total_allocated + df.loc[savings_mask, "Amount"].sum(), actual_savings, unallocated_balance]
            colors = ['#1DB954', '#E91E63', '#2196F3', '#FFC107']
            
            fig_bar = go.Figure(data=[
                go.Bar(x=categories, y=values, marker_color=colors, text=[f"{currency_sym}{abs(v):,.0f}" for v in values], textposition='auto')
            ])
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FAFAFA'),
                title="Monthly Cash Flow Dynamics",
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                margin=dict(t=50, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # Projection Line Chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("10-Year Wealth Projection (Assuming 7% Annual Return)")
        
        months = np.arange(1, 121)
        monthly_investment = actual_savings if actual_savings > 0 else 0
        rate = 0.07 / 12
        # Future value of a series formula
        future_values = [monthly_investment * (((1 + rate)**m - 1) / rate) for m in months]
        
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Scatter(
            x=months, y=future_values, 
            mode='lines', 
            line=dict(color='#1DB954', width=3),
            fill='tozeroy', 
            fillcolor='rgba(29, 185, 84, 0.2)'
        ))
        fig_proj.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FAFAFA'),
            xaxis_title="Months", yaxis_title=f"Portfolio Value ({currency_sym})",
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            margin=dict(t=20, b=40, l=40, r=20)
        )
        st.plotly_chart(fig_proj, use_container_width=True)

    else:
        st.info("No expense data available to visualize yet. Add data in the Budget Editor or ask the AI Advisor to build one.")

# ------------------------------------------
# TAB 4: AI ADVISOR
# ------------------------------------------
with tab4:
    st.subheader("Neural Financial Advisor")
    st.caption("Ask complex questions, parse messy text into budgets, or get investment strategies.")
    
    # Render chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input Trigger
    if prompt := st.chat_input("E.g., 'I make 6k. Rent is 2k, car 500, groceries 600. Build my budget.'"):
        if not api_key:
            st.error("⚠️ API Key required. Please enter it in the sidebar.")
        else:
            # Append user msg
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # API Call
            client = genai.Client(api_key=api_key)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing neural models..."):
                    try:
                        expense_str = df.to_string(index=False)
                        
                        sys_prompt = f"""
                        You are FinAI, an elite, highly intelligent financial advisor.
                        User's Stated Income: {currency_sym}{st.session_state.income}
                        Current Unallocated: {currency_sym}{unallocated_balance}
                        Current Budget Table:
                        {expense_str}
                        
                        If the user is providing a list of expenses to start a budget, you MUST extract it as a JSON array.
                        Format EXACTLY as: [{{"Category": "Rent", "Amount": 1000}}]
                        If returning JSON, type exactly '===ADVICE===' immediately after the JSON block, followed by your textual advice.
                        
                        If the user is just asking a question, ignore the JSON and just answer intelligently, formatting your text with markdown (bolding, lists). Keep advice actionable and strictly related to finance.
                        """
                        
                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite", 
                            contents=f"{sys_prompt}\n\nUser Input: {prompt}"
                        )
                        
                        raw_text = response.text
                        
                        # Check if AI attempted to generate a budget JSON
                        if "===ADVICE===" in raw_text:
                            json_part, advice_part = raw_text.split("===ADVICE===")
                            
                            # Regex to safely find JSON array
                            match = re.search(r'\[.*\]', json_part, re.DOTALL)
                            if match:
                                new_budget_df = pd.DataFrame(json.loads(match.group(0)))
                                st.session_state.expenses_df = new_budget_df
                                st.session_state.setup_complete = True
                                
                                st.markdown(advice_part.strip())
                                st.session_state.chat_history.append({"role": "assistant", "content": advice_part.strip()})
                                
                                st.toast("New budget synchronized to OS!", icon="✅")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                msg = "I analyzed your input but failed to build the table. Please try formatting as: Rent 1000, Food 500."
                                st.markdown(msg)
                                st.session_state.chat_history.append({"role": "assistant", "content": msg})
                        else:
                            # Standard conversational response
                            st.markdown(raw_text)
                            st.session_state.chat_history.append({"role": "assistant", "content": raw_text})

                    except Exception as e:
                        st.error(f"System Error: {e}")
