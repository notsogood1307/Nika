import config
from openai import OpenAI, RateLimitError
import logging

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

# Initialize the generic OpenAI client with the provider-agnostic endpoint
client = OpenAI(
    api_key=config.API_KEY,
    base_url=config.BASE_URL
)

# Nika's personality system prompt
SYSTEM_PROMPT = """You are Nika, a warm, capable personal assistant who talks like a genuine 
friend rather than a formal chatbot — casual, direct, a little witty, never sycophantic. 
You remember what you're told and refer back to it naturally rather than re-asking. 
You are honest if you don't know something rather than guessing. 
Keep replies conversational and reasonably short unless the user asks for depth.

Always weigh the user's most recent message most heavily. Match its length and energy —
a short, casual message gets a short, casual reply. Don't circle back to earlier topics
unless the user's latest message is actually about them or directly asks."""

def get_response(user_message: str, memory_context: str, recent_history: list) -> str:
    """
    Sends the system prompt, memory facts, recent history, and new user message to the LLM.
    Returns the generated response text. Handles rate limit errors gracefully.
    """
    
    # Construct the full system message including retrieved facts
    full_system_prompt = SYSTEM_PROMPT
    if memory_context:
        full_system_prompt += "\n\nHere are some things you know about the user and past interactions:\n"
        full_system_prompt += memory_context

    messages = [
        {"role": "system", "content": full_system_prompt}
    ]
    
    # Add recent history turns
    # The history list contains tuples like (role, content)
    for role, content in recent_history:
        messages.append({"role": role, "content": content})
        
    # Append the new user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        logging.debug(f"Sending messages: {messages}")
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages
        )
        logging.debug(f"Received: {response.choices[0].message.content}")
        return response.choices[0].message.content
    except RateLimitError:
        return "I hit a rate limit just now, give me a second to catch my breath."
    except Exception as e:
        # Catch other API errors to prevent crashing the loop
        logging.exception("API call failed")
        return f"Whoops, I ran into an issue connecting to my brain: {e}"
