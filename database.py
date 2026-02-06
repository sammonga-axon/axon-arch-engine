import sqlite3
import json

DB_NAME = "axon_arch_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Clients Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            api_key TEXT PRIMARY KEY,
            organization_name TEXT,
            tier TEXT DEFAULT 'Gatekeeper',
            active INTEGER DEFAULT 1
        )
    ''')
    
    # 2. Provenance Log (Updated for V1.1 to store the Data Payload)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS provenance_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_key TEXT,
            merkle_root TEXT,
            stored_data TEXT,  -- New: Stores the full JSON batch
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(client_key) REFERENCES clients(api_key)
        )
    ''')
    
    cursor.execute("INSERT OR IGNORE INTO clients (api_key, organization_name, tier) VALUES (?, ?, ?)", 
                   ("SOVEREIGN_KEY_001", "AXON_ARCH_ADMIN", "Sovereign"))
    
    conn.commit()
    conn.close()
    print("AXON ARCH V1.1: Database initialized.")

class AxonDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.row_factory = sqlite3.Row

    def validate_key(self, api_key: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE api_key = ? AND active = 1", (api_key,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def log_seal(self, api_key: str, root_hash: str, data_payload: list) -> int:
        """Saves the Root AND the Data Batch."""
        cursor = self.conn.cursor()
        data_json = json.dumps(data_payload) # Convert list to string
        cursor.execute("INSERT INTO provenance_log (client_key, merkle_root, stored_data) VALUES (?, ?, ?)", 
                       (api_key, root_hash, data_json))
        self.conn.commit()
        return cursor.lastrowid

    def get_batch_by_root(self, root_hash: str):
        """Retrieves the original data batch using the Seal ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT stored_data FROM provenance_log WHERE merkle_root = ?", (root_hash,))
        row = cursor.fetchone()
        return json.loads(row['stored_data']) if row else None

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    init_db()