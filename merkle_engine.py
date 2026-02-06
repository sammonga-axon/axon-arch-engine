import hashlib
from typing import List, Optional

class MerkleEngine:
    """
    AXON ARCH Provenance Engine.
    Implements a standard Merkle Tree for immutable data verification.
    """

    def __init__(self, data_blocks: List[str] = None):
        self.leaves = []
        if data_blocks:
            self.leaves = [self.hash_data(data) for data in data_blocks]
        self.tree = []
        self.root = None
        if self.leaves:
            self.build_tree()

    @staticmethod
    def hash_data(data: str) -> str:
        """
        Creates a SHA-256 hash of the input data.
        This is the 'Digital Fingerprint'.
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def build_tree(self):
        """
        Constructs the Merkle Tree from the leaves up to the Root.
        """
        if not self.leaves:
            self.root = None
            return

        # Start with the bottom layer (the data hashes)
        current_layer = self.leaves
        self.tree.append(current_layer)

        # Loop until we reach the single Root hash
        while len(current_layer) > 1:
            next_layer = []
            
            # Process pairs of hashes
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                # If there is no right partner, duplicate the left one (standard practice)
                right = current_layer[i + 1] if (i + 1) < len(current_layer) else left
                
                # Combine and hash the pair
                combined_hash = self.hash_data(left + right)
                next_layer.append(combined_hash)
            
            self.tree.append(next_layer)
            current_layer = next_layer

        # The last remaining hash is the Master Root
        self.root = current_layer[0]

    def get_proof(self, data_index: int) -> List[dict]:
        """
        Generates a 'Merkle Proof' for a specific piece of data.
        This allows a client to verify one record without downloading the whole database.
        """
        proof = []
        layer_index = 0
        
        # Determine the path from the leaf to the root
        while layer_index < len(self.tree) - 1:
            layer = self.tree[layer_index]
            is_right_node = data_index % 2 == 1
            sibling_index = data_index - 1 if is_right_node else data_index + 1

            # If the sibling index is valid, add it to the proof
            if sibling_index < len(layer):
                proof.append({
                    "position": "left" if is_right_node else "right",
                    "hash": layer[sibling_index]
                })
            else:
                # Handle the case where the node was duplicated (odd number of leaves)
                proof.append({
                    "position": "right",
                    "hash": layer[data_index] 
                })

            data_index //= 2
            layer_index += 1

        return proof

    @staticmethod
    def verify_proof(data: str, proof: List[dict], target_root: str) -> bool:
        """
        The 'Intent Invalidation' Logic.
        Reconstructs the root from the data + proof. If it matches the target_root, the data is TRUTH.
        """
        current_hash = MerkleEngine.hash_data(data)

        for step in proof:
            sibling = step['hash']
            if step['position'] == "left":
                current_hash = MerkleEngine.hash_data(sibling + current_hash)
            else:
                current_hash = MerkleEngine.hash_data(current_hash + sibling)

        return current_hash == target_root

# --- Quick Test Block (Only runs if you execute this file directly) ---
if __name__ == "__main__":
    print("--- AXON ARCH ENGINE DIAGNOSTIC ---")
    
    # 1. Simulate Client Data
    records = ["Patient_A_Diagnosis_Clean", "Financial_Transaction_X_Verified", "Log_Entry_77_Secure"]
    
    # 2. Build the Arch
    engine = MerkleEngine(records)
    print(f"Merkle Root (Seal): {engine.root}")
    
    # 3. Generate a Proof for Record #1 (Financial Transaction)
    proof_for_tx = engine.get_proof(1)
    
    # 4. Verify (The "Truth" Check)
    is_valid = MerkleEngine.verify_proof("Financial_Transaction_X_Verified", proof_for_tx, engine.root)
    print(f"Verification Result (Original Data): {is_valid}") # Should be True
    
    # 5. Verify a LIE (The "Poison" Check)
    is_valid_lie = MerkleEngine.verify_proof("Financial_Transaction_X_CORRUPTED", proof_for_tx, engine.root)
    print(f"Verification Result (Corrupted Data): {is_valid_lie}") # Should be False