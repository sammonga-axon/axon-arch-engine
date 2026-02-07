import requests

class AxonGuard:
    def __init__(self, api_url, api_key):
        # We strip any trailing slash to avoid errors like 'url//v1'
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def protect(self, data, seal_id):
        """
        The 'Automatic' check.
        It fetches the proof and verifies the data in one go.
        """
        # 1. Automatically fetch the proof (The "Receipt")
        proof_payload = {"target_root": seal_id, "target_data": data}
        
        try:
            proof_res = requests.post(f"{self.api_url}/v1/get_proof", json=proof_payload, headers=self.headers)
        except requests.exceptions.RequestException as e:
            return False, f"CONNECTION_ERROR: {str(e)}"

        if proof_res.status_code != 200:
            return False, "PROVENANCE_MISSING"

        proof = proof_res.json().get('proof')

        # 2. Automatically verify against the Seal (The "Judge")
        verify_payload = {"data": data, "target_root": seal_id, "proof": proof}
        
        try:
            verify_res = requests.post(f"{self.api_url}/v1/verify", json=verify_payload, headers=self.headers)
            result = verify_res.json()
            
            # 3. Return a clean verdict
            if result.get("intent") == "TRUTH":
                return True, "SECURE"
            else:
                return False, "POISONED"
                
        except requests.exceptions.RequestException:
            return False, "VERIFICATION_FAILED"