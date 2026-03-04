import os
import json
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

# Load the Connection String (Ensure this uses Port 6543 for Transaction Pooling)
DB_URL = os.getenv("DATABASE_URL")
# Extract admin key dynamically to prevent hardcoded credential leakage
ADMIN_KEY = os.getenv("AXON_SOVEREIGN_KEY", "UNCONFIGURED_KEY")

class AxonDB:
    def __init__(self):
        self.mode = "POSTGRES"
        self.conn = None
        
        # 1. STRATEGIC ATTEMPT: Sovereign Cloud Vault (Supabase)
        if DB_URL:
            self.conn = self._connect_postgres()

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

    def _connect_postgres(self):
        """Establishes a resilient PostgreSQL connection with OSI Layer 4 Keepalives."""
        try:
            conn = psycopg2.connect(
                DB_URL, 
                cursor_factory=RealDictCursor, 
                connect_timeout=10,
                keepalives=1,
                keepalives_idle=60,
                keepalives_interval=10,
                keepalives_count=5
            )
            # Autocommit ensures high-frequency SIEM writes do not lock the transaction table
            conn.autocommit = True
            print("AXON ARCH | CONNECTED: Sovereign Cloud Vault [KEEPALIVES ACTIVE]")
            return conn
        except Exception as e:
            print(f"--- CLOUD CONNECTION FAILED: {e} ---")
            return None

    def get_cursor(self):
        """Executes a pre-ping to mathematically guarantee socket liveliness before execution."""
        if self.mode == "POSTGRES":
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                print("AXON ARCH | SOCKET DEAD. Executing graceful reconnection...")
                self.conn = self._connect_postgres()
                if not self.conn:
                    raise Exception("DATABASE_UNREACHABLE")
        
        return self.conn.cursor()

    def commit(self):
        if self.mode == "SQLITE":
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
            # Seed Admin (Dynamic, Zero-Trust)
            cursor.execute('''
                INSERT INTO clients (api_key, organization_name, tier) 
                VALUES (%s, %s, %s)
                ON CONFLICT (api_key) DO NOTHING
            ''', (ADMIN_KEY, "AXON_ARCH_ADMIN", "Sovereign"))
            
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
            # Seed Admin (Dynamic, Zero-Trust)
            try:
                cursor.execute('''
                    INSERT INTO clients (api_key, organization_name, tier) 
                    VALUES (?, ?, ?)
                ''', (ADMIN_KEY, "AXON_ARCH_ADMIN", "Sovereign"))
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
            self.commit()
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
    print("AXON ARCH | PRE-FLIGHT CHECK: Bypassed. Handing execution to Uvicorn.")
    pass