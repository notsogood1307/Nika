import sys
import builtins
import main
import guardrails
import memory

# Mock inputs to simulate the user's test scenario
inputs = [
    # 1. Ask to open URL and grant 'always allow'
    "Open youtube.com",
    "always allow",
    
    # 2. Ask to open a different URL to prove Tier 3 still blocks
    "Open chest.com",
    "yes",
    
    # 3. Ask for a longer response
    "Can you give me the solution for leetcode 78 in Python?",
    
    # 4. Garbled/ambiguous request testing the anti-hallucination structural fix
    "open o-class p-tashon browser",
    
    "exit"
]

def mock_get_mixed_input():
    if not inputs:
        return "exit"
    val = inputs.pop(0)
    print(f"\n[MOCK USER]: {val}")
    return val

# Override the input function
main.get_mixed_input = mock_get_mixed_input

# Prevent pyttsx3 from speaking during tests
def mock_speak(text):
    pass
main.voice_io.speak = mock_speak

# Disable db initialization warning
memory.db.init_db = lambda: None
# Mock memory DB to avoid filling real db with test data
def mock_get_recent_history(n=10): return []
def mock_get_all_facts(): return ""
def mock_log_message(role, content): pass
memory.get_recent_history = mock_get_recent_history
memory.get_all_facts = mock_get_all_facts
memory.log_message = mock_log_message
memory.summarize_if_needed = lambda: None

# Disable actual app launching
def mock_open_url(url):
    return f"Simulated opening URL: {url}"
main.actions.open_url = mock_open_url

print("--- STARTING TEST SEQUENCE ---")
main.main()
