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
