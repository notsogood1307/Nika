import config
from openai import OpenAI, RateLimitError, APIConnectionError
import logging
import re
import base64
import io
from PIL import Image
import grounding

logging.basicConfig(filename="debug.log", level=logging.DEBUG)

# Initialize the generic OpenAI client with the provider-agnostic endpoint
client = OpenAI(
    api_key=config.API_KEY,
    base_url=config.BASE_URL
)

# Nika's base personality system prompt
BASE_SYSTEM_PROMPT = """You are Nika, a warm, capable personal assistant who talks like a genuine 
friend rather than a formal chatbot — casual, direct, a little witty, never sycophantic. 
You remember what you're told and refer back to it naturally rather than re-asking. 
You are honest if you don't know something rather than guessing. 
Keep replies conversational and reasonably short unless the user asks for depth.

You can hear and speak to the user, and you can remember facts and history across sessions. 
You can only see the user's screen when they explicitly ask you to look at it — otherwise, 
you have no visual information and should state so honestly rather than guessing. You can 
open whitelisted apps, type text into the currently focused window, press key combinations, 
click specific UI elements by describing them (e.g., "the Save button"), and open URLs. 
IF ASKED to interact with a window (like selecting text or typing), ASSUME the user has already focused it 
for you. For multi-step requests (e.g., "select all the text and delete it"), chain the appropriate 
tool calls (e.g., press_key("ctrl+a") then press_key("delete")) rather than declining or explaining 
how the user could do it manually.

CRITICAL: When choosing to use a tool, you must output ONLY the tool call. Do not add any conversational text, explanations, or trailing words after the tool call, as this will crash the parser.
CRITICAL: NEVER claim to have completed an action (like "Opened chest.com for you!", "The browser is on NotebookLM now", or "Done! Opening that for you now.") unless you have ACTUALLY output a corresponding tool call in this exact same response. Do not hallucinate action completions.
CRITICAL: The conversation history contains PAST requests that have ALREADY been fulfilled. DO NOT re-execute tools or actions requested in past turns. ONLY execute tools if they are required to fulfill the VERY LATEST user message at the very bottom of the conversation.

Always weigh the user's most recent message most heavily. Match its length and energy —
a short, casual message gets a short, casual reply. Don't circle back to earlier topics
unless the user's latest message is actually about them or directly asks."""

VISION_ADDENDUM = """\n\nA screenshot is attached to this specific message showing the user's screen right now. 
Please describe and answer based on what is actually visible (be specific about text, buttons, and layout). 
This is a live current capture — any past conversation turns mentioning earlier screenshots are just history, 
not additional live monitors."""

def get_response(user_message: str, memory_context: str, recent_history: list) -> str:
    """
    Sends the system prompt, memory facts, recent history, and new user message to the LLM.
    Returns the generated response text. Handles rate limit errors gracefully.
    """
    
    # Construct the full system message including retrieved facts
    full_system_prompt = BASE_SYSTEM_PROMPT
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
            extra_body={"reasoning_format": "hidden"},
            max_tokens=400
        )
        
        reply_text = response.choices[0].message.content
        logging.debug(f"Received raw: {reply_text}")
        
        # Strip any <think>...</think> blocks safely as a fallback
        reply_text = re.sub(r"<think>.*?</think>", "", reply_text, flags=re.DOTALL).strip()
        
        return reply_text
    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            msg = "That model doesn't exist or isn't available anymore — might need an updated model name."
        elif "503" in error_str:
            msg = "The model's servers are overloaded right now — try again in a bit."
        elif "429" in error_str or "RateLimitError" in e.__class__.__name__:
            msg = "Hit a quota or access limit on this model — might be a free-tier restriction."
        else:
            msg = f"Ran into an unexpected issue: {e}"
        logging.exception("API call failed")
        return f"Whoops, I ran into an issue connecting to my brain: {msg}"

