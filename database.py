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
            self.conn = sqlite3.connect("axon_ledger.db", check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def init_db(self):
        """Universal Schema Init for both Cloud and Local"""
        cursor = self.get_cursor()
        
        # SQL Syntax differs slightly, but this works for both for simple tables
        if self.mode == "POSTGRES":
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
            
        else: # SQLITE MODE
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
                pass # Already exists

        self.commit()
        print(f"AXON ARCH | {self.mode}: Schema Initialized.")

    def validate_key(self, api_key: str):
        cursor = self.get_cursor()
        query = "SELECT * FROM clients WHERE api_key = ? AND active = 1" if self.mode == "SQLITE" else "SELECT * FROM clients WHERE api_key = %s AND active = TRUE"
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
            return cursor.fetchone()['id']
        else:
            cursor.execute(
                "INSERT INTO provenance_log (client_key, merkle_root, stored_data) VALUES (?, ?, ?)", 
                (api_key, root_hash, data_json)
            )
            return cursor.lastrowid

    def close(self):
        if self.conn:
            self.conn.close()

# STANDALONE INIT
if __name__ == "__main__":
    db = AxonDB()
    db.init_db()
    db.close()