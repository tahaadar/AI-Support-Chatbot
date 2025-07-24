# test_concurrent.py
import main
from config import SessionManager

client = main.initialize_client()
manager = SessionManager(client)

# Create 3 different support sessions
session1 = manager.create_session()
session2 = manager.create_session()
session3 = manager.create_session()

print("=== SESSION 1: Docker Issue ===")
resp1 = manager.add_user_message_and_get_response(session1, "My Docker container won't start")
print(f"Bot: {resp1[:100]}...")  # First 100 chars

print("\n=== SESSION 2: Git Issue ===")
resp2 = manager.add_user_message_and_get_response(session2, "I can't push to git, getting permission denied")
print(f"Bot: {resp2[:100]}...")

print("\n=== SESSION 3: Database Issue ===")
resp3 = manager.add_user_message_and_get_response(session3, "PostgreSQL connection keeps timing out")
print(f"Bot: {resp3[:100]}...")

# Now continue with session 1 - it should remember Docker context
print("\n=== BACK TO SESSION 1 ===")
resp1_continue = manager.add_user_message_and_get_response(session1, "Port 8080 is the issue")
print(f"Bot remembers Docker context: {resp1_continue[:150]}...")

# Check all sessions are tracked
print(f"\n=== ACTIVE SESSIONS: {manager.get_active_sessions()} ===")
print(f"Session 1 category: {manager.sessions[session1]['category']}")
print(f"Session 2 category: {manager.sessions[session2]['category']}")
print(f"Session 3 category: {manager.sessions[session3]['category']}")

# Check message counts
print(f"\nSession 1 messages: {manager.sessions[session1]['message_count']}")
print(f"Session 2 messages: {manager.sessions[session2]['message_count']}")
print(f"Session 3 messages: {manager.sessions[session3]['message_count']}")