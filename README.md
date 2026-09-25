# Nika - Personal AI Assistant (Phase 1)

This is Phase 1 of the Nika project: a text-only chat loop with a persistent memory system backed by PostgreSQL.

## Prerequisites

- Python 3.10+
- PostgreSQL server running locally

## Database Setup

1. Open your PostgreSQL command line tool (e.g., `psql` or pgAdmin).
2. Run the following commands to create the database and user:

```sql
CREATE DATABASE nika_memory;
CREATE USER nika WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE nika_memory TO nika;
-- For PostgreSQL 15+, you may also need to grant schema usage:
-- \c nika_memory
-- GRANT ALL ON SCHEMA public TO nika;
```

*(Note: Change the password if you prefer, and update the `DATABASE_URL` in `.env` accordingly).*

## Configuration

1. Copy `.env.example` to a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your API key and other details.
   - **Gemini (Google AI Studio)**: Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey).
   - **Groq**: Get a free key at [console.groq.com](https://console.groq.com/keys). (Uncomment the Groq section in `.env`).
   - **NVIDIA NIM**: Get a free key at [build.nvidia.com](https://build.nvidia.com). (Uncomment the NIM section in `.env`).

## Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Running Nika

Start the interactive chat loop:

```bash
python main.py
```

The application will automatically create the necessary database tables (`facts` and `conversation_log`) on startup if they don't already exist.

Type `exit` during the chat loop to gracefully quit.

## Phase 2: Voice Input/Output

Phase 2 adds push-to-talk voice input and spoken output. 

**Note on Windows:** The `keyboard` library is used to detect the hotkey (Spacebar) globally. You may need to run the script as Administrator on Windows for the hotkey detection to work properly.
**Note on Whisper:** On the first run, the `faster-whisper` model will be downloaded automatically. This is a one-time delay.

## Phase 3: Screen Perception with Ollama

Nika can now look at your screen using a local vision model! This keeps your screen data completely private.
1. Install [Ollama](https://ollama.com/) and make sure it is running (it usually starts automatically as a background service).
2. Pull the default vision model by running: `ollama pull moondream` (or update `OLLAMA_VISION_MODEL` in your `.env` to use another vision model).

If Ollama is not running, normal text and voice conversations will still work seamlessly without interruption.
