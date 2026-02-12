from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import os
import uvicorn

# IMPORT YOUR MODULES
from database import AxonDB
from merkle_engine import MerkleEngine  # Uses your HMAC Class
from siem_engine import SovereignSentinel

# --- INIT ---
app = FastAPI(title="AXON ARCH ENGINE", version="2.0.0")
db = AxonDB()
# We do not instantiate MerkleEngine globaly anymore because 
# your class takes data in __init__
sentinel = SovereignSentinel()

# --- MODELS ---
class SealRequest(BaseModel):
    data_items: List[str]

class ValidateRequest(BaseModel):
    merkle_root: str
    data_fragment: str

# --- STARTUP EVENT ---
@app.on_event("startup")
async def startup_event():
    print("AXON ARCH | SYSTEM BOOT: Initializing Ledger...")
    db.init_db()

# --- ENDPOINTS ---
@app.get("/")
def health_check():
    return {"status": "AXON_ARCH_ONLINE", "security": "HMAC_SHA256"}

@app.post("/v1/seal")
def seal_data(payload: SealRequest, x_api_key: Optional[str] = Header(None)):
    """
    1. Scan (SIEM)
    2. Hash (HMAC Merkle)
    3. Save (DB)
    """
    # 1. Security Check
    if x_api_key != "SOVEREIGN_KEY_001": 
        raise HTTPException(status_code=401, detail="UNAUTHORIZED_ACCESS")

    # 2. Sentinel Scan
    for item in payload.data_items:
        scan = sentinel.scan_payload(item)
        if scan["status"] == "DETECTED":
            raise HTTPException(status_code=403, detail=f"THREAT_DETECTED: {scan['type']}")

    # 3. Merkle Hashing (USING YOUR CLASS)
    # We initialize the engine with data, it automatically looks for the ENV Key
    try:
        engine = MerkleEngine(data_blocks=payload.data_items)
        root_hash = engine.root
    except Exception as e:
        print(f"MERKLE ERROR: {e}")
        raise HTTPException(status_code=500, detail="HASH_CALCULATION_FAILED")

    # 4. Persistence
    try:
        db.log_seal(x_api_key, root_hash, payload.data_items)
        return {
            "status": "SEALED",
            "seal_id": root_hash,
            "integrity": "HMAC-SHA256"
        }
    except Exception as e:
        print(f"DB ERROR: {e}")
        raise HTTPException(status_code=500, detail="LEDGER_WRITE_FAILED")

@app.post("/v1/validate")
def validate_integrity(payload: ValidateRequest, x_api_key: Optional[str] = Header(None)):
    """
    THE AUDIT LOGIC:
    1. Check DB for Provenance (Did we seal this?)
    2. Check HMAC for Integrity (Does the math match?)
    """
    print(f"AUDIT REQUEST: Checking Root {payload.merkle_root}")

    # STEP 1: PROVENANCE CHECK (Database)
    record = db.verify_integrity(payload.merkle_root)
    
    if not record:
        return {
            "verified": False,
            "status": "PROVENANCE_MISSING",
            "detail": "Root Hash not found in Immutable Ledger."
        }

    # STEP 2: MATHEMATICAL CHECK (HMAC)
    # We use your static verify_proof method.
    # For a simple 'Data vs Root' check (Single Item), the proof list is empty [].
    # Your class will automatically pull the AXON_SOVEREIGN_KEY from Env to verify.
    
    is_valid_math = MerkleEngine.verify_proof(
        data=payload.data_fragment,
        proof=[], # Empty proof for single-item verification
        target_root=payload.merkle_root
    )

    if is_valid_math:
        return {
            "verified": True,
            "status": "VERIFIED_SECURE",
            "timestamp": str(record['timestamp'])
        }
    else:
        return {
            "verified": False,
            "status": "INTEGRITY_FAILURE",
            "detail": "Math does not match. Data may be altered or Key Mismatch."
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)