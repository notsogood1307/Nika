import memory
import time
import db

def test_ordering():
    # Insert messages very rapidly to ensure they hit the same timestamp (second resolution)
    # in SQLite's CURRENT_TIMESTAMP
    
    # 1. Clear the table for clean testing
    with db.get_connection() as conn:
        conn.execute("DELETE FROM conversation_log")
        conn.commit()
    
    # 2. Insert user message and assistant reply rapidly
    memory.log_message("user", "Open Notepad")
    memory.log_message("assistant", "Notepad is open!")
    
    memory.log_message("user", "Type hello")
    memory.log_message("assistant", "Typed hello!")
    
    # 3. Retrieve history
    history = memory.get_recent_history()
    
    print("--- Retrieved History ---")
    for role, content in history:
        print(f"{role}: {content}")
        
    print("\nExpected order:")
    print("user: Open Notepad")
    print("assistant: Notepad is open!")
    print("user: Type hello")
    print("assistant: Typed hello!")

if __name__ == '__main__':
    test_ordering()
