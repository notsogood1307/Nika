import sys
import sqlite3
import time
import msvcrt
import keyboard
import db
import memory
import brain
import voice_io

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
        
    print("\nNika is online. Type 'exit' to quit.")
    print("-" * 50)
    
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

            # Check if memory needs summarizing
            memory.summarize_if_needed()

            # Retrieve context
            facts = memory.get_all_facts()
            history = memory.get_recent_history(n=10)
            
            # Get Nika's response
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