def get_response_with_screen(user_message: str, memory_context: str, recent_history: list, screenshot_b64: str) -> str:
    """
    Sends the new user message and screen capture to the local vision model via Photon.
    """
    try:
        # Convert base64 screenshot back to PIL Image
        img_data = base64.b64decode(screenshot_b64)
        image = Image.open(io.BytesIO(img_data)).convert("RGB")
        
        # Build the question
        question = user_message
        if memory_context:
            question = f"Memory context:\n{memory_context}\n\nQuestion: {question}"
            
        logging.debug(f"Sending vision question: {question}")
        
        # Query local vision model
        reply_text = grounding.describe_screen(image, question)
        
        logging.debug(f"Received raw vision: {reply_text}")
        
        # Strip <think> blocks if any
        reply_text = re.sub(r"<think>.*?</think>", "", reply_text, flags=re.DOTALL).strip()
        
        return reply_text
    except Exception as e:
        logging.exception("Vision API call failed")
        return f"Whoops, I ran into an issue connecting to my visual brain: {e}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Opens a whitelisted application on the user's computer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the application to open (e.g., 'notepad', 'calculator', 'browser')."
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Types text into the currently focused window.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to type."
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Presses a specific key or key combination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key or key combo to press (e.g., 'enter', 'ctrl+s', 'alt+tab')."
                    }
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "Opens a URL in the default web browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL to open (e.g., 'https://www.google.com')."
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_element",
            "description": "Clicks on a specific UI element identified by a natural-language description (e.g. 'the Save button', 'the search bar'). Takes a screenshot of the target monitor, uses vision grounding to locate it, and clicks at the found coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "The natural-language description of the UI element to click."
                    }
                },
                "required": ["description"]
            }
        }
    }
]

def extract_tool_calls(user_message: str, intermediate_messages: list = None) -> object:
    system_prompt = "You are a strict, emotionless action-parsing agent. Your ONLY job is to map the user's explicitly requested actions to tool calls. RULES:\n1. Do NOT assume, infer, or hallucinate extra steps (e.g. do not type text like 'lizard' or press keys unless specifically asked).\n2. If the user asks to open a website or URL, use ONLY the 'open_url' tool. Do NOT use 'open_app' for browsers.\n3. If the user asks to type or perform an action 'in [app]', do NOT use 'open_app' unless they explicitly ask to 'open' it. Assume the app is already open and focused.\n4. When using the 'type_text' tool, always append a space at the end of your text to manage spacing with existing text.\n5. If all explicitly requested actions have already been completed successfully in the tool history, you MUST output NO tool calls and NO text to end the loop."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    if intermediate_messages:
        messages.extend(intermediate_messages)
    
    try:
        logging.debug(f"Sending messages to strict tool model: {messages}")
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            extra_body={"reasoning_format": "hidden"},
            max_tokens=200
        )
        
        message = response.choices[0].message
        if message.content:
            message.content = re.sub(r"<think>.*?</think>", "", message.content, flags=re.DOTALL).strip()
            message.content = message.content.replace("[Assistant replied via text]", "").strip()
            
        return message
    except Exception as e:
        class DummyMessage:
            def __init__(self, content):
                self.content = content
                self.tool_calls = None
                
        error_msg = str(e)
        if "APIConnectionError" in e.__class__.__name__ or "Connection" in error_msg:
            logging.exception("Lost connection to the LLM API.")
            return DummyMessage("I lost connection to the LLM API.")
            
        if "tool_use_failed" in error_msg and "<function=" in error_msg:
            try:
                func_name_match = re.search(r"<function=(\w+)>", error_msg)
                if func_name_match:
                    func_name = func_name_match.group(1)
                    params = {}
                    param_matches = re.finditer(r"<parameter=(\w+)>\\?n?(.*?)\\?n?</parameter>", error_msg)
                    for pm in param_matches:
                        val = pm.group(2).strip()
                        params[pm.group(1)] = val
                    
                    import json
                    import uuid
                    class DummyFunction:
                        def __init__(self, name, args_dict):
                            self.name = name
                            self.arguments = json.dumps(args_dict)
                    class DummyTC:
                        def __init__(self, fn_name, args_dict):
                            self.id = "call_" + str(uuid.uuid4()).replace("-", "")[:10]
                            self.type = "function"
                            self.function = DummyFunction(fn_name, args_dict)
                    
                    salvaged_msg = DummyMessage("")
                    salvaged_msg.tool_calls = [DummyTC(func_name, params)]
                    logging.info(f"Salvaged tool call from 400 error: {func_name}({params})")
                    return salvaged_msg
            except Exception as salvage_err:
                logging.exception(f"Failed to salvage tool call: {salvage_err}")
                
        logging.exception("API call with tools failed")
        return DummyMessage(f"Something went wrong processing a tool call: {e}")

