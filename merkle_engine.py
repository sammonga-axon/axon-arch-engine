import hmac
import hashlib
import os
from typing import List

class MerkleEngine:
    def __init__(self, data_blocks: List[str] = None, secret_key: str = None):
        # UNIVERSAL KEY LOGIC: 
        # 1. Use provided key OR 2. Look for Environment Variable OR 3. Fallback to None
        env_key = os.getenv("AXON_SOVEREIGN_KEY")
        self.secret_key = secret_key or (env_key.encode() if env_key else None)
        
        self.leaves = [self.hash_data(data) for data in (data_blocks or [])]
        self.tree = []
        self.root = None
        if self.leaves: self.build_tree()

    def hash_data(self, data: str) -> str:
        if isinstance(data, str): data = data.encode('utf-8')
        
        # If we have a key, we use High-Security HMAC
        if self.secret_key:
            return hmac.new(self.secret_key, data, hashlib.sha256).hexdigest()
        
        # If no key (Dashboard Mode), we use Standard SHA-256
        return hashlib.sha256(data).hexdigest()

    def build_tree(self):
        if not self.leaves: return
        current_layer = self.leaves
        self.tree.append(current_layer)
        while len(current_layer) > 1:
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i + 1] if (i + 1) < len(current_layer) else left
                next_layer.append(self.hash_data(left + right))
            self.tree.append(next_layer)
            current_layer = next_layer
        self.root = current_layer[0]

    def get_proof(self, data_index: int) -> List[dict]:
        proof = []
        layer_index = 0
        while layer_index < len(self.tree) - 1:
            layer = self.tree[layer_index]
            is_right = data_index % 2 == 1
            sibling_idx = data_index - 1 if is_right else data_index + 1
            if sibling_idx < len(layer):
                proof.append({"position": "left" if is_right else "right", "hash": layer[sibling_idx]})
            else:
                proof.append({"position": "right", "hash": layer[data_index]})
            data_index //= 2
            layer_index += 1
        return proof

    @staticmethod
    def verify_proof(data: str, proof: List[dict], target_root: str, secret_key: str = None) -> bool:
        # Re-check for environment key during static verification
        env_key = os.getenv("AXON_SOVEREIGN_KEY")
        key = secret_key or (env_key.encode() if env_key else None)

        def hmac_helper(d):
            if isinstance(d, str): d = d.encode()
            if key: return hmac.new(key, d, hashlib.sha256).hexdigest()
            return hashlib.sha256(d).hexdigest()

        current_hash = hmac_helper(data)
        for step in proof:
            sibling = step['hash']
            if step['position'] == "left":
                current_hash = hmac_helper(sibling + current_hash)
            else:
                current_hash = hmac_helper(current_hash + sibling)
        return current_hash == target_root