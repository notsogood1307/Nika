import sqlite3

def migrate():
    conn = sqlite3.connect('nika_memory.db')
    cursor = conn.cursor()
    
    # 1. Fetch all summary rows
    cursor.execute("SELECT id, value FROM facts WHERE key IN ('Conversation Summary', 'conversation_summary') ORDER BY created_at ASC")
    rows = cursor.fetchall()
    
    if not rows:
        print("No summaries found. Nothing to migrate.")
        return
        
    print(f"Found {len(rows)} existing summary row(s).")
    
    # The most recent one is the last in the chronological list, 
    # but the prompt says they were 'accumulating'. 
    # Usually the latest one has the most recent information, 
    # or they might be disconnected.
    # The user says: "keeping only the most recent one's content merged forward if reasonably possible, or just keep the single most recent one if merging is impractical"
    # Given the previous logic was just summarizing isolated batches of 40 messages, 
    # the existing summaries are disjoint. Merging them forward is just concatenating them.
    
    merged_summary = "\n\n".join([row[1] for row in rows])
    
    # Delete all old summary rows
    cursor.execute("DELETE FROM facts WHERE key IN ('Conversation Summary', 'conversation_summary')")
    print("Deleted old summary rows.")
    
    # Insert the merged summary under the new standard key
    cursor.execute("INSERT INTO facts (key, value) VALUES (?, ?)", ("conversation_summary", merged_summary))
    print("Inserted merged summary as 'conversation_summary'.")
    
    conn.commit()
    conn.close()
    
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
