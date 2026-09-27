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

## Phase 3: Screen Perception and Action Grounding with Photon (Moondream)

Nika can now look at your screen and interact with specific elements using a local vision model via Photon! This keeps your screen data completely private and doesn't require any separate server to run.

1. Ensure you have installed the required dependencies, which now includes `moondream`.
2. When you run Nika, the Moondream vision model will be loaded in-process automatically. There is no separate service to start before running `main.py`!

Because the model runs locally, the first time you ask Nika to look at your screen or click on an element, it may take a moment to initialize on your GPU.

## Phase 4: Local Actions and Guardrails

Nika can now take real actions on your PC! To keep you safe, this operates under strict limits:
- **Global Kill Switch:** Press **Ctrl+Shift+Esc** at any time to instantly cancel an ongoing action sequence.
- **Whitelist Only:** The `open_app` action can *only* launch commands explicitly allowed in `actions.py`. The defaults are `notepad`, `calculator`, and `browser`.

Action requests are routed through a 3-tier risk system:
- **Tier 1 (Safe):** Executes immediately (e.g., opening an app).
- **Tier 2 (Moderate):** Requires user confirmation the first time. You can say "always allow" to skip the prompt for the rest of the session (e.g., typing text, opening URLs).
- **Tier 3 (High):** Requires explicit confirmation *every single time*. You cannot "always allow" these (e.g., pressing key combinations like Enter or Ctrl+S).
