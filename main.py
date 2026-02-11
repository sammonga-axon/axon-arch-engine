import os
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List
from merkle_engine import MerkleEngine
from database import AxonDB

# --- CONFIGURATION ---
# In Production (Render), set this variable in your Dashboard!
SOVEREIGN_KEY = os.getenv("AXON_SOVEREIGN_KEY", "dev_secret_2026_default").encode()

app = FastAPI(title="AXON ARCH | Sovereign Gateway V2.0 (HMAC)")

# --- MODELS ---
class SealRequest(BaseModel):
    data_items: List[str]

class ProofRequest(BaseModel):
    target_root: str
    target_data: str

class VerifyRequest(BaseModel):
    data: str
    target_root: str
    proof: List[dict]

# --- AUTH ---
def get_current_client(x_api_key: str = Header(...)):
    db = AxonDB()
    client = db.validate_key(x_api_key)
    db.close()
    if not client:
        raise HTTPException(status_code=403, detail="Access Denied")
    return client

# --- ENDPOINTS ---

@app.post("/v1/seal")
async def create_seal(payload: SealRequest, client: dict = Depends(get_current_client)):
    # 1. Initialize Engine with the Sovereign Key
    engine = MerkleEngine(payload.data_items, secret_key=SOVEREIGN_KEY)
    
    db = AxonDB()
    # 2. Log the Seal (Standard Schema)
    log_id = db.log_seal(client['api_key'], engine.root, payload.data_items)
    db.close()
    
    return {
        "status": "COMMITTED",
        "seal_id": engine.root,
        "count": len(payload.data_items),
        "timestamp": "Synced"
    }

@app.post("/v1/get_proof")
async def generate_proof(payload: ProofRequest, client: dict = Depends(get_current_client)):
    db = AxonDB()
    batch = db.get_batch_by_root(payload.target_root)
    db.close()

    if not batch:
        raise HTTPException(status_code=404, detail="Seal ID not found.")

    if payload.target_data not in batch:
        raise HTTPException(status_code=400, detail="Data not found in this Seal.")

    # Rebuild the engine with the SAME key to reproduce the tree
    engine = MerkleEngine(batch, secret_key=SOVEREIGN_KEY)
    
    # Find index and generate proof
    target_hash = engine.hash_data(payload.target_data)
    
    try:
        index = engine.leaves.index(target_hash)
    except ValueError:
        raise HTTPException(status_code=500, detail="CRITICAL: Hash mismatch. Integrity compromised.")
    
    proof = engine.get_proof(index)
    
    return {
        "target_data": payload.target_data,
        "proof": proof
    }

@app.post("/v1/verify")
async def verify_integrity(payload: VerifyRequest, client: dict = Depends(get_current_client)):
    # Stateless Verification
    is_valid = MerkleEngine.verify_proof(
        payload.data, 
        payload.proof, 
        payload.target_root, 
        secret_key=SOVEREIGN_KEY
    )

    if is_valid:
        return {"verified": True, "integrity": "SECURE", "intent": "TRUTH"}
    else:
        # Intent Invalidation Signal
        return {"verified": False, "integrity": "COMPROMISED", "intent": "POISONING"}