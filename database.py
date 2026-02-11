import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Load the Connection String from the Environment
DB_URL = os.getenv("DATABASE_URL")

def get_connection():
    """
    Establishes a secure connection to the Sovereign Vault (Supabase).
    """
    if not DB_URL:
        raise ValueError("FATAL: DATABASE_URL is not set. The Vault is locked.")
    try:
        # FIX 1: Removed 'sslmode' kwarg because it is already in the DB_URL string.
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.Error as e:
        print(f"--- DATABASE CONNECTION ERROR: {e} ---")
        raise e

def init_db():
    """
    Self-Healing Schema: Automatically creates tables on startup.
    """
    if not DB_URL:
        print("--- WARNING: No DATABASE_URL found. Skipping DB Init. ---")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Clients Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                api_key TEXT PRIMARY KEY,
                organization_name TEXT,
                tier TEXT DEFAULT 'Gatekeeper',
                active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # 2. Provenance Log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS provenance_log (
                id SERIAL PRIMARY KEY,
                client_key TEXT,
                merkle_root TEXT,
                stored_data TEXT, 
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_key) REFERENCES clients(api_key)
            )
        ''')
        
        # 3. Seed the Admin Key
        cursor.execute('''
            INSERT INTO clients (api_key, organization_name, tier) 
            VALUES (%s, %s, %s)
            ON CONFLICT (api_key) DO NOTHING
        ''', ("SOVEREIGN_KEY_001", "AXON_ARCH_ADMIN", "Sovereign"))
        
        conn.commit()
        conn.close()
        print("AXON ARCH | POSTGRESQL: Schema Initialized.")
        
    except Exception as e:
        print(f"Schema Init Failed: {e}")

class AxonDB:
    def __init__(self):
        self.conn = get_connection()

    def validate_key(self, api_key: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE api_key = %s AND active = TRUE", (api_key,))
        return cursor.fetchone()

    def log_seal(self, api_key: str, root_hash: str, data_payload: list) -> int:
        """Saves the Root AND the Data Batch."""
        cursor = self.conn.cursor()
        data_json = json.dumps(data_payload)
        
        cursor.execute(
            "INSERT INTO provenance_log (client_key, merkle_root, stored_data) VALUES (%s, %s, %s) RETURNING id", 
            (api_key, root_hash, data_json)
        )
        
        # FIX 2: Handle potential None return (Safety Check)
        result = cursor.fetchone()
        if result is None:
            raise ValueError("Database Insert Failed: No ID returned.")
            
        row_id = result['id']
        self.conn.commit()
        return row_id

    def get_batch_by_root(self, root_hash: str):
        """Retrieves the original data batch using the Seal ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT stored_data FROM provenance_log WHERE merkle_root = %s", (root_hash,))
        row = cursor.fetchone()
        return json.loads(row['stored_data']) if row else None

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    init_db()