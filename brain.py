import config
from openai import OpenAI, RateLimitError
import logging
import re

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

# Initialize the generic OpenAI client with the provider-agnostic endpoint
client = OpenAI(
    api_key=config.API_KEY,
    base_url=config.BASE_URL
)

# Initialize a separate client for Vision so you can mix-and-match providers
vision_client = OpenAI(
    api_key=config.VISION_API_KEY,
    base_url=config.VISION_BASE_URL
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
            messages=messages,
            extra_body={"reasoning_format": "hidden"}
        )
        
        reply_text = response.choices[0].message.content
        logging.debug(f"Received raw: {reply_text}")
        
        # Strip any <think>...</think> blocks safely as a fallback
        reply_text = re.sub(r"<think>.*?</think>", "", reply_text, flags=re.DOTALL).strip()
        
        return reply_text
    except RateLimitError:
        return "I hit a rate limit just now, give me a second to catch my breath."
    except Exception as e:
        # Catch other API errors to prevent crashing the loop
        logging.exception("API call failed")
        return f"Whoops, I ran into an issue connecting to my brain: {e}"

def get_response_with_screen(user_message: str, memory_context: str, recent_history: list, screenshot_b64: str) -> str:
    """
    Sends the system prompt, memory facts, recent history, new user message and screen capture to the vision LLM.
    """
    full_system_prompt = SYSTEM_PROMPT
    if memory_context:
        full_system_prompt += "\n\nHere are some things you know about the user and past interactions:\n"
        full_system_prompt += memory_context

    messages = [
        {"role": "system", "content": full_system_prompt}
    ]
    
    for role, content in recent_history:
        messages.append({"role": role, "content": content})
        
    messages.append({
        "role": "user", 
        "content": [
            {"type": "text", "text": user_message},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}}
        ]
    })
    
    try:
        logging.debug(f"Sending vision messages: {messages}")
        response = vision_client.chat.completions.create(
            model=config.VISION_MODEL_NAME,
            messages=messages
        )
        
        reply_text = response.choices[0].message.content
        logging.debug(f"Received raw vision: {reply_text}")
        
        reply_text = re.sub(r"<think>.*?</think>", "", reply_text, flags=re.DOTALL).strip()
        
        return reply_text
    except RateLimitError:
        return "I hit a rate limit just now, give me a second to catch my breath."
    except Exception as e:
        logging.exception("Vision API call failed")
        return f"Whoops, I ran into an issue connecting to my visual brain: {e}"
