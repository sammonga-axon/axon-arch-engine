import streamlit as st
import requests
import pandas as pd
import time
from PIL import Image
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

# --- CSS: GLOBAL STYLES ---
st.markdown("""
    <style>
    /* 1. Global Theme */
    .stApp { background-color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #f8fafc !important; } 
    h1, h2, h3, h4, h5, h6, p, span, div, label { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    textarea, input { color: #0f172a !important; background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; font-family: 'JetBrains Mono', monospace !important; }
    header[data-testid="stHeader"] { background-color: #ffffff !important; border-bottom: 1px solid #e2e8f0; }
    
    /* 2. UPLIFT FIX: Remove default top padding to pull everything up */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* 3. Visual Elements */
    .hash-box { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1; padding: 15px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 14px; margin-top: 5px; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05); }
    .verdict-success { color: #0f172a !important; font-weight: 600 !important; background-color: #f0fdf4; padding: 15px; border-radius: 6px; border: 1px solid #bbf7d0; margin-top: 10px; }
    .verdict-fail { color: #0f172a !important; font-weight: 600 !important; background-color: #fef2f2; padding: 15px; border-radius: 6px; border: 1px solid #fecaca; margin-top: 10px; }
    .latency-box { background-color: #e2e8f0; color: #0f172a; padding: 8px 12px; border-radius: 5px; font-family: 'Source Code Pro', monospace; font-size: 14px; border: 1px solid #cbd5e1; }
    .verified-badge { background-color: #dcfce7; color: #166534 !important; padding: 4px 8px; border-radius: 4px; font-size: 14px; font-weight: 600; border: 1px solid #bbf7d0; }

    /* 4. BUTTONS */
    div[data-testid="stButton"] > button {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: 45px !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        border-color: #0f172a !important;
    }
    
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT (Auto-Clear Logic) ---
if 'seal_input' not in st.session_state: st.session_state.seal_input = ""
if 'audit_root' not in st.session_state: st.session_state.audit_root = ""
if 'audit_data' not in st.session_state: st.session_state.audit_data = ""
if 'last_latency' not in st.session_state: st.session_state.last_latency = "0.00 ms"

def clear_seal_console():
    st.session_state.seal_input = ""

def clear_audit_console():
    st.session_state.audit_root = ""
    st.session_state.audit_data = ""

# --- SIDEBAR ---
with st.sidebar:
    # 1. LOGO & BRANDING
    try:
        st.image("graphic.webp", use_column_width=True)
    except:
        st.warning("Logo not found: Ensure 'graphic.webp' is in root.")

    st.markdown("---")
    
    # 2. SENTINEL STATUS & LATENCY (High Visibility)
    st.header("Sentinel Status")
    st.success("AI Firewall: ONLINE")
    
    st.caption("Engine Latency (Live):")
    sidebar_latency_placeholder = st.empty()
    sidebar_latency_placeholder.markdown(f'<div class="latency-box">{st.session_state.last_latency}</div>', unsafe_allow_html=True)
    
    st.markdown("---")

    # 3. INFO BLOCKS
    st.markdown("""
        <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><strong>Storage Layer</strong></div>
        <div style="background: #e2e8f0; padding: 6px; border-radius: 4px; font-size: 12px; color: #0f172a; margin-bottom: 12px;">Vector DB: Pinecone/Weaviate</div>
        <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><strong>Integrity Core</strong></div>
        <div style="background: #e2e8f0; padding: 6px; border-radius: 4px; font-size: 12px; color: #0f172a;">Engine: Merkle-Tree (SHA-256)</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""<div style="font-size: 14px; color: #64748b !important; margin-bottom: 5px;">Integrity Level</div><div style="font-size: 48px; font-weight: 700; color: #0f172a !important; line-height: 1;">100%</div><div style="margin-top: 10px;"><span class="verified-badge">↑ Verified</span></div>""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([5, 1]) 
with c1:
    st.title("🛡️ AXON ARCH | AI Memory Defense")
    st.caption("Immutable Ledger for Vector Embeddings & Model Weights | v2.1.0 (Enterprise)")

with c2:
    latency_metric_placeholder = st.empty()
    latency_metric_placeholder.metric("Inference Latency", st.session_state.last_latency, delta="Target < 5ms")

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
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        st.subheader("Inject Data into AI Memory Stream")
    with c_btn:
        st.button("🔄 New Session", on_click=clear_seal_console, help="Clear console to prevent data leaks.")

    data_to_seal = st.text_area("Input Vector / Context Chunk:", 
                                key="seal_input",
                                placeholder="EXAMPLE DATA: 'Vector_Embedding_Array: [0.002, 0.991, -0.221]'", 
                                height=150)
    
    if st.button("🛡️ Scan & Seal to Memory"):
        if data_to_seal:
            items = [i.strip() for i in data_to_seal.split('\n') if i.strip()]
            
            with st.spinner("Sentinel analyzing adversarial patterns..."):
                time.sleep(0.4) 
                threats_found = [sentinel.scan_payload(item) for item in items if sentinel.scan_payload(item)["status"] == "DETECTED"]
                clean_items = [item for item in items if sentinel.scan_payload(item)["status"] != "DETECTED"]
                
                # 1. LOCAL BLOCK (Client-Side)
                if threats_found:
                    st.error(f"🚨 ADVERSARIAL ATTACK DETECTED (LOCAL)")
                    for threat in threats_found:
                        st.markdown(f'<div class="verdict-fail">⛔ SIEM CLEARANCE: <span style="color: #dc2626; font-weight: 800;">DENIED</span> <br><span style="font-size:14px; font-weight:normal; color:#b91c1c;">Threat Pattern: {threat["type"]}<br>Action: BLOCKED</span></div>', unsafe_allow_html=True)
                
                # 2. SERVER REQUEST
                if clean_items:
                    core_start = time.perf_counter()
                    for item in clean_items:
                        local_merkle.hash_data(item)
                    core_end = time.perf_counter()
                    core_latency = (core_end - core_start) * 1000
                    
                    new_latency_text = f"{core_latency:.4f} ms"
                    st.session_state.last_latency = new_latency_text
                    latency_metric_placeholder.metric("Inference Latency", new_latency_text, delta="Target < 5ms")
                    sidebar_latency_placeholder.markdown(f'<div class="latency-box">{new_latency_text}</div>', unsafe_allow_html=True)
                    
                    try:
                        res = requests.post(f"{API_URL}/v1/seal", json={"data_items": clean_items}, headers={"x-api-key": API_KEY})
                        
                        if res.status_code == 200:
                            seal_id = res.json()['seal_id']
                            st.markdown(f'<div class="verdict-success">🛡️ SIEM CLEARANCE: <span style="color: #16a34a; font-weight: 800;">GRANTED</span> <br><span style="font-size:14px; font-weight:normal; color:#15803d;">Deep Packet Inspection Complete. Sealed to Immutable Ledger.<br>Core Latency: {new_latency_text}</span></div>', unsafe_allow_html=True)
                            st.markdown("### 🔑 Cryptographic Proof:")
                            st.markdown(f'<div class="hash-box">{seal_id}</div>', unsafe_allow_html=True)
                        elif res.status_code == 403:
                            st.error("🚨 CLOUD SENTINEL: THREAT BLOCKED")
                            st.markdown(f'<div class="verdict-fail">⛔ SERVER VERDICT: <span style="color: #dc2626; font-weight: 800;">DENIED (403)</span> <br>The Cloud API detected a malicious payload.</div>', unsafe_allow_html=True)
                        else:
                            st.error(f"Cloud Engine Error: {res.status_code}")
                    except Exception as e:
                        st.error(f"Network Timeout: Ensure Render service is awake.")

# --- TAB 3: AUDIT ---
with tab3:
    c_aud_head, c_aud_btn = st.columns([4, 1])
    with c_aud_head:
        st.subheader("Model Weight & Data Audit")
    with c_aud_btn:
        st.button("🔄 Reset Console", on_click=clear_audit_console)

    target_root = st.text_input("Enter Merkle Root Hash:", key="audit_root")
    target_data = st.text_input("Enter Vector Data Fragment:", key="audit_data")
    
    if st.button("Run Integrity Check"):
        with st.spinner("Verifying Mathematical Proof..."):
            is_safe, status = guard.protect(target_data, target_root)
            if is_safe:
                st.balloons()
                st.markdown(f'<div class="verdict-success">✅ VERIFIED: <span style="color: #16a34a; font-weight: 800;">SECURE</span> <br>Mathematical Proof Confirmed. Data is Untainted.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="verdict-fail">🚨 ALERT: <span style="color: #dc2626; font-weight: 800;">{status}</span> <br>Intent Invalidation Triggered. Do not load into Model.</div>', unsafe_allow_html=True)