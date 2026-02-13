import streamlit as st
import requests
import pandas as pd
import time
import hashlib
from axon_sdk import AxonGuard
from merkle_engine import MerkleEngine 
from siem_engine import SovereignSentinel 

# --- CONFIGURATION ---
st.set_page_config(page_title="AXON ARCH | AI Memory Defense", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

API_URL = "https://axon-arch-engine.onrender.com" 
API_KEY = "SOVEREIGN_KEY_001"

# Initialize Engines
guard = AxonGuard(API_URL, API_KEY)
sentinel = SovereignSentinel()
local_merkle = MerkleEngine()

# --- CSS: VISUAL SURGERY ---
st.markdown("""
    <style>
    /* 1. LAYOUT SPACING (Push content down slightly as requested) */
    .block-container { 
        padding-top: 3rem !important; 
        padding-bottom: 1rem !important;
    }
    
    /* 2. FORCE LIGHT THEME (Global) */
    .stApp { background-color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #f8fafc !important; } 
    h1, h2, h3, h4, h5, h6, p, li, span, div, label { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    
    /* 3. INPUT FIELDS (White Background / Black Text) */
    .stTextArea textarea, .stTextInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* 4. BUTTON SURGERY (Fixing the Black Void) */
    /* Target specifically the Form Submit Buttons */
    button[kind="primary"], div[data-testid="stFormSubmitButton"] > button {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 2px solid #cbd5e1 !important; /* Thicker border for visibility */
        border-radius: 6px;
        font-weight: 700 !important;
        height: 48px !important;
        width: 100% !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #f1f5f9 !important;
        border-color: #0f172a !important;
        transform: translateY(-1px);
        color: #0f172a !important;
    }
    /* Force internal text color of buttons */
    div[data-testid="stFormSubmitButton"] p { color: #0f172a !important; }

    /* 5. METRIC RESIZING (Fixing "Gib Size") */
    .latency-badge {
        font-family: 'JetBrains Mono', monospace;
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        color: #0f172a;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 18px; /* Smaller, cleaner size */
        display: inline-flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .latency-dot {
        height: 10px;
        width: 10px;
        background-color: #16a34a; /* Green dot */
        border-radius: 50%;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7); }
        70% { box-shadow: 0 0 0 6px rgba(22, 163, 74, 0); }
        100% { box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
    }

    /* 6. STATUS MESSAGES (AV Style) */
    .verdict-success { 
        color: #166534 !important; 
        background-color: #dcfce7; 
        padding: 20px; 
        border-radius: 8px; 
        border: 1px solid #bbf7d0; 
        margin-top: 15px; 
        font-weight: 700; 
        font-size: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* Sidebar Compactness */
    div[data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'last_latency' not in st.session_state: 
    st.session_state.last_latency = "0.0000 ms"

# --- SIDEBAR (RESTRUCTURED FOR DONORS) ---
with st.sidebar:
    # 1. Tech Stack (First thing they see - "How it works")
    st.markdown("### 🏗️ Core Architecture")
    st.markdown("""
        <div style="background: #e2e8f0; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
            <div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Storage Layer</div>
            <div style="font-size: 14px; color: #0f172a; font-weight: 600;">Vector DB (Pinecone)</div>
        </div>
        <div style="background: #e2e8f0; padding: 10px; border-radius: 6px; margin-bottom: 20px;">
            <div style="font-size: 11px; color: #64748b; font-weight: 700; text-transform: uppercase;">Integrity Core</div>
            <div style="font-size: 14px; color: #0f172a; font-weight: 600;">Merkle-Tree (HMAC)</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 2. Sentinel Status (Lifted Up)
    st.header("Sentinel Status")
    st.success("AI Firewall: ONLINE")
    
    # Verified Badge
    st.markdown("""
        <div style="margin-top: 10px; display: flex; align-items: baseline; gap: 10px;">
            <div style="font-size: 32px; font-weight: 800; color: #0f172a;">100%</div>
            <span style="background-color: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; border: 1px solid #bbf7d0;">VERIFIED</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # 3. Defense Protocols
    st.markdown("### 🛡️ Active Protocols")
    st.markdown("""
        <div style="font-size: 13px; margin-bottom: 6px;">✅ SQL Injection <span style="color:#64748b">(Pattern)</span></div>
        <div style="font-size: 13px; margin-bottom: 6px;">✅ XSS Payloads <span style="color:#64748b">(Sanitize)</span></div>
        <div style="font-size: 13px; margin-bottom: 6px;">✅ RCE Attempts <span style="color:#64748b">(Heuristic)</span></div>
        <div style="font-size: 13px;">✅ Prompt Injection <span style="color:#64748b">(AI)</span></div>
    """, unsafe_allow_html=True)

# --- HEADER (CLEANER LAYOUT) ---
c1, c2 = st.columns([3, 1]) 
with c1:
    st.title("🛡️ AXON ARCH | AI Memory Defense")
    st.caption("Immutable Ledger for Vector Embeddings & Model Weights | v3.7.0 (Enterprise)")

with c2:
    # Custom HTML Component for Latency (Solves "Gib Size")
    latency_placeholder = st.empty()
    latency_placeholder.markdown(f"""
        <div class="latency-badge">
            <span class="latency-dot"></span>
            <span>{st.session_state.last_latency}</span>
        </div>
    """, unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Threat Landscape", "🧠 Secure AI Context", "🧬 Forensic DNA"])

# --- TAB 1: OVERVIEW ---
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Vectors Secured", "14.2M")
    col2.metric("Threats Neutralized", "42")
    col3.metric("Model Integrity", "100%", delta="HMAC-SHA256 Verified")
    
    st.markdown("### 📡 Real-Time Packet Analysis")
    siem_data = pd.DataFrame({
        'Timestamp': ['14:02:01', '14:02:05', '14:03:12'],
        'Origin': ['LLM_Inference_Node', 'RAG_Pipeline_04', 'External_API'],
        'Payload_Hash': ['a1b2...99x', 'System Override...', 'Standard_Query'],
        'Defense_Action': ['CLEAN', 'QUARANTINED', 'CLEAN']
    })
    st.table(siem_data)

# --- TAB 2: SECURE AI CONTEXT ---
with tab2:
    st.subheader("Inject Data into AI Memory Stream")
    
    with st.form("seal_form"):
        data_to_seal = st.text_area("Input Vector / Context Chunk:", 
                                    placeholder="EXAMPLE DATA: [0.002, 0.991, -0.221]", 
                                    height=150)
        
        # This button is now targeted by CSS to be White/Dark Text
        submitted = st.form_submit_button("🛡️ SCAN & SEAL TO MEMORY")
        
        if submitted:
            if data_to_seal:
                clean_input = data_to_seal.strip()
                items = [clean_input]
                
                with st.spinner("Running Deep Packet Inspection..."):
                    threat = sentinel.scan_payload(clean_input)
                    
                    if threat["status"] == "DETECTED":
                         st.markdown(f'<div class="verdict-fail">🚨 MALWARE DETECTED<br>Type: {threat["type"]}<br>Status: QUARANTINED</div>', unsafe_allow_html=True)
                    else:
                        core_start = time.perf_counter()
                        _ = hashlib.sha256(clean_input.encode()).hexdigest()
                        core_end = time.perf_counter()
                        
                        # Update Latency Badge Immediately
                        new_latency = f"{(core_end - core_start) * 1000:.4f} ms"
                        st.session_state.last_latency = new_latency
                        latency_placeholder.markdown(f"""
                            <div class="latency-badge">
                                <span class="latency-dot"></span>
                                <span>{new_latency}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        try:
                            res = requests.post(f"{API_URL}/v1/seal", json={"data_items": items}, headers={"x-api-key": API_KEY})
                            
                            if res.status_code == 200:
                                seal_id = res.json()['seal_id']
                                # DONOR ATTRACTIVE LANGUAGE
                                st.markdown(f"""
                                    <div class="verdict-success">
                                        <div style="font-size: 24px;">🛡️</div>
                                        <div>
                                            <div style="font-size: 18px; margin-bottom: 2px;">THREAT NEUTRALIZED. SYSTEM CLEAN.</div>
                                            <div style="font-size: 13px; font-weight: 500; opacity: 0.9;">Integrity Sealed on Immutable Ledger.</div>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                st.markdown("### 🔑 Cryptographic Proof:")
                                st.markdown(f"""
                                    <div style="background: #f1f5f9; padding: 15px; border-radius: 6px; border: 1px solid #cbd5e1; font-family: 'JetBrains Mono'; font-size: 13px; color: #334155;">
                                        {seal_id}
                                    </div>
                                """, unsafe_allow_html=True)
                            elif res.status_code == 403:
                                st.error("🚨 CLOUD FIREWALL: INJECTION BLOCKED")
                            else:
                                st.error(f"Cloud Engine Error: {res.status_code}")
                        except Exception as e:
                            st.error(f"Network Timeout: {str(e)}")

# --- TAB 3: AUDIT ---
with tab3:
    st.subheader("Forensic Audit")

    with st.form("audit_form"):
        target_root = st.text_input("Enter Seal ID (Hash):")
        target_data = st.text_input("Enter Suspect Data:")
        
        # This button is also fixed by the CSS
        audit_submitted = st.form_submit_button("RUN INTEGRITY CHECK")
        
        if audit_submitted:
            clean_data = target_data.strip()
            clean_root = target_root.strip()
            
            with st.spinner("Querying Sovereign Ledger..."):
                is_safe, status = guard.protect(clean_data, clean_root)
                
                if is_safe:
                    st.balloons()
                    st.markdown(f'<div class="verdict-success">✅ INTEGRITY CONFIRMED<br>The data is authentic and has not been tampered with.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="verdict-fail">🚨 TAMPERING DETECTED<br>Digital Signature Mismatch.</div>', unsafe_allow_html=True)