import streamlit as st
import requests
import pandas as pd
import time  # Added for Investor Metrics
from axon_sdk import AxonGuard

# --- CONFIGURATION ---
st.set_page_config(page_title="AXON ARCH | Enterprise Gateway", layout="wide", page_icon="🛡️")

# Use your Cloud URL
API_URL = "https://axon-arch-engine.onrender.com" 
API_KEY = "SOVEREIGN_KEY_001"

# Initialize SDK
guard = AxonGuard(API_URL, API_KEY)

# Custom CSS for Enterprise Look
st.markdown("""
    <style>
    .stMetric {
        background-color: #0e1117;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🛡️ AXON ARCH | Command Center")
    st.caption("Sovereign Integrity Layer V1.1 | Status: LIVE")
with c2:
    # Live Latency Indicator for Investors
    if 'last_latency' not in st.session_state:
        st.session_state.last_latency = "0.00 ms"
    st.metric("Engine Latency", st.session_state.last_latency, delta="Target < 10ms")

st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("Network Status")
st.sidebar.success("Engine: ONLINE")
st.sidebar.info("Node: Ohio (Render Cloud)")
st.sidebar.markdown(f"**API Connection:** `{API_URL}`")

# --- MAIN DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["📊 Executive Overview", "🔐 Immutable Ledger", "🕵️ Forensic Audit"])

# --- TAB 1: OVERVIEW ---
with tab1:
    st.subheader("Global Integrity Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records Sealed", "1,240", delta="+12 today")
    col2.metric("Active Verifications", "85,402", delta="+5%")
    col3.metric("Attacks Blocked", "12", delta="-3 this week", delta_color="inverse")
    
    st.write("### 📜 Real-Time Provenance Log")
    # Mock data for the visual
    df = pd.DataFrame({
        'Timestamp': ['2026-02-09 14:02', '2026-02-09 14:15', '2026-02-09 15:10'],
        'Event': ['Bank_Transfer_Seal', 'Medical_Record_Audit', 'Unauthorized_Edit_Blocked'],
        'Status': ['SUCCESS', 'SUCCESS', 'CRITICAL_REJECTION'],
        'Latency': ['4ms', '3ms', '5ms']
    })
    st.table(df)

# --- TAB 2: SEAL (The "Write" Operation) ---
with tab2:
    st.subheader("Commit Data to Room of Truth")
    
    col_input, col_stats = st.columns([2, 1])
    
    with col_input:
        data_to_seal = st.text_area("Enter Critical Data Payload:", 
                               placeholder="Transaction_ID: TXN_9982\nAmount: $10,000.00\nOrigin: Chase_Bank_NY", height=150)
    
    with col_stats:
        st.info("ℹ️ Data is hashed using SHA-256 and anchored in the Axon Merkle Tree.")
    
    if st.button("🔒 Seal to Ledger"):
        if data_to_seal:
            items = data_to_seal.split('\n')
            
            with st.spinner("Cryptographic Sealing in progress..."):
                # --- START TIMER (Christoph's Metric) ---
                start_time = time.perf_counter()
                
                try:
                    res = requests.post(f"{API_URL}/v1/seal", 
                                    json={"data_items": items}, 
                                    headers={"x-api-key": API_KEY})
                    
                    # --- STOP TIMER ---
                    end_time = time.perf_counter()
                    latency = (end_time - start_time) * 1000
                    st.session_state.last_latency = f"{latency:.2f} ms"

                    if res.status_code == 200:
                        st.success(f"Successfully Sealed! Seal ID: {res.json()['seal_id']}")
                        st.metric("Operation Speed", f"{latency:.4f} ms", delta="O(log n) Efficiency")
                    else:
                        st.error(f"Failed to seal data. Server code: {res.status_code}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Connection Error: Is the backend server running?")

# --- TAB 3: AUDIT (The "Read" Operation) ---
with tab3:
    st.subheader("Cryptographic Integrity Audit")
    
    c1, c2 = st.columns(2)
    with c1:
        target_root = st.text_input("Enter Seal ID (Master Root):")
    with c2:
        target_data = st.text_input("Enter Data to Verify:")
    
    if st.button("🔍 Run Forensic Verification"):
        with st.spinner("Calculating Merkle Proof..."):
            
            # --- START TIMER ---
            start_time = time.perf_counter()
            
            # Using your SDK
            is_safe, status = guard.protect(target_data, target_root)
            
            # --- STOP TIMER ---
            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000
            
            if is_safe:
                st.balloons()
                
                st.success(f"VERDICT: {status}")
                st.info(f"Verification completed in {latency:.4f} ms")
            else:
                st.error(f"VERDICT: {status} | ALERT: Intent Invalidation Triggered.")
                st.warning(f"Detection Speed: {latency:.4f} ms")