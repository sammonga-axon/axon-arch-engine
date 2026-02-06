from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
from merkle_engine import MerkleEngine
from database import AxonDB

app = FastAPI(title="AXON ARCH | Provenance Gateway V1.1")

class SealRequest(BaseModel):
    data_items: List[str]

class ProofRequest(BaseModel):
    target_root: str
    target_data: str

class VerifyRequest(BaseModel):
    data: str
    target_root: str
    proof: List[dict] # In V1.1, the proof is mandatory for verification

def get_current_client(x_api_key: str = Header(...)):
    db = AxonDB()
    client = db.validate_key(x_api_key)
    db.close()
    if not client:
        raise HTTPException(status_code=403, detail="Access Denied")
    return client

# --- Endpoint 1: Seal a Batch ---
@app.post("/v1/seal")
async def create_seal(payload: SealRequest, client: dict = Depends(get_current_client)):
    engine = MerkleEngine(payload.data_items)
    db = AxonDB()
    # We now save the data so we can generate proofs later
    log_id = db.log_seal(client['api_key'], engine.root, payload.data_items)
    db.close()
    return {
        "status": "COMMITTED",
        "seal_id": engine.root,
        "count": len(payload.data_items)
    }

# --- Endpoint 2: Generate a Proof (The New SaaS Feature) ---
@app.post("/v1/get_proof")
async def generate_proof(payload: ProofRequest, client: dict = Depends(get_current_client)):
    """
    Client sends a Root and the Data they want to verify.
    Server looks up the batch, rebuilds the tree, and sends back the Proof path.
    """
    db = AxonDB()
    batch = db.get_batch_by_root(payload.target_root)
    db.close()

    if not batch:
        raise HTTPException(status_code=404, detail="Seal ID not found.")

    if payload.target_data not in batch:
        raise HTTPException(status_code=400, detail="Data not found in this Seal.")

    # Rebuild the engine to calculate the path
    engine = MerkleEngine(batch)
    
    # Find the index of the requested data
    target_hash = MerkleEngine.hash_data(payload.target_data)
    index = engine.leaves.index(target_hash)
    
    # Get the mathematical proof
    proof = engine.get_proof(index)
    
    return {
        "target_data": payload.target_data,
        "proof": proof
    }

# --- Endpoint 3: Verify the Proof ---
@app.post("/v1/verify")
async def verify_integrity(payload: VerifyRequest, client: dict = Depends(get_current_client)):
    # The stateless verification logic
    is_valid = MerkleEngine.verify_proof(payload.data, payload.proof, payload.target_root)

    if is_valid:
        return {"verified": True, "integrity": "SECURE", "intent": "TRUTH"}
    else:
        return {"verified": False, "integrity": "COMPROMISED", "intent": "POISONING"}