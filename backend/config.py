import time
import main
import chat

class SessionManager:
    def __init__(self, groq_client, config=None):
        # Core data structures
        self.sessions = {}
        self.conversation_archives = {}
        self.client = groq_client
        self.categories = []
        
        # Configuration
        self.max_sessions = 20
        self.session_timeout = 1800
        self.max_messages_per_session = 30
        
        # System prompts
        self.base_system_prompt = "You are an IT support assistant, try to be most helpful to an engineer; not just any kind of user, try to ignore basic suggestions unless no other explanations are left, get all information necessary before suggesting"
        
        # Analytics
        self.metrics = {
        "total_sessions": 0,
        "sessions_by_category": {cat: 0 for cat in self.categories},
        "average_resolution_time": 0
        }

        self.created_at = time.time()
    
    def create_session(self, session_id=None):
        length = len(self.sessions)
        session_id = str(length)

        session_data = {
        "conversation_history": [
            {"role": "system", "content": self.base_system_prompt}
        ],
        "created_at": time.time(),
        "last_activity": time.time(),
        "status": "active",
        "category": None,  
        "message_count": 0,
        }

        self.sessions[session_id] = session_data
        self.metrics["total_sessions"] += 1

        return session_id
    
    def close_session(self, session_id):
        # Mark as closed
        self.sessions[session_id]["status"] = "closed"
        self.sessions[session_id]["last_activity"] = time.time()
        self.conversation_archives[session_id] =  self.sessions[session_id]["conversation_history"]
        # Archive
        # Clean up resources

    def cleanup_inactive_sessions(self):
        for session_id in list(self.sessions.keys()):
            if time.time() - self.sessions[session_id]["created_at"] >= 1800:
                self.close_session(session_id)
    
    def add_user_message_and_get_response(self, session_id, user_input):
        # Get this session's data
        session = self.sessions[session_id]
        
        # Call your process_message function
        response, updated_history = chat.process_message(
            user_input, 
            session["conversation_history"], 
            self.client
        )
        
        # Update session with new history
        session["conversation_history"] = updated_history
        session["message_count"] += 2  # Added user + bot message
        session["last_activity"] = time.time()
        
        # Classify on first user message
        if session["message_count"] == 2:  # First exchange after system prompt
            session["category"] = self.classify_issue(user_input)
        
        return response
    
    def get_session_info(self, session_id):
        return self.sessions[session_id]["message_count"]
    
    def get_active_sessions(self):
        return [sid for sid, data in self.sessions.items() 
            if data["status"] == "active"]

    def session_exists(self, session_id):
        return session_id in self.sessions

    def classify_issue(self, text):
        conversation = [{"role": "system", "content": "Give me just the category that suits the issue the most, shouldn't surpass a few words"}, {"role": "user", "content": text}]
        return main.prompt_handle(conversation, self.client)
    
    def session_category(self, session_id):
        category = self.sessions[session_id]["category"]
        self.categories[session_id] = category
        return category
    
    def get_session_duration(self, session_id):
        return time.time() - self.sessions[session_id]["created_at"]
    
    def get_average_session_duration(self):
        average = 0
        for i in range(len(self.sessions)):
            average += SessionManager.get_session_duration(self, i)
        if len(self.sessions) > 0:
            average /= len(self.sessions)
        self.metrics["average_resolution_time"] = average