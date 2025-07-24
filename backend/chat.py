import main

client = main.initialize_client()

def maintain_window(conversation_history):
    if len(conversation_history) <= 10:
        return conversation_history
    return [conversation_history[0]] + conversation_history[-9:]

def process_message(user_prompt, conversation_history, client):
    # Add user message
    conversation_history.append({"role": "user", "content": user_prompt})
    
    # Get response
    response = main.prompt_handle(conversation_history, client)
    
    # Add assistant response
    conversation_history.append({"role": "assistant", "content": response})
    
    # Handle sliding window if needed
    if len(conversation_history) > 10:
        conversation_history = maintain_window(conversation_history)
    
    return response, conversation_history





