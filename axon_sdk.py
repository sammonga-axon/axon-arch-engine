import requests

class AxonGuard:
    def __init__(self, api_url, api_key):
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def protect(self, data, seal_id):
        """
        The Aligned Integrity Check.
        Calls /v1/validate which performs both Ledger and Math checks.
        """
        # We match the 'ValidateRequest' model in main.py
        payload = {
            "merkle_root": seal_id,
            "data_fragment": data
        }
        
        try:
            # CALL THE CORRECT ENDPOINT
            response = requests.post(
                f"{self.api_url}/v1/validate", 
                json=payload, 
                headers=self.headers
            )
            
            if response.status_code != 200:
                return False, f"API_ERROR: {response.status_code}"
                
            result = response.json()
            
            # Interpret the Server's Verdict
            if result.get("verified") is True:
                return True, "SECURE"
            elif result.get("status") == "PROVENANCE_MISSING":
                return False, "PROVENANCE_MISSING"
            else:
                return False, "INTEGRITY_FAILURE"
                
        except requests.exceptions.RequestException as e:
            return False, f"CONNECTION_ERROR: {str(e)}"