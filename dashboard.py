import streamlit as st
import requests
import pandas as pd
import time
from axon_sdk import AxonGuard
from merkle_engine import MerkleEngine 
from siem_engine import SovereignSentinel 

# --- CONFIGURATION ---
st.set_page_config(page_title="AXON ARCH | AI Memory Defense", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

API_URL = "https://axon-arch-engine.onrender.com" 
API_KEY = "SOVEREIGN_KEY_001"

guard = AxonGuard(API_URL, API_KEY)
sentinel = SovereignSentinel()

# --- CSS: FINAL VISUAL POLISH ---
st.markdown("""
    <style>
    /* 1. Global Professional White */
    .stApp { background-color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #f8fafc !important; } 
    
    /* 2. Typography */
    h1, h2, h3, h4, h5, h6, p, span, div, label { 
        color: #0f172a !important; 
        font-family: 'Inter', sans-serif;
    }
    
    /* 3. Inputs */
    textarea, input {
        color: #0f172a !important;
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14px !important;
        caret-color: #0f172a !important;
    }
    ::placeholder { color: #94a3b8 !important; opacity: 1 !important; }

    /* CUSTOM HASH BOX (PURE WHITE) */
    .hash-box {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1;
        padding: 15px;
        border-radius: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        font-weight: 500;
        word-wrap: break-word;
        margin-top: 5px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    /* TABLE VISIBILITY */
    div[data-testid="stTable"] {
        color: #0f172a !important;
        background-color: #ffffff !important;
        width: 100%;
    }
    thead tr th {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        font-weight: 600 !important;
    }
    tbody tr td {
        color: #334155 !important;
        background-color: #ffffff !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }

    /* VERDICT COLORS */
    .verdict-success {
        color: #0f172a !important; /* Base Text Dark */
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: #f0fdf4;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #bbf7d0;
        margin-top: 10px;
    }
    .verdict-fail {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        background-color: #fef2f2;
        padding: 15px;
        border-radius: 6px;
        border: 1px solid #fecaca;
        margin-top: 10px;
    }

    /* LATENCY BOX */
    .latency-box {
        background-color: #e2e8f0;
        color: #0f172a;
        padding: 8px 12px;
        border-radius: 5px;
        font-family: 'Source Code Pro', monospace;
        font-size: 14px;
        border: 1px solid #cbd5e1;
    }

    /* VERIFIED BADGE */
    .verified-badge {
        background-color: #dcfce7;
        color: #166534 !important;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 600;
        border: 1px solid #bbf7d0;
    }

    /* BUTTONS */
    div[data-testid="stButton"] > button {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stButton"] > button:hover {
        background-color: #f8fafc !important;
        border-color: #0f172a !important;
    }

    /* Hide Streamlit Elements - BUT KEEP HEADER VISIBLE FOR SIDEBAR ARROW */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* header {visibility: hidden;}  <-- DELETED THIS LINE TO FIX SIDEBAR BUG */
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([5, 1]) 
with c1:
    st.title("🛡️ AXON ARCH | AI Memory Defense")
    st.caption("Immutable Ledger for Vector Embeddings & Model Weights | v2.0.0 (Sentinel)")

# --- INSTANT METRIC UPDATER ---
with c2:
    latency_metric_placeholder = st.empty()
    if 'last_latency' not in st.session_state: 
        st.session_state.last_latency = "0.00 ms"
    latency_metric_placeholder.metric("Inference Latency", st.session_state.last_latency, delta="Target < 5ms")

st.markdown("---")

# --- SIDEBAR (UPDATED WITH MERKLE ENGINE) ---
with st.sidebar:
    st.header("Sentinel Status")
    st.success("AI Firewall: ONLINE")
    
    # --- PROFESSIONAL TECH STACK DISPLAY ---
    st.markdown("""
        <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><strong>Storage Layer</strong></div>
        <div style="background: #e2e8f0; padding: 6px; border-radius: 4px; font-size: 12px; color: #0f172a; margin-bottom: 12px;">
            Vector DB: Pinecone/Weaviate
        </div>

        <div style="font-size: 13px; color: #475569; margin-bottom: 4px;"><strong>Integrity Core</strong></div>
        <div style="background: #e2e8f0; padding: 6px; border-radius: 4px; font-size: 12px; color: #0f172a;">
            Engine: Merkle-Tree (SHA-256)
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
        <div style="font-size: 14px; color: #64748b !important; margin-bottom: 5px;">Integrity Level</div>
        <div style="font-size: 48px; font-weight: 700; color: #0f172a !important; line-height: 1;">100%</div>
        <div style="margin-top: 10px;">
            <span class="verified-badge">↑ Verified</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("**Active Threat Rules**")
    st.markdown("""
        <div style="font-size: 14px; color: #475569; line-height: 1.6;">
        [✓] Prompt Injection<br>
        [✓] RAG Poisoning<br>
        [✓] Model Exfiltration<br>
        [✓] PII Leakage
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.caption("Engine Latency (Live):")
    sidebar_latency_placeholder = st.empty()
    sidebar_latency_placeholder.markdown(f"""
        <div class="latency-box">
            {st.session_state.last_latency}
        </div>
    """, unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Threat Landscape", "🧠 Secure AI Context", "🧬 Forensic DNA"])

# --- TAB 1: OVERVIEW ---
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Vectors Secured", "14.2M")
    col2.metric("Adversarial Blocks", "42")
    with col3:
        st.metric("Model Integrity", "100%", delta="SHA-256 Verified")
    
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
    
    data_to_seal = st.text_area("Input Vector / Context Chunk:", 
                               placeholder="EXAMPLE DATA: 'Vector_Embedding_Array: [0.002, 0.991, -0.221]'", height=150)
    
    if st.button("🛡️ Scan & Seal to Memory"):
        if data_to_seal:
            items = data_to_seal.split('\n')
            
            with st.spinner("Sentinel analyzing adversarial patterns..."):
                time.sleep(0.4) 
                
                # 1. RUN AI THREAT SCAN
                threats_found = []
                clean_items = []
                
                for item in items:
                    analysis = sentinel.scan_payload(item)
                    if analysis["status"] == "DETECTED":
                        threats_found.append(analysis)
                    else:
                        clean_items.append(item)
                
                # 2. DISPLAY THREATS (RED & BOLD)
                if threats_found:
                    st.error(f"🚨 ADVERSARIAL ATTACK DETECTED")
                    for threat in threats_found:
                        st.markdown(f"""
                        <div class="verdict-fail">
                            ⛔ SIEM CLEARANCE: <span style="color: #dc2626; font-weight: 800;">DENIED</span> <br>
                            <span style='font-size:14px; font-weight:normal; color:#b91c1c;'>
                                Threat Pattern: <span style="color: #dc2626; font-weight: 800;">{threat['type']}</span><br>
                                Action: <span style="color: #dc2626; font-weight: 800;">BLOCKED</span>
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 3. SEAL CLEAN ITEMS
                if clean_items:
                    # Calculate Latency
                    core_start = time.perf_counter()
                    for item in clean_items:
                        _ = MerkleEngine.hash_data(item)
                    core_end = time.perf_counter()
                    core_latency = (core_end - core_start) * 1000
                    
                    # UPDATE STATE
                    new_latency_text = f"{core_latency:.4f} ms"
                    st.session_state.last_latency = new_latency_text
                    
                    # FORCE UPDATE METRICS
                    latency_metric_placeholder.metric("Inference Latency", new_latency_text, delta="Target < 5ms")
                    sidebar_latency_placeholder.markdown(f"""
                        <div class="latency-box">
                            {new_latency_text}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Cloud Sync
                    try:
                        res = requests.post(f"{API_URL}/v1/seal", 
                                        json={"data_items": clean_items}, 
                                        headers={"x-api-key": API_KEY})
                        
                        if res.status_code == 200:
                            seal_id = res.json()['seal_id']
                            
                            st.markdown(f"""
                            <div class="verdict-success" style="margin-bottom: 10px;">
                                🛡️ SIEM CLEARANCE: <span style="color: #16a34a; font-weight: 800;">GRANTED</span> <br>
                                <span style='font-size:14px; font-weight:normal; color:#15803d;'>
                                    Deep Packet Inspection Complete: <span style="color: #16a34a; font-weight: 800;">Zero Threats Detected.</span><br>
                                    Payload Sealed to Immutable Ledger.<br>
                                    Core Latency: <span style="color: #16a34a; font-weight: 800;">{new_latency_text}</span>
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("### 🔑 Cryptographic Proof (Copy This):")
                            st.markdown(f"""
                                <div class="hash-box">
                                    {seal_id}
                                </div>
                            """, unsafe_allow_html=True)
                            
                        else:
                            st.error("Cloud Sync Failed.")
                    except Exception as e:
                        st.error(f"Network Error: {e}")

# --- TAB 3: AUDIT ---
with tab3:
    st.subheader("Model Weight & Data Audit")
    
    target_root = st.text_input("Enter Merkle Root Hash:")
    target_data = st.text_input("Enter Vector Data Fragment:")
    
    if st.button("Run Integrity Check"):
        with st.spinner("Verifying Mathematical Proof..."):
            is_safe, status = guard.protect(target_data, target_root)
            
            if is_safe:
                st.balloons()
                st.markdown(f"""
                <div class="verdict-success">
                    ✅ VERIFIED: <span style="color: #16a34a; font-weight: 800;">SECURE</span> <br>
                    <span style='font-size:14px; font-weight:normal; color:#15803d;'>Mathematical Proof Confirmed. Data is Untainted.</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="verdict-fail">
                    🚨 ALERT: <span style="color: #dc2626; font-weight: 800;">{status}</span> <br>
                    <span style='font-size:14px; font-weight:normal; color:#b91c1c;'>Intent Invalidation Triggered. Do not load into Model.</span>
                </div>
                """, unsafe_allow_html=True)