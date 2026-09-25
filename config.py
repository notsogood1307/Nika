import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required configuration variables
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
DATABASE_URL = os.getenv("DATABASE_URL")

# Optional Phase 2 configurations
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")

# Optional Phase 3 configurations
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "moondream")

# Validate that all required variables are set
missing_vars = []
if not API_KEY:
    missing_vars.append("API_KEY")
if not BASE_URL:
    missing_vars.append("BASE_URL")
if not MODEL_NAME:
    missing_vars.append("MODEL_NAME")
if not DATABASE_URL:
    missing_vars.append("DATABASE_URL")

if missing_vars:
    raise ValueError(f"Missing required environment variables in .env file: {', '.join(missing_vars)}")
