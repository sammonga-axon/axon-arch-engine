import os
import json
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor

# Load the Connection String
DB_URL = os.getenv("DATABASE_URL")

class AxonDB:
    def __init__(self):
        self.mode = "POSTGRES"
        self.conn = None
        
        # 1. Try Connecting to Cloud Vault (Supabase)
        if DB_URL:
            try:
                self.conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
                print("AXON ARCH | CONNECTED: Sovereign Cloud Vault (Supabase)")
            except Exception as e:
                print(f"--- CLOUD CONNECTION FAILED: {e} ---")
                self.conn = None

        # 2. Fallback to Local Ledger (SQLite) if Cloud fails
        if not self.conn:
            print("AXON ARCH | MODE: Tactical Local Ledger (SQLite)")
            self.mode = "SQLITE"
            
            # --- PERSISTENCE UPGRADE START ---
            # Check if we have a mounted disk at /var/lib/axon_data
            # You must create this 'Disk' in Render Dashboard first!
            if os.path.exists("/var/lib/axon_data"):
                db_path = "/var/lib/axon_data/axon_ledger.db"
                print(f"AXON ARCH | STORAGE: 💾 PERSISTENT DISK ({db_path})")
            else:
                db_path = "axon_ledger.db"
                print("AXON ARCH | STORAGE: ⚠️ EPHEMERAL CONTAINER (Data loss on restart)")
            # --- PERSISTENCE UPGRADE END ---

            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    # ... [Rest of your code remains exactly the same] ...