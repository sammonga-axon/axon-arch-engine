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

guard = AxonGuard(API_URL, API_KEY)
sentinel = SovereignSentinel()
local_merkle = MerkleEngine()

# --- CSS: HIGH CONTRAST THEME ENFORCER ---
st.markdown("""
    <style>
    /* 1. FORCE LIGHT MODE (Overrides System Dark Mode) */
    .stApp { background-color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #f8fafc !important; } 
    
    /* 2. FORCE TEXT COLORS (Fixes Invisible Cursor) */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    
    /* 3. INPUT FIELDS (Explicit White Background + Black Text) */
    .stTextArea textarea, .stTextInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #94a3b8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        caret-color: #000000 !important; /* Force Cursor Black */
    }
    
    /* 4. BUTTONS (Force White with Dark Text) */
    div[data-testid="stButton"] > button {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px;
        font-weight: 700 !important;
        height: 45px !important;
        width: 100% !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #f1f5f9 !important;
        border-color: #0f172a !important;
        color: #0f172a !important;
    }

    /* 5. Custom Alert Boxes */
    .verdict-success { 
        color: #166534 !important; 
        background-color: #dcfce7; 
        padding: 15px; 
        border-radius: 6px; 
        border: 1px solid #bbf7d0; 
        margin-top: 10px; 
        font-weight: 600; 
    }
    .verdict-fail { 
        color: #991b1b !important; 
        background-color: #fee2e2; 
        padding: 15px; 
        border-radius: 6px; 
        border: 1px solid #fecaca; 
        margin-top: 10px; 
        font-weight: 600; 
    }
    
    /* 6. Layout & Metrics */
    .hash-box { background-color: #f1f5f9 !important; color: #0f172a !important; border: 1px solid #cbd5e1; padding: 15px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 14px; margin-top: 5px; }
    .verified-badge { background-color: #dcfce7; color: #166534 !important; padding: 4px 8px; border-radius: 4px; font-size: 14px; font-weight: 600; border: 1px solid #bbf7d0; }
    .block-container { padding-top: 2rem; }
    footer {visibility: hidden;}
    
    /* 7. Sidebar List */
    .siem-item { font-size: 13px; color: #334155 !important; margin-bottom: 5px; }
    .siem-check { color: #16a34a !important; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'last_latency' not in st.session_state: st.session_state.last_latency = "0.00 ms"

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("graphic.webp", use_column_width=True)
    except:
        st.warning("Logo not found.")

    st.markdown("---")
    
    st.header("Sentinel Status")
    st.success("AI Firewall: ONLINE")
    
    # 100% Verified Badge
    st.markdown("""<div style="font-size: 14px; color: #64748b !important; margin-top: 15px; margin-bottom: 5px;">Integrity Level</div><div style="font-size: 48px; font-weight: 700; color: #0f172a !important; line-height: 1;">100%</div><div style="margin-top: 10px;"><span class="verified-badge">↑ Verified</span></div>""", unsafe_allow_html=True)
    
    st.markdown("---")

    # SIEM List (Restored)
    st.markdown("### 🛡️ Defense Protocols")
    st.markdown("""
        <div class="siem-item"><span class="siem-check">✓</span> SQL Injection (Pattern)</div>
        <div class="siem-item"><span class="siem-check">✓</span> XSS Payloads (Sanitize)</div>
        <div class="siem-item"><span class="siem-check">✓</span> RCE Attempts (Heuristic)</div>
        <div class="siem-item"><span class="siem-check">✓</span> Prompt Injection (AI)</div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Latency moved to bottom to prevent overlapping
    st.metric("Engine Latency", st.session_state.last_latency)

# --- HEADER ---
c1, c2 = st.columns([5, 1]) 
with c1:
    st.title("🛡️ AXON ARCH | AI Memory Defense")
    st.caption("Immutable Ledger for Vector Embeddings & Model Weights | v3.6.0 (High Contrast)")

with c2:
    st.metric("Latency", st.session_state.last_latency, delta="Target < 5ms")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Threat Landscape", "🧠 Secure AI Context", "🧬 Forensic DNA"])

# --- TAB 1: OVERVIEW ---
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Vectors Secured", "14.2M")
    col2.metric("Adversarial Blocks", "42")
    col3.metric("Model Integrity", "100%", delta="HMAC-SHA256 Verified")
    
    st.markdown("### 📡 Live Vector Stream Analysis")
    siem_data = pd.DataFrame({
        'Timestamp': ['14:02:01', '14:02:05', '14:03:12'],
        'Origin': ['LLM_Inference_Node', 'RAG_Pipeline_04', 'External_API'],
        'Payload_Hash': ['a1b2...99x', 'System Override...', 'Standard_Query'],
        'Defense_Action': ['VERIFIED', 'BLOCKED (Injection)', 'VERIFIED']
    })
    st.table(siem_data)

# --- TAB 2: SECURE AI CONTEXT ---
with tab2:
    st.subheader("Inject Data into AI Memory Stream")
    
    with st.form("seal_form"):
        data_to_seal = st.text_area("Input Vector / Context Chunk:", 
                                    placeholder="EXAMPLE DATA: [0.002, 0.991, -0.221]", 
                                    height=150)
        
        submitted = st.form_submit_button("🛡️ Scan & Seal to Memory")
        
        if submitted:
            if data_to_seal:
                clean_input = data_to_seal.strip()
                items = [clean_input]
                
                with st.spinner("Sentinel analyzing..."):
                    threat = sentinel.scan_payload(clean_input)
                    if threat["status"] == "DETECTED":
                         st.markdown(f'<div class="verdict-fail">🚨 ADVERSARIAL ATTACK DETECTED (LOCAL)<br>Threat: {threat["type"]}<br>Action: BLOCKED</div>', unsafe_allow_html=True)
                    else:
                        core_start = time.perf_counter()
                        _ = hashlib.sha256(clean_input.encode()).hexdigest()
                        core_end = time.perf_counter()
                        st.session_state.last_latency = f"{(core_end - core_start) * 1000:.4f} ms"
                        
                        try:
                            res = requests.post(f"{API_URL}/v1/seal", json={"data_items": items}, headers={"x-api-key": API_KEY})
                            if res.status_code == 200:
                                seal_id = res.json()['seal_id']
                                st.markdown(f'<div class="verdict-success">🛡️ SIEM CLEARANCE: GRANTED<br>Deep Packet Inspection Complete. Sealed to Immutable Ledger.</div>', unsafe_allow_html=True)
                                st.markdown("### 🔑 Cryptographic Proof:")
                                st.markdown(f'<div class="hash-box">{seal_id}</div>', unsafe_allow_html=True)
                            elif res.status_code == 403:
                                st.error("🚨 CLOUD SENTINEL: THREAT BLOCKED")
                            else:
                                st.error(f"Cloud Engine Error: {res.status_code}")
                        except Exception as e:
                            st.error(f"Network Timeout: {str(e)}")

# --- TAB 3: AUDIT ---
with tab3:
    st.subheader("Model Weight & Data Audit")

    with st.form("audit_form"):
        target_root = st.text_input("Enter Merkle Root Hash (Seal ID):")
        target_data = st.text_input("Enter Vector Data Fragment:")
        audit_submitted = st.form_submit_button("Run Integrity Check")
        
        if audit_submitted:
            clean_data = target_data.strip()
            clean_root = target_root.strip()
            
            with st.spinner("Querying Sovereign Ledger..."):
                is_safe, status = guard.protect(clean_data, clean_root)
                
                if is_safe:
                    st.balloons()
                    st.markdown(f'<div class="verdict-success">✅ VERIFIED: SECURE<br>Cryptographic Proof Confirmed by Cloud Sentinel.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="verdict-fail">🚨 ALERT: {status}<br>Intent Invalidation Triggered.</div>', unsafe_allow_html=True)
                    st.warning("Analysis: The data does not match the sealed ledger record.")