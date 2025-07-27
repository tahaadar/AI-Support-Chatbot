import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        uri = os.getenv("MONGODB_URI")
        self.client = MongoClient(
            uri,
            tls=True,
            tlsAllowInvalidCertificates=True
        )
        self.db = self.client.support_bot
        self.sessions = self.db.sessions
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for better performance"""
        self.sessions.create_index("status")
        self.sessions.create_index("created_at")
        self.sessions.create_index([("conversation_history.content", "text")])  # For search
    
    # Session operations
    def save_session(self, session_id, session_data):
        """Create or update session"""
        return self.sessions.replace_one(
            {"_id": session_id},
            {"_id": session_id, **session_data},
            upsert=True
        )
    
    def get_session(self, session_id):
        """Get single session"""
        return self.sessions.find_one({"_id": session_id})
    
    def get_active_sessions(self):
        """Get all active sessions"""
        return list(self.sessions.find({"status": "active"})) 
    
    def update_conversation(self, session_id, new_messages, metrics_update):
        """Efficiently update conversation and metrics"""
        return self.sessions.update_one(
            {"_id": session_id},
            {
                "$push": {"conversation_history": {"$each": new_messages}},
                "$set": {
                    "last_activity": datetime.now(),
                    **metrics_update
                }
            }
        )
    
    def close_session(self, session_id):
        """Mark session as closed"""
        return self.sessions.update_one(
            {"_id": session_id},
            {
                "$set": {
                    "status": "closed",
                    "closed_at": datetime.now()
                }
            }
        )
    
    def search_conversations(self, query):
        """Search across all conversations"""
        return list(self.sessions.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]))
    
    def get_session_analytics(self):
        """Get aggregate analytics"""
        pipeline = [
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "avg_messages": {"$avg": "$message_count"}
                }
            }
        ]
        return list(self.sessions.aggregate(pipeline))