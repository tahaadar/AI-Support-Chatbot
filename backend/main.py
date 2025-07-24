import os
from dotenv import load_dotenv
from groq import Groq
import time

load_dotenv()

def initialize_client():
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )
    return client

def prompt_handle(conversation_history, client, max_retries=3):
    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
            messages=conversation_history,
            model="llama-3.3-70b-versatile",
            temperature=0.5
            )

            return chat_completion.choices[0].message.content
        except Groq.RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                print(f"Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return "System is experiencing high demand. Please try again in a moment."
                
        except Groq.APIConnectionError as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return "Connection issue detected. Please check your internet connection."
            
        except Groq.AuthenticationError as e:
            # Don't retry auth errors
            print(f"Authentication failed: {e}")
            return "System configuration error. Please contact support."
            
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")
            return "An unexpected error occurred. Please try rephrasing your question."