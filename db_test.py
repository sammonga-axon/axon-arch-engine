import requests
import json
import time
import random

# --- CONFIGURATION ---
# We use the exact credentials from your dashboard
API_URL = "https://axon-arch-engine.onrender.com"
API_KEY = "SOVEREIGN_KEY_001"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

def print_status(stage, status, message):
    icon = "✅" if status == "PASS" else "❌"
    print(f"{icon} [{stage}] {status}: {message}")

def run_diagnostics():
    print(f"📡 CONNECTING TO: {API_URL}")
    print("-------------------------------------------------")

    # 1. GENERATE TEST VECTOR
    # We create a unique, random vector to ensure we aren't reading cached data
    test_vector = f"TEST_VECTOR_{random.randint(1000, 9999)}_{time.time()}"
    payload = {"data_items": [test_vector]}
    
    print(f"🧬 GENERATED PAYLOAD: {test_vector}")

    # 2. TEST: WRITE (SEALING)
    # This verifies the API can talk to the Vector DB and return a Hash
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/v1/seal", json=payload, headers=HEADERS)
        latency = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            seal_id = data.get('seal_id')
            print_status("WRITE", "PASS", f"Latency: {latency:.2f}ms")
            print(f"   🔑 SEAL ID: {seal_id}")
            return seal_id, test_vector
        else:
            print_status("WRITE", "FAIL", f"Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
            
    except Exception as e:
        print_status("WRITE", "CRITICAL FAIL", f"Connection Error: {str(e)}")
        return None, None

if __name__ == "__main__":
    seal_id, original_data = run_diagnostics()
    
    if seal_id:
        print("\n-------------------------------------------------")
        print("🕵️ MANUAL VERIFICATION REQUIRED")
        print("1. Copy the SEAL ID above.")
        print(f"2. Copy the DATA: {original_data}")
        print("3. Go to your Dashboard -> 'Forensic DNA' Tab.")
        print("4. Paste them in. If it says 'VERIFIED', your Database is healthy.")