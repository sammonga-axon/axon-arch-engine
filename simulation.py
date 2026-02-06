import requests
import json

API_URL = "http://127.0.0.1:8000"
API_KEY = "SOVEREIGN_KEY_001"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

# --- SCENARIO 1: The Bank Seals a BATCH of Data ---
print_separator("STEP 1: SEALING A BATCH")
batch_data = [
    "Tx_101: Alice -> Bob $100",
    "Tx_102: Bob -> Charlie $50",
    "Tx_103: NGO -> Hospital $50,000", # <-- We will verify this one
    "Tx_104: Salary -> Employee $2,000",
    "Tx_105: Admin -> Server Config_Update"
]

payload = {"data_items": batch_data}
response = requests.post(f"{API_URL}/v1/seal", json=payload, headers=HEADERS)
data = response.json()
SEAL_ID = data['seal_id']

print(f"✅ BATCH SEALED.")
print(f"🔐 Master Root: {SEAL_ID}")

# --- SCENARIO 2: Fetching the Proof for ONE Item ---
print_separator("STEP 2: REQUESTING PROOF FOR Tx_103")
target_item = "Tx_103: NGO -> Hospital $50,000"

proof_payload = {
    "target_root": SEAL_ID,
    "target_data": target_item
}
response = requests.post(f"{API_URL}/v1/get_proof", json=proof_payload, headers=HEADERS)
proof_data = response.json()

if 'proof' in proof_data:
    MY_PROOF = proof_data['proof']
    print(f"✅ PROOF RECEIVED.")
    print(f"📜 Proof Path Length: {len(MY_PROOF)} hops")
else:
    print(f"❌ Failed to get proof: {response.text}")
    exit()

# --- SCENARIO 3: Verifying (The Client-Side Check) ---
print_separator("STEP 3: VERIFYING Tx_103")

verify_payload = {
    "data": target_item,
    "target_root": SEAL_ID,
    "proof": MY_PROOF
}
response = requests.post(f"{API_URL}/v1/verify", json=verify_payload, headers=HEADERS)
print(f"Item: '{target_item}'")
print(f"Verdict: {response.json()['intent']}")

# --- SCENARIO 4: The Poisoning Attack ---
print_separator("STEP 4: DETECTING POISON")
# Attacker changes $50,000 to $500,000
poisoned_item = "Tx_103: NGO -> Hospital $500,000"

verify_payload = {
    "data": poisoned_item,
    "target_root": SEAL_ID,
    "proof": MY_PROOF
}
response = requests.post(f"{API_URL}/v1/verify", json=verify_payload, headers=HEADERS)
print(f"Item: '{poisoned_item}'")
print(f"Verdict: {response.json()['intent']}")