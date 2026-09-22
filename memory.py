import db
import brain

def add_fact(key: str, value: str):
    """Adds a new durable fact to the database."""
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO facts (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()

def get_all_facts() -> str:
    """Retrieves all facts formatted as a single string context."""
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT key, value FROM facts ORDER BY created_at ASC")
        rows = cursor.fetchall()
        
    if not rows:
        return ""
        
    facts = []
    for row in rows:
        facts.append(f"- {row[0]}: {row[1]}")
    return "\n".join(facts)

def log_message(role: str, content: str):
    """Logs a single conversational turn into the raw history."""
    with db.get_connection() as conn:
        conn.execute(
            "INSERT INTO conversation_log (role, content) VALUES (?, ?)",
            (role, content)
        )
        conn.commit()

def get_recent_history(n: int = 10) -> list:
    """
    Returns the last `n` turns from the conversation history in chronological order.
    Returns a list of tuples: [(role, content), ...]
    """
    with db.get_connection() as conn:
        # Fetch the latest n messages, then reverse them to be in chronological order
        cursor = conn.execute(
            "SELECT role, content FROM conversation_log ORDER BY timestamp DESC LIMIT ?",
            (n,)
        )
        rows = cursor.fetchall()
        
    # Reverse to chronological order (oldest to newest among the recent set)
    rows.reverse()
    return rows

def summarize_if_needed():
    """
    Checks if the conversation log has grown too large.
    If so, calls the LLM to summarize older messages into a fact, and trims the log.
    """
    THRESHOLD = 50
    TRIM_TO = 10
    
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM conversation_log")
        count = cursor.fetchone()[0]
        
        if count > THRESHOLD:
            # Fetch the messages to summarize (all except the most recent ones we want to keep)
            messages_to_summarize = count - TRIM_TO
            cursor = conn.execute(
                "SELECT role, content FROM conversation_log ORDER BY timestamp ASC LIMIT ?",
                (messages_to_summarize,)
            )
            old_messages = cursor.fetchall()
            
            # Prepare transcript for summarization
            transcript = []
            for role, content in old_messages:
                transcript.append(f"{role.capitalize()}: {content}")
            transcript_text = "\n".join(transcript)
            
            # Use the brain to summarize
            prompt = (
                "Please summarize the following conversation history briefly. "
                "Focus on important facts, preferences, or ongoing context that should be remembered.\n\n"
                f"{transcript_text}"
            )
            
            # Call a simple LLM completion without context just for this summary
            # Alternatively, we could reuse the get_response, but we just need a direct answer here.
            try:
                response = brain.client.chat.completions.create(
                    model=brain.config.MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes conversations concisely."},
                        {"role": "user", "content": prompt}
                    ]
                )
                summary_text = response.choices[0].message.content
                
                # Store the summary as a fact
                conn.execute(
                    "INSERT INTO facts (key, value) VALUES (?, ?)",
                    ("Conversation Summary", summary_text)
                )
                
                # Delete the summarized messages
                # Find the timestamp of the last message we summarized
                cursor = conn.execute(
                    "SELECT timestamp FROM conversation_log ORDER BY timestamp ASC LIMIT 1 OFFSET ?",
                    (messages_to_summarize - 1,)
                )
                cutoff_time = cursor.fetchone()[0]
                
                conn.execute(
                    "DELETE FROM conversation_log WHERE timestamp <= ?",
                    (cutoff_time,)
                )
                
                conn.commit()
                print("[System] Memory summarized and trimmed.")
            except Exception as e:
                print(f"[System] Failed to summarize memory: {e}")
