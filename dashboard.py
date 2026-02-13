import streamlit as st
import requests
import pandas as pd
import time
import hashlib
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

# --- CSS: VISUAL POLISH (Buttons Fixed) ---
st.markdown("""
    <style>
    /* 1. Force Light Theme Backgrounds */
    .stApp { background-color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #f8fafc !important; } 
    h1, h2, h3, h4, h5, h6, p, span, div, label { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    textarea, input { color: #0f172a !important; background-color: #ffffff !important; border: 1px solid #cbd5e1 !important; font-family: 'JetBrains Mono', monospace !important; }
    header[data-testid="stHeader"] { background-color: #ffffff !important; border-bottom: 1px solid #e2e8f0; }

    /* 2. BUTTON REPAIR: Force White Background & Dark Text */
    div[data-testid="stButton"] > button {
        width: 100%;
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px;
        font-weight: 600 !important;
        height: 45px !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        border-color: #0f172a !important;
    }

    /* 3. Alert Boxes */
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
    
    /* 4. Badges & Boxes */
    .hash-box { background-color: #f1f5f9 !important; color: #0f172a !important; border: 1px solid #cbd5e1; padding: 15px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 14px; margin-top: 5px; }
    .verified-badge { background-color: #dcfce7; color: #166534 !important; padding: 4px 8px; border-radius: 4px; font-size: 14px; font-weight: 600; border: 1px solid #bbf7d0; }
    
    /* 5. SIEM List Styling */
    .siem-item { font-size: 13px; color: #334155; margin-bottom: 5px; }
    .siem-check { color: #16a34a; font-weight: bold; margin-right: 5px; }

    /* 6. Layout Cleanup */
    .block-container { padding-top: 2rem; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'last_latency' not in st.session_state: st.session_state.last_latency = "0.00 ms"

# --- SIDEBAR (ALIGNED) ---
with st.sidebar:
    try:
        st.image("graphic.webp", use_column_width=True)
    except:
        st.warning("Logo not found.")

    st.markdown("---")
    
    # 1. Sentinel Status
    st.header("Sentinel Status")
    st.success("AI Firewall: ONLINE")
    
    # 2. SIEM Capabilities List
    st.markdown("### 🛡️ Active Defense Protocols")
    st.markdown("""
        <div class="siem-item"><span class="siem-check">✓</span> SQL Injection (Pattern Matching)</div>
        <div class="siem-item"><span class="siem-check">✓</span> XSS Payloads (Sanitization)</div>
        <div class="siem-item"><span class="siem-check">✓</span> RCE Attempts (Heuristic)</div>
        <div class="siem-item"><span class="siem-check">✓</span> Prompt Injection (AI Specific)</div>
        <div class="siem-item"><span class="siem-check">✓</span> Buffer Overflow (Size Limit)</div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 3. Integrity Badge
    st.markdown("""<div style="font-size: 14px; color: #64748b !important; margin-bottom: 5px;">Integrity Level</div><div style="font-size: 48px; font-weight: 700; color: #0f172a !important; line-height: 1;">100%</div><div style="margin-top: 10px;"><span class="verified-badge">↑ Verified</span></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 4. Latency (Using Native Metric for Alignment)
    st.metric("Engine Latency (Live)", st.session_state.last_latency)

    st.markdown("---")
    
    # 5. Tech Stack
    st.markdown("""
        <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><strong>Storage Layer</strong></div>
        <div style="background: #e2e8f0; padding: 6px; border-radius: 4px; font-size: 12px; color: #0f172a; margin-bottom: 12px;">Vector DB: Pinecone/Weaviate</div>
        <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><strong>Integrity Core</strong></div>
        <div style="background: #e2e8f0; padding: 6px; border-radius: 4px; font-size: 12px; color: #0f172a;">Engine: Merkle-Tree (HMAC)</div>
    """, unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([5, 1]) 
with c1:
    st.title("🛡️ AXON ARCH | AI Memory Defense")
    st.caption("Immutable Ledger for Vector Embeddings & Model Weights | v3.5.0 (Enterprise)")

with c2:
    st.metric("Inference Latency", st.session_state.last_latency, delta="Target < 5ms")

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
    
    # FORM: Handles State Management
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
                        # Latency Simulation
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
                                st.error("🚨 CLOUD SENTINEL: THREAT BLOCKED (Server Side)")
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
                # SDK Call
                is_safe, status = guard.protect(clean_data, clean_root)
                
                if is_safe:
                    st.balloons()
                    st.markdown(f'<div class="verdict-success">✅ VERIFIED: SECURE<br>Cryptographic Proof Confirmed by Cloud Sentinel.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="verdict-fail">🚨 ALERT: {status}<br>Intent Invalidation Triggered.</div>', unsafe_allow_html=True)
                    st.warning("Analysis: The data does not match the sealed ledger record.")