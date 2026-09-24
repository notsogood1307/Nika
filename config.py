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
VISION_MODEL_NAME = os.getenv("VISION_MODEL_NAME", "gemini-3.6-flash")
VISION_API_KEY = os.getenv("VISION_API_KEY", API_KEY)
VISION_BASE_URL = os.getenv("VISION_BASE_URL", BASE_URL)

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
