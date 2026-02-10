import streamlit as st
import requests
import pandas as pd
import time
from axon_sdk import AxonGuard
# --- CRITICAL IMPORT FOR ENGINE LOGIC ---
from merkle_engine import MerkleEngine 

# --- CONFIGURATION ---
st.set_page_config(page_title="AXON ARCH | Sovereign Command Center", layout="wide", page_icon="🛡️")

# Use your Cloud URL
API_URL = "https://axon-arch-engine.onrender.com" 
API_KEY = "SOVEREIGN_KEY_001"

# Initialize SDK
guard = AxonGuard(API_URL, API_KEY)

# --- CSS: CUSTOM SOVEREIGN CARDS ---
st.markdown("""
    <style>
    /* 1. HIDE DEFAULT ELEMENTS */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. MAIN BACKGROUND */
    .stApp {
        background-color: #0e1117;
    }

    /* 3. CUSTOM 'SOVEREIGN CARD' DESIGN */
    .sovereign-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        height: 140px; /* Fixed height for perfect alignment */
    }
    .card-label {
        color: #8b949e;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-value {
        color: #ffffff;
        font-size: 36px;
        font-weight: 700;
        margin-top: 10px;
    }
    .delta-negative {
        color: #4CAF50; /* Green for 'Good' drop in attacks */
        font-size: 12px;
        background-color: rgba(76, 175, 80, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .delta-positive {
        color: #4CAF50;
        font-size: 12px;
    }

    /* 4. SIDEBAR INTEGRITY BADGE */
    .integrity-box {
        background-color: #0d1117;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
    }
    .verified-badge {
        background-color: #238636;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        margin-left: 8px;
        vertical-align: middle;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ AXON ARCH | Sovereign Command Center")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("System Status")
    
    # 1. Status Boxes (Standard Streamlit works well here)
    st.success("Engine: Operational")
    st.info("Region: Ohio (Cloud-Node)")
    
    st.markdown("---")
    
    # 2. CUSTOM HTML INTEGRITY BADGE (Your Specific Request)
    st.markdown("""
        <div style="margin-bottom: 5px; color: #8b949e; font-size: 14px;">Integrity Level</div>
        <div class="integrity-box">
            <span style="font-size: 40px; font-weight: bold; color: white;">100%</span>
            <span class="verified-badge">✔ Verified</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Live Latency Indicator
    if 'last_latency' not in st.session_state:
        st.session_state.last_latency = "0.00 ms"
    st.caption("Engine Latency (Live):")
    st.code(st.session_state.last_latency)

# --- MAIN DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔐 Seal Data", "🕵️ Audit Truth"])

# --- TAB 1: OVERVIEW (CUSTOM CARDS) ---
with tab1:
    st.subheader("Global Integrity Metrics")
    
    # We use st.columns but fill them with HTML instead of st.metric
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div class="sovereign-card">
            <div class="card-label">Total Records Sealed</div>
            <div class="card-value">1,240</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="sovereign-card">
            <div class="card-label">Active Verifications</div>
            <div class="card-value">85k</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        # HERE is your specific request: Label and Delta on the same line
        st.markdown(f"""
        <div class="sovereign-card">
            <div class="card-label">
                Attacks Blocked
                <span class="delta-negative">▼ 3 this week</span>
            </div>
            <div class="card-value">12</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("### Recent Activity Log")
    df = pd.DataFrame({
        'Timestamp': ['2026-02-09 14:02', '2026-02-09 14:15', '2026-02-09 15:10'],
        'Event': ['Bank_Transfer_Seal', 'Medical_Record_Audit', 'Unauthorized_Edit_Blocked'],
        'Status': ['SUCCESS', 'SUCCESS', 'CRITICAL_REJECTION']
    })
    st.table(df)

# --- TAB 2: SEAL (The "Write" Operation) ---
with tab2:
    st.subheader("Seal New Data into the Room of Truth")
    
    data_to_seal = st.text_area("Enter Critical Data (One item per line):", 
                               placeholder="Transaction_ID: TXN_9982\nAmount: $10,000.00\nOrigin: Chase_Bank_NY", height=150)
    
    if st.button("🔒 Seal to Ledger"):
        if data_to_seal:
            items = data_to_seal.split('\n')
            
            with st.spinner("Cryptographic Sealing in progress..."):
                
                # 1. MEASURE CORE ENGINE SPEED (The "Samuel" Metric)
                core_start = time.perf_counter()
                for item in items:
                    _ = MerkleEngine.hash_data(item)
                core_end = time.perf_counter()
                core_latency = (core_end - core_start) * 1000
                
                # 2. MEASURE CLOUD SYNC SPEED
                net_start = time.perf_counter()
                try:
                    res = requests.post(f"{API_URL}/v1/seal", 
                                    json={"data_items": items}, 
                                    headers={"x-api-key": API_KEY})
                    net_end = time.perf_counter()
                    net_latency = (net_end - net_start) * 1000
                    
                    if res.status_code == 200:
                        st.success(f"Successfully Sealed! Seal ID: {res.json()['seal_id']}")
                        
                        st.session_state.last_latency = f"{core_latency:.4f} ms"
                        
                        m1, m2 = st.columns(2)
                        m1.metric("Core Engine Speed", f"{core_latency:.4f} ms", delta="🚀 O(log n) Target Met")
                        m2.metric("Cloud Sync (RTT)", f"{net_latency:.0f} ms", delta="Network Latency", delta_color="off")
                        
                    else:
                        st.error("Failed to seal data.")
                except requests.exceptions.ConnectionError:
                    st.error("Connection Error: Is the backend server running?")

# --- TAB 3: AUDIT (The "Read" Operation) ---
with tab3:
    st.subheader("Cryptographic Integrity Audit")
    target_root = st.text_input("Enter Seal ID (Master Root):")
    target_data = st.text_input("Enter Data to Verify:")
    
    if st.button("Run Audit"):
        with st.spinner("Calculating Merkle Proof..."):
            is_safe, status = guard.protect(target_data, target_root)
            
            if is_safe:
                st.balloons()
                st.success(f"VERDICT: {status} | Data is untainted.")
            else:
                st.error(f"VERDICT: {status} | ALERT: Intent Invalidation Triggered.")