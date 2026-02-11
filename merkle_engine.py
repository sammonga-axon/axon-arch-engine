import hmac
import hashlib
import os
from typing import List

class MerkleEngine:
    """
    AXON ARCH Provenance Engine | HMAC Edition.
    Secures the Merkle Tree with a Sovereign Salt (Secret Key).
    """

    def __init__(self, data_blocks: List[str] = None, secret_key: str = None):
        # 1. Load the Sovereign Key (Fail-safe: defaults to a dev key if missing)
        self.secret_key = secret_key if secret_key else os.getenv("AXON_SOVEREIGN_KEY", "dev_secret_2026_default").encode()
        
        self.leaves = []
        if data_blocks:
            self.leaves = [self.hash_data(data) for data in data_blocks]
        
        self.tree = []
        self.root = None
        
        if self.leaves:
            self.build_tree()

    def hash_data(self, data: str) -> str:
        """
        Creates an HMAC-SHA256 hash. 
        Formula: HMAC = H((K ^ opad) || H((K ^ ipad) || m))
        This prevents 'Length Extension Attacks'.
        """
        # Ensure data is bytes
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        return hmac.new(
            self.secret_key, 
            data, 
            hashlib.sha256
        ).hexdigest()

    def build_tree(self):
        """Constructs the tree using the HMAC function."""
        if not self.leaves:
            self.root = None
            return

        current_layer = self.leaves
        self.tree.append(current_layer)

        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                # Duplicate last node if odd number of leaves
                right = current_layer[i + 1] if (i + 1) < len(current_layer) else left
                
                # Hash the combined pair using HMAC
                combined_hash = self.hash_data(left + right)
                next_layer.append(combined_hash)
            
            self.tree.append(next_layer)
            current_layer = next_layer

        self.root = current_layer[0]

    def get_proof(self, data_index: int) -> List[dict]:
        """Generates the Merkle Proof path."""
        proof = []
        layer_index = 0
        
        # Determine the path from the leaf to the root
        while layer_index < len(self.tree) - 1:
            layer = self.tree[layer_index]
            is_right_node = data_index % 2 == 1
            sibling_index = data_index - 1 if is_right_node else data_index + 1

            if sibling_index < len(layer):
                proof.append({
                    "position": "left" if is_right_node else "right",
                    "hash": layer[sibling_index]
                })
            else:
                proof.append({
                    "position": "right",
                    "hash": layer[data_index] 
                })

            data_index //= 2
            layer_index += 1

        return proof

    @staticmethod
    def verify_proof(data: str, proof: List[dict], target_root: str, secret_key: str = None) -> bool:
        """
        The 'Intent Invalidation' Logic using HMAC.
        Requires the Sovereign Key to reconstruct the truth.
        """
        # Load Key
        key = secret_key if secret_key else os.getenv("AXON_SOVEREIGN_KEY", "dev_secret_2026_default").encode()
        
        # Helper to run HMAC locally
        def hmac_helper(d):
            if isinstance(d, str): d = d.encode()
            return hmac.new(key, d, hashlib.sha256).hexdigest()

        current_hash = hmac_helper(data)

        for step in proof:
            sibling = step['hash']
            if step['position'] == "left":
                current_hash = hmac_helper(sibling + current_hash)
            else:
                current_hash = hmac_helper(current_hash + sibling)

        return current_hash == target_root