import os
from dotenv import load_dotenv

load_dotenv()

# --- API keys / credentials ---
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

# Google Drive credentials
DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")

# --- Image processing specs ---
TARGET_WIDTH = 1800
TARGET_HEIGHT = 1200
MAX_FILE_SIZE_MB = 10
JPEG_QUALITY_START = 90  

# --- Search / quality gate ---
CANDIDATES_PER_ITEM = 5       
QUALITY_SCORE_THRESHOLD = 6   

# Now pointing to our local Ollama model!
VISION_MODEL = "moondream"  

# --- Local working dirs ---
RAW_DIR = "downloads/raw"
PROCESSED_DIR = "downloads/processed"
REPORT_PATH = "output_report.xlsx"

for d in (RAW_DIR, PROCESSED_DIR):
    os.makedirs(d, exist_ok=True)