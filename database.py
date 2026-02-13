import os
import json
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

# Load the Connection String (Ensure this uses Port 6543 for Transaction Pooling)
DB_URL = os.getenv("DATABASE_URL")

class AxonDB:
    def __init__(self):
        self.mode = "POSTGRES"
        self.conn = None
        
        # 1. STRATEGIC ATTEMPT: Sovereign Cloud Vault (Supabase)
        if DB_URL:
            try:
                # Use connect_timeout to prevent the app from hanging on cold starts
                self.conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor, connect_timeout=10)
                print("AXON ARCH | CONNECTED: Sovereign Cloud Vault (Supabase)")
            except Exception as e:
                print(f"--- CLOUD CONNECTION FAILED: {e} ---")
                self.conn = None

        # 2. TACTICAL FALLBACK: Persistent Local Ledger (SQLite)
        if not self.conn:
            self.mode = "SQLITE"
            
            # Check for Render Persistent Disk mount point
            if os.path.exists("/var/lib/axon_data"):
                db_path = "/var/lib/axon_data/axon_ledger.db"
                print(f"AXON ARCH | STORAGE: 💾 PERSISTENT DISK ({db_path})")
            else:
                db_path = "axon_ledger.db"
                print("AXON ARCH | STORAGE: ⚠️ EPHEMERAL CONTAINER (Data loss on restart)")
            
            print(f"AXON ARCH | MODE: Tactical Local Ledger (SQLite)")
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def init_db(self):
        cursor = self.get_cursor()
        
        if self.mode == "POSTGRES":
            # PostGres Schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    api_key TEXT PRIMARY KEY,
                    organization_name TEXT,
                    tier TEXT DEFAULT 'Gatekeeper',
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS provenance_log (
                    id SERIAL PRIMARY KEY,
                    client_key TEXT,
                    merkle_root TEXT,
                    stored_data TEXT, 
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Seed Admin
            cursor.execute('''
                INSERT INTO clients (api_key, organization_name, tier) 
                VALUES (%s, %s, %s)
                ON CONFLICT (api_key) DO NOTHING
            ''', ("SOVEREIGN_KEY_001", "AXON_ARCH_ADMIN", "Sovereign"))
            
        else: 
            # SQLite Schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    api_key TEXT PRIMARY KEY,
                    organization_name TEXT,
                    tier TEXT DEFAULT 'Gatekeeper',
                    active BOOLEAN DEFAULT 1
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS provenance_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_key TEXT,
                    merkle_root TEXT,
                    stored_data TEXT, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Seed Admin
            try:
                cursor.execute('''
                    INSERT INTO clients (api_key, organization_name, tier) 
                    VALUES (?, ?, ?)
                ''', ("SOVEREIGN_KEY_001", "AXON_ARCH_ADMIN", "Sovereign"))
            except sqlite3.IntegrityError:
                pass 

        self.commit()
        print(f"AXON ARCH | {self.mode}: Schema Initialized.")

    def validate_key(self, api_key: str):
        cursor = self.get_cursor()
        if self.mode == "SQLITE":
            query = "SELECT * FROM clients WHERE api_key = ? AND active = 1"
        else:
            query = "SELECT * FROM clients WHERE api_key = %s AND active = TRUE"
        
        cursor.execute(query, (api_key,))
        return cursor.fetchone()

    def log_seal(self, api_key: str, root_hash: str, data_payload: list) -> int:
        cursor = self.get_cursor()
        data_json = json.dumps(data_payload)
        
        if self.mode == "POSTGRES":
            cursor.execute(
                "INSERT INTO provenance_log (client_key, merkle_root, stored_data) VALUES (%s, %s, %s) RETURNING id", 
                (api_key, root_hash, data_json)
            )
            result = cursor.fetchone()
            return result['id']
        else:
            cursor.execute(
                "INSERT INTO provenance_log (client_key, merkle_root, stored_data) VALUES (?, ?, ?)", 
                (api_key, root_hash, data_json)
            )
            return cursor.lastrowid

    def verify_integrity(self, root_hash: str):
        cursor = self.get_cursor()
        print(f"DEBUG: Searching for Root Hash: {root_hash}")
        
        if self.mode == "POSTGRES":
            cursor.execute("SELECT * FROM provenance_log WHERE merkle_root = %s", (root_hash,))
        else:
            cursor.execute("SELECT * FROM provenance_log WHERE merkle_root = ?", (root_hash,))
            
        result = cursor.fetchone()
        if result:
            print("DEBUG: Hash FOUND in Ledger.")
        else:
            print("DEBUG: Hash NOT FOUND.")
        return result

    def close(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    db = AxonDB()
    db.init_db()
    db.close()