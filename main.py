import sys
import sqlite3
import time
import msvcrt
import keyboard
import urllib.request
import json
import re
import config
import db
import memory
import brain
import voice_io
import screen_capture

def get_mixed_input():
    print("\nHold [SPACE] to talk, or just type and press Enter, or type 'exit' to quit.")
    print("You: ", end="", flush=True)
    
    typed_chars = []
    
    while True:
        if keyboard.is_pressed('space'):
            time.sleep(0.3)
            if keyboard.is_pressed('space'):
                # It's a hold! Voice mode
                print("\r" + " " * 80 + "\r", end="", flush=True)
                audio_path = voice_io.record_audio()
                text = voice_io.transcribe(audio_path)
                print(f"You (Voice): {text}")
                
                # Drain stdin of any spaces that were buffered during hold
                while msvcrt.kbhit():
                    msvcrt.getwch()
                return text
        
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            if char in ('\r', '\n'):
                print()
                return "".join(typed_chars).strip()
            elif char == '\x08': # Backspace
                if typed_chars:
                    typed_chars.pop()
                    print("\b \b", end="", flush=True)
            elif char == '\x00' or char == '\xe0': # Special keys
                msvcrt.getwch()
            else:
                typed_chars.append(char)
                print(char, end="", flush=True)
                
        time.sleep(0.01)

def main():
    print("Initializing Nika...")
    
    # Attempt to initialize the database
    try:
        db.init_db()
        print("Database connected and verified.")
    except sqlite3.OperationalError as e:
        print(f"Error: Cannot reach the SQLite database.\nDetails: {e}")
        print("Please check your DATABASE_URL in the .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected database error: {e}")
        sys.exit(1)
        
    print("Checking for local Ollama vision model...")
    base_url = config.OLLAMA_BASE_URL.replace("/v1", "")
    tags_url = f"{base_url}/api/tags"
    try:
        req = urllib.request.Request(tags_url)
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = [m.get("name") for m in data.get("models", [])]
            target_model = config.OLLAMA_VISION_MODEL
            if target_model not in models and f"{target_model}:latest" not in models:
                print(f"Warning: Ollama is running, but the model '{target_model}' isn't pulled.")
                print(f"Suggestion: Run 'ollama pull {target_model}' to enable screen perception.")
    except Exception:
        print("Warning: Ollama doesn't seem to be running — screen perception won't work until it's started.")

    print("\nNika is online. Type 'exit' to quit.")
    print("-" * 50)
    
    default_monitor = 1
    
    while True:
        try:
            # Read user input
            user_input = get_mixed_input()
            
            # Check for exit command
            if user_input.lower() in ('exit', 'quit'):
                print("Nika: See ya later!")
                break
                
            if not user_input:
                continue

            user_input_lower = user_input.lower()
            
            # Check for diagnostic monitor listing command
            if any(phrase in user_input_lower for phrase in ["how many monitors", "list my monitors", "show my monitors", "what monitors", "monitors do i have"]):
                monitors = screen_capture.list_monitors()
                print(f"\nNika: You have {len(monitors)} monitor(s):")
                for m in monitors:
                    print(f"  - Monitor {m['index']}: {m['width']}x{m['height']}")
                voice_io.speak(f"You have {len(monitors)} monitor{'s' if len(monitors) != 1 else ''}.")
                continue

            # Check for local monitor switching command
            switch_match = re.search(r'(?:switch|change|use)(?:\s+(?:to|2|two))?\s+monitor\s+(\d+)', user_input_lower)
            if not switch_match:
                # Also try matching just "2 monitor X" as a typo for "to monitor X"
                switch_match = re.search(r'(?:to|2|two)\s+monitor\s+(\d+)', user_input_lower)

            if switch_match:
                default_monitor = int(switch_match.group(1))
                print(f"\nNika: Switched to monitor {default_monitor}.")
                voice_io.speak(f"Switched to monitor {default_monitor}.")
                continue
            elif any(phrase in user_input_lower for phrase in ["use my second monitor", "use my other screen", "switch monitor"]):
                default_monitor = 2
                print(f"\nNika: Switched to monitor {default_monitor}.")
                voice_io.speak(f"Switched to monitor {default_monitor}.")
                continue

            # Check if memory needs summarizing
            memory.summarize_if_needed()

            # Retrieve context
            facts = memory.get_all_facts()
            history = memory.get_recent_history(n=10)
            
            # Get Nika's response based on keywords
            vision_keywords = [
                "look at my screen", "what's on my screen", "what do you see", 
                "look at monitor", "what's on monitor", "look at my second monitor", 
                "what's on my second monitor", "look at my other screen"
            ]
            
            if any(kw in user_input_lower for kw in vision_keywords):
                inline_monitor_match = re.search(r'monitor\s*(\d+)', user_input_lower)
                if inline_monitor_match:
                    target_monitor = int(inline_monitor_match.group(1))
                elif any(phrase in user_input_lower for phrase in ["second monitor", "second screen", "other screen"]):
                    target_monitor = 2
                else:
                    target_monitor = default_monitor
                    
                print(f"[Looking at your monitor {target_monitor}...]")
                try:
                    screenshot_b64 = screen_capture.capture_screen(monitor_index=target_monitor)
                    response = brain.get_response_with_screen(user_input, facts, history, screenshot_b64)
                except Exception as e:
                    response = f"I tried to look at monitor {target_monitor}, but ran into an issue: {e}"
            else:
                response = brain.get_response(user_input, facts, history)
            
            # Print and speak response
            print(f"\nNika: {response}")
            voice_io.speak(response)
            
            # Log the conversation
            memory.log_message("user", user_input)
            memory.log_message("assistant", response)
            
        except KeyboardInterrupt:
            print("\nNika: See ya later!")
            break
        except Exception as e:
            print(f"\n[System Error] Something went wrong in the loop: {e}")

if __name__ == "__main__":
    main()
