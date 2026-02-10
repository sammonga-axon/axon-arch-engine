import streamlit as st
import requests
import pandas as pd
import time
from axon_sdk import AxonGuard
from merkle_engine import MerkleEngine 

# --- CONFIGURATION ---
st.set_page_config(page_title="AXON ARCH | Sovereign Command Center", layout="wide", page_icon="🛡️")

API_URL = "https://axon-arch-engine.onrender.com" 
API_KEY = "SOVEREIGN_KEY_001"

guard = AxonGuard(API_URL, API_KEY)

# --- CSS: PURE CLEAN THEME (FINAL PERFECTED) ---
st.markdown("""
    <style>
    /* 1. Force Light Mode Global Colors */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* 2. Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
    }
    
    /* 3. Text Colors (Global) */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #0e1117 !important;
    }
    
    /* 4. HIDE STREAMLIT BRANDING */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* --- FIX 1: INPUT FIELDS & PLACEHOLDERS --- */
    div[data-baseweb="textarea"], div[data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 4px !important;
    }
    textarea, input {
        color: #0e1117 !important;
        background-color: #ffffff !important;
    }
    /* MAKE PLACEHOLDER TEXT VERY LIGHT GREY */
    ::placeholder {
        color: #e2e8f0 !important; /* Very Light Grey */
        opacity: 1 !important;
    }
    ::-webkit-input-placeholder {
        color: #e2e8f0 !important;
    }

    /* --- FIX 2: LATENCY BOX --- */
    .latency-box {
        background-color: #e6e8eb;
        color: #0e1117;
        padding: 8px 12px;
        border-radius: 5px;
        font-family: 'Source Code Pro', monospace;
        font-size: 14px;
        border: 1px solid #d1d5db;
    }

    /* --- FIX 3: BUTTONS --- */
    div[data-testid="stButton"] > button {
        background-color: #ffffff !important;
        color: #0e1117 !important;
        border: 1px solid #d1d5db !important;
        font-weight: 600 !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #0e1117 !important;
        background-color: #f3f4f6 !important;
    }

    /* --- FIX 4: ALERTS (Red Error / Green Success) --- */
    div[data-testid="stNotification"] {
        border-radius: 6px;
    }
    
    /* ERROR BOX (Red Alert) */
    div[data-testid="stNotification"][aria-label="Error"] {
        background-color: #fee2e2 !important; /* Light Red BG */
        border: 1px solid #ef4444 !important; /* Red Border */
    }
    div[data-testid="stNotification"][aria-label="Error"] div,
    div[data-testid="stNotification"][aria-label="Error"] p,
    div[data-testid="stNotification"][aria-label="Error"] span {
        color: #b91c1c !important; /* DARK RED TEXT */
    }

    /* SUCCESS BOX (Green Hash) */
    div[data-testid="stNotification"][aria-label="Success"] {
        background-color: #dcfce7 !important;
        border: 1px solid #22c55e !important;
    }
    div[data-testid="stNotification"][aria-label="Success"] div,
    div[data-testid="stNotification"][aria-label="Success"] p {
        color: #15803d !important; /* Dark Green Text */
    }
    
    /* 5. Custom Badge Style */
    .verified-badge {
        background-color: #d1fae5;
        color: #065f46 !important;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 600;
    }
    
    /* 6. Custom Metric Layouts (Fixed Normal Weight) */
    .metric-container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    .metric-label {
        font-size: 14px;
        color: #586069 !important;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 36px; 
        font-weight: 500; /* Normal Weight (Not Bold) */
        color: #0e1117 !important;
        line-height: 1.2;
    }
    .delta-badge {
        background-color: #dafbe1;
        color: #1f883d !important;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        vertical-align: middle;
        margin-left: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([5, 1]) 
with c1:
    st.title("🛡️ AXON ARCH | Sovereign Command Center")
with c2:
    if 'last_latency' not in st.session_state:
        st.session_state.last_latency = "0.00 ms"
    st.metric("Engine Latency", st.session_state.last_latency, delta="Target < 10ms")

st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("System Status")
    
    st.success("Engine: Operational")
    st.info("Region: Ohio (Cloud-Node)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Integrity Level
    st.markdown("""
        <div style="font-size: 14px; color: #586069 !important; margin-bottom: 5px;">Integrity Level</div>
        <div style="font-size: 48px; font-weight: 700; color: #0e1117 !important; line-height: 1;">100%</div>
        <div style="margin-top: 10px;">
            <span class="verified-badge">↑ Verified</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # LATENCY DISPLAY
    st.caption("Engine Latency (Live):")
    st.markdown(f"""
        <div class="latency-box">
            {st.session_state.last_latency}
        </div>
    """, unsafe_allow_html=True)

# --- MAIN DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔐 Seal Data", "🕵️ Audit Truth"])

with tab1:
    st.subheader("Global Integrity Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Total Records Sealed", "1,240")
    col2.metric("Active Verifications", "85k")
    
    # Custom "Attacks Blocked" Layout
    with col3:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">
                Attacks Blocked
                <span class="delta-badge">↓ -3 this week</span>
            </div>
            <div class="metric-value">12</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.write("### Recent Activity Log")
    df = pd.DataFrame({
        'Timestamp': ['2026-02-09 14:02', '2026-02-09 14:15', '2026-02-09 15:10'],
        'Event': ['Bank_Transfer_Seal', 'Medical_Record_Audit', 'Unauthorized_Edit_Blocked'],
        'Status': ['SUCCESS', 'SUCCESS', 'CRITICAL_REJECTION']
    })
    st.table(df)

with tab2:
    st.subheader("Seal New Data into the Room of Truth")
    
    # INPUT FIELD (Placeholders are now very light)
    data_to_seal = st.text_area("Enter Critical Data (One item per line):", 
                               placeholder="Transaction_ID: TXN_9982\nAmount: $10,000.00\nOrigin: Chase_Bank_NY", height=150)
    
    if st.button("🔒 Seal to Ledger"):
        if data_to_seal:
            items = data_to_seal.split('\n')
            
            with st.spinner("Cryptographic Sealing in progress..."):
                
                # --- METRIC LOGIC ---
                core_start = time.perf_counter()
                for item in items:
                    _ = MerkleEngine.hash_data(item)
                core_end = time.perf_counter()
                core_latency = (core_end - core_start) * 1000
                
                # --- CLOUD SYNC ---
                net_start = time.perf_counter()
                try:
                    res = requests.post(f"{API_URL}/v1/seal", 
                                    json={"data_items": items}, 
                                    headers={"x-api-key": API_KEY})
                    net_end = time.perf_counter()
                    net_latency = (net_end - net_start) * 1000
                    
                    if res.status_code == 200:
                        # SUCCESS: Shows the Hash!
                        st.success(f"Successfully Sealed! Seal ID: {res.json()['seal_id']}")
                        
                        st.session_state.last_latency = f"{core_latency:.4f} ms"
                        
                        m1, m2 = st.columns(2)
                        m1.metric("Core Engine Speed", f"{core_latency:.4f} ms", delta="🚀 O(log n) Target Met")
                        m2.metric("Cloud Sync (RTT)", f"{net_latency:.0f} ms", delta="Network Latency", delta_color="off")
                        
                        # NO RERUN - Keeps the hash visible!
                        
                    else:
                        st.error("Failed to seal data.")
                except requests.exceptions.ConnectionError:
                    st.error("Connection Error: Is the backend server running?")

with tab3:
    st.subheader("Cryptographic Integrity Audit")
    
    # INPUT FIELDS
    target_root = st.text_input("Enter Seal ID (Master Root):")
    target_data = st.text_input("Enter Data to Verify:")
    
    if st.button("Run Audit"):
        with st.spinner("Calculating Merkle Proof..."):
            is_safe, status = guard.protect(target_data, target_root)
            
            if is_safe:
                st.balloons()
                st.success(f"VERDICT: {status} | Data is untainted.")
            else:
                # Custom Red Alert Message
                st.error(f"VERDICT: {status} | ALERT: Intent Invalidation Triggered.")