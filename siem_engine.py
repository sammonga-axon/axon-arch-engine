import re
from datetime import datetime

class SovereignSentinel:
    def __init__(self):
        # SERIES A THREAT SIGNATURES (AI MEMORY DEFENSE)
        self.threat_signatures = [
            # 1. Prompt Injection (Trying to break the AI's instructions)
            {"pattern": r"(ignore previous instructions|system override|mode: developer)", "severity": "CRITICAL", "type": "Prompt Injection / Jailbreak"},
            
            # 2. RAG Poisoning (Injecting false facts into the Vector DB)
            {"pattern": r"(<hidden_context>|invisible_text|weight: 9999)", "severity": "HIGH", "type": "RAG Data Poisoning"},
            
            # 3. Model Extraction (Trying to steal the weights)
            {"pattern": r"(GET /v1/weights|dump_model|torch\.save)", "severity": "CRITICAL", "type": "Model Weight Exfiltration"},
            
            # 4. PII Leakage (AI accidentally remembering secrets)
            {"pattern": r"(AKIA[0-9A-Z]{16}|BEGIN PRIVATE KEY)", "severity": "HIGH", "type": "Credential Leakage in Memory"},
            
            # 5. SQL/Vector Injection
            {"pattern": r"(DROP TABLE|DELETE FROM vectors)", "severity": "MEDIUM", "type": "Vector DB Destruction"}
        ]

    def scan_payload(self, data: str):
        """
        Scans AI Context Windows & Vector Inputs for Adversarial Attacks.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        for sig in self.threat_signatures:
            if re.search(sig["pattern"], data, re.IGNORECASE):
                return {
                    "timestamp": timestamp,
                    "status": "DETECTED",
                    "severity": sig["severity"],
                    "type": sig["type"],
                    "payload_fragment": data[:40] + "..." # Show snippet
                }
        
        return {"timestamp": timestamp, "status": "CLEAN", "severity": "NONE", "type": "Verified Tensor Data"}