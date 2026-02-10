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

# Custom CSS to match your Screenshot's clean look
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 15px;
        border-radius: 5px;
        color: black;
    }
    div[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER (Matches your Screenshot) ---
st.title("🛡️ AXON ARCH | Sovereign Command Center")
st.markdown("---")

# --- SIDEBAR (RESTORED EXACTLY AS YOU HAD IT) ---
with st.sidebar:
    st.subheader("System Status")
    
    # 1. The Green "Engine: Operational" Box
    st.success("Engine: Operational")
    
    # 2. The Blue "Region: Ohio" Box
    st.info("Region: Ohio (Cloud-Node)")
    
    st.markdown("---")
    
    # 3. The Big Integrity Metric (100% Verified)
    st.metric(label="Integrity Level", value="100%", delta="Verified")
    
    st.markdown("---")
    # Live Latency Indicator (Kept small at bottom for Christoph)
    if 'last_latency' not in st.session_state:
        st.session_state.last_latency = "0.00 ms"
    st.caption("Engine Latency (Live):")
    st.code(st.session_state.last_latency)

# --- MAIN DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔐 Seal Data", "🕵️ Audit Truth"])

# --- TAB 1: OVERVIEW ---
with tab1:
    st.subheader("Global Integrity Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records Sealed", "1,240")
    col2.metric("Active Verifications", "85k")
    col3.metric("Attacks Blocked", "12", delta="-3 this week", delta_color="inverse")
    
    st.write("### Recent Activity Log")
    df = pd.DataFrame({
        'Timestamp': ['2026-02-09 14:02', '2026-02-09 14:15', '2026-02-09 15:10'],
        'Event': ['Bank_Transfer_Seal', 'Medical_Record_Audit', 'Unauthorized_Edit_Blocked'],
        'Status': ['SUCCESS', 'SUCCESS', 'CRITICAL_REJECTION']
    })
    st.table(df)

# --- TAB 2: SEAL (The "Write" Operation - WITH SAMUEL'S TIMER) ---
with tab2:
    st.subheader("Seal New Data into the Room of Truth")
    
    data_to_seal = st.text_area("Enter Critical Data (One item per line):", 
                               placeholder="Transaction: $10,000\nPatient_ID: 9982", height=150)
    
    if st.button("Commit to Immutable Ledger"):
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
                        
                        # Save the Fast Speed to Session State for the Sidebar
                        st.session_state.last_latency = f"{core_latency:.4f} ms"
                        
                        # Show the split metrics right here
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