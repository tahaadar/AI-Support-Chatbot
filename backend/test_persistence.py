import main
from config import SessionManager
from database import MongoDB

# Test 1: Create sessions and persist
print("=== TEST 1: Create and Persist ===")
client = main.initialize_client()
manager = SessionManager(client)

session1 = manager.create_session()
response = manager.add_user_message_and_get_response(session1, "Docker won't start")
print(f"Session {session1} created and saved")

# Test 2: Simulate restart
print("\n=== TEST 2: Simulate Restart ===")
del manager  # Destroy manager

# Create new manager and load sessions
manager2 = SessionManager(client)
manager2.load_active_sessions()
print(f"Active sessions after restart: {manager2.get_active_sessions()}")

# Test 3: Continue old conversation
print("\n=== TEST 3: Continue Conversation ===")
response = manager2.add_user_message_and_get_response(session1, "Port 8080 is blocked")
print(f"Bot remembers context: {response[:100]}...")

# Test 4: Search functionality
print("\n=== TEST 4: Search ===")
results = manager2.search_all_conversations("Docker")
print(f"Found {len(results)} results for 'Docker'")

# Test 5: Analytics
print("\n=== TEST 5: Analytics ===")
db = MongoDB()
analytics = db.get_session_analytics()
print(f"Analytics: {analytics}")