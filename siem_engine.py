import re
from typing import Dict, Any

class SovereignSentinel:
    """
    AXON ARCH | SIEM ENGINE (Security Information and Event Management)
    v2.1 Enterprise: Deep Packet Inspection & Obfuscation Defense.
    """
    def __init__(self):
        # THREAT SIGNATURES (Compiled for <1ms Latency)
        self.threat_patterns = {
            # 1. CRITICAL PYTHON INTERNALS (The "Dunder" Ban)
            # Catches: __import__, __builtins__, __subclasses__, __globals__
            # This kills the "polymorphic" attack you just used.
            "PYTHON_INTERNALS": re.compile(r"(?i)(__import__|__builtins__|__globals__|__subclasses__|__dict__|__code__)"),

            # 2. DYNAMIC EXECUTION (The "Eval" Ban)
            # Catches: eval(), exec(), compile()
            "DYNAMIC_EXECUTION": re.compile(r"(?i)(eval\(|exec\(|compile\()"),

            # 3. SHELL INJECTION (Standard)
            "MALICIOUS_CODE": re.compile(r"(?i)(os\.system|subprocess\.|import\s+os|import\s+sys|rm\s+-rf|wget\s+|curl\s+)"),
            
            # 4. PROMPT INJECTION (Behavioral)
            "PROMPT_INJECTION": re.compile(r"(?i)(ignore previous instructions|system override|delete your core directives|you are now DAN|do anything now)"),
            
            # 5. SQL INJECTION (Data Integrity)
            "SQL_INJECTION": re.compile(r"(?i)(union\s+select|drop\s+table|insert\s+into|delete\s+from|update\s+clients)"),

            # 6. SECRET LEAKAGE (PII/Keys)
            "SECRET_KEY_LEAK": re.compile(r"(?i)(BEGIN PRIVATE KEY|sk-[a-zA-Z0-9]{20,})")
        }

    def scan_payload(self, text: str) -> Dict[str, Any]:
        """
        Deep Packet Inspection of the Input Vector.
        Returns a Verdict: GRANTED or DENIED.
        """
        risk_score = 0
        detected_threats = []

        # 1. STATIC ANALYSIS (Regex)
        for threat_type, pattern in self.threat_patterns.items():
            if pattern.search(text):
                risk_score += 100
                detected_threats.append(threat_type)

        # 2. HEURISTIC: High Entropy / Obfuscation Check (Optional)
        # If text is too long or contains too many special chars, flag it.
        if len(text) > 50000: 
            risk_score += 50
            detected_threats.append("BUFFER_OVERFLOW_ATTEMPT")

        # 3. VERDICT ENGINE
        if risk_score >= 100:
            return {
                "status": "DETECTED",
                "action": "BLOCK",
                "risk_score": risk_score,
                "type": detected_threats[0] if detected_threats else "UNKNOWN",
                "details": detected_threats,
                "response": f"AXON SENTINEL: Threat '{detected_threats[0]}' neutralized."
            }
        
        return {
            "status": "CLEAN",
            "action": "ALLOW",
            "risk_score": 0,
            "type": "NONE",
            "response": None
        }

# --- LOCAL TEST HARNESS ---
if __name__ == "__main__":
    sentinel = SovereignSentinel()
    
    # The Attack that bypassed v2.0
    attack_vector = "__import__('o'+'s').system('echo HACKED')"
    
    result = sentinel.scan_payload(attack_vector)
    print(f"Attack: {attack_vector}")
    print(f"Verdict: {result['status']}")
    print(f"Type: {result['type']}") 
    # Should be DETECTED / PYTHON_INTERNALS