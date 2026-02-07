import streamlit as st
import requests
import pandas as pd
from axon_sdk import AxonGuard

# --- CONFIGURATION ---
st.set_page_config(page_title="AXON ARCH | Command Center", layout="wide")
API_URL = "https://axon-arch-engine.onrender.com" # Your Live URL
API_KEY = "SOVEREIGN_KEY_001"

# Initialize our SDK
guard = AxonGuard(API_URL, API_KEY)

# --- HEADER ---
st.title("🛡️ AXON ARCH | Sovereign Command Center")
st.markdown("---")

# --- SIDEBAR (Stats) ---
st.sidebar.header("System Status")
st.sidebar.success("Engine: Operational")
st.sidebar.info("Region: Ohio (Cloud-Node)")
st.sidebar.metric(label="Integrity Level", value="100%", delta="Verified")

# --- MAIN DASHBOARD ---
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔐 Seal Data", "🕵️ Audit Truth"])

with tab1:
    st.subheader("Global Integrity Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records Sealed", "1,240")
    col2.metric("Active Verifications", "85k")
    col3.metric("Attacks Blocked", "12", delta="-3 this week", delta_color="inverse")
    
    st.write("### Recent Activity Log")
    # Mock data for the visual
    df = pd.DataFrame({
        'Timestamp': ['2026-02-07 14:02', '2026-02-07 14:15', '2026-02-07 15:10'],
        'Event': ['Bank_Transfer_Seal', 'Medical_Record_Audit', 'Unauthorized_Edit_Blocked'],
        'Status': ['SUCCESS', 'SUCCESS', 'CRITICAL_REJECTION']
    })
    st.table(df)

with tab2:
    st.subheader("Seal New Data into the Room of Truth")
    data_to_seal = st.text_area("Enter Critical Data (One item per line):", 
                               placeholder="Transaction: $10,000\nPatient_ID: 9982")
    
    if st.button("Commit to Immutable Ledger"):
        if data_to_seal:
            items = data_to_seal.split('\n')
            # Call your API
            res = requests.post(f"{API_URL}/v1/seal", 
                                json={"data_items": items}, 
                                headers={"x-api-key": API_KEY})
            if res.status_code == 200:
                st.success(f"Successfully Sealed! Seal ID: {res.json()['seal_id']}")
            else:
                st.error("Failed to seal data.")

with tab3:
    st.subheader("Cryptographic Integrity Audit")
    target_root = st.text_input("Enter Seal ID (Master Root):")
    target_data = st.text_input("Enter Data to Verify:")
    
    if st.button("Run Audit"):
        with st.spinner("Calculating Merkle Proof..."):
            is_safe, status = guard.protect(target_data, target_root)
            
            if is_safe:
                st.balloons()
                st.success(f"VERDICT: {status} | This data is untainted and mathematically proven.")
            else:
                st.error(f"VERDICT: {status} | ALERT: Intent Invalidation Triggered. This data has been manipulated.")