"""
JSON-based Database Engine
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import uuid
import aiosqlite
from app.core.config import settings

class Database:
    """Simple JSON-based database with SQLite fallback"""
    
    def __init__(self):
        self.db_path = settings.DATA_DIR / "db"
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.collections = {}
        self.sqlite_db = None
    
    async def connect(self):
        """Connect to database"""
        # Create SQLite connection for complex queries
        self.sqlite_db = await aiosqlite.connect(
            settings.DATA_DIR / "akavin.db"
        )
        
        # Create tables
        await self._create_tables()
        
        # Load JSON collections
        self._load_collections()
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.sqlite_db:
            await self.sqlite_db.close()
    
    def _load_collections(self):
        """Load all JSON collections"""
        for file in self.db_path.glob("*.json"):
            name = file.stem
            with open(file, 'r') as f:
                try:
                    data = json.load(f)
                    self.collections[name] = data
                except json.JSONDecodeError:
                    self.collections[name] = []
    
    def _save_collection(self, name: str):
        """Save a collection to disk"""
        file_path = self.db_path / f"{name}.json"
        with open(file_path, 'w') as f:
            json.dump(self.collections.get(name, []), f, indent=2)
    
    async def _create_tables(self):
        """Create SQLite tables"""
        await self.sqlite_db.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        await self.sqlite_db.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id TEXT PRIMARY KEY,
                data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        await self.sqlite_db.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        await self.sqlite_db.commit()
    
    # Collection operations
    
    def get_collection(self, name: str) -> List[Dict]:
        """Get a collection"""
        if name not in self.collections:
            self.collections[name] = []
        return self.collections[name]
    
    def insert(self, collection: str, data: Dict) -> Dict:
        """Insert a document into a collection"""
        if collection not in self.collections:
            self.collections[collection] = []
        
        # Add metadata
        if '_id' not in data:
            data['_id'] = str(uuid.uuid4())
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow().isoformat()
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow().isoformat()
        
        self.collections[collection].append(data)
        self._save_collection(collection)
        return data
    
    def find(self, collection: str, query: Dict = None) -> List[Dict]:
        """Find documents in a collection"""
        if collection not in self.collections:
            return []
        
        if not query:
            return self.collections[collection]
        
        # Simple filtering
        results = []
        for doc in self.collections[collection]:
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                results.append(doc)
        return results
    
    def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        """Find one document in a collection"""
        results = self.find(collection, query)
        return results[0] if results else None
    
    def update(self, collection: str, query: Dict, update: Dict) -> int:
        """Update documents in a collection"""
        if collection not in self.collections:
            return 0
        
        count = 0
        for i, doc in enumerate(self.collections[collection]):
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                # Update fields
                for key, value in update.items():
                    if key != '_id' and key != 'created_at':
                        doc[key] = value
                doc['updated_at'] = datetime.utcnow().isoformat()
                self.collections[collection][i] = doc
                count += 1
        
        if count > 0:
            self._save_collection(collection)
        return count
    
    def delete(self, collection: str, query: Dict) -> int:
        """Delete documents from a collection"""
        if collection not in self.collections:
            return 0
        
        original_len = len(self.collections[collection])
        self.collections[collection] = [
            doc for doc in self.collections[collection]
            if not all(doc.get(k) == v for k, v in query.items())
        ]
        deleted = original_len - len(self.collections[collection])
        
        if deleted > 0:
            self._save_collection(collection)
        return deleted
    
    # SQLite operations for complex queries
    
    async def execute_query(self, query: str, params: tuple = ()):
        """Execute a raw SQL query"""
        async with self.sqlite_db.execute(query, params) as cursor:
            return await cursor.fetchall()
    
    async def insert_sql(self, table: str, data: Dict):
        """Insert into SQLite"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        await self.sqlite_db.execute(query, tuple(data.values()))
        await self.sqlite_db.commit()
