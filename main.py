import sys
import sqlite3
import db
import memory
import brain

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
            user_input = input("\nYou: ").strip()
            
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
            
            # Print response
            print(f"\nNika: {response}")
            
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
