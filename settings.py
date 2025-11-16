import os
from dotenv import load_dotenv

load_dotenv()
MANAGER_CHAT_ID = int(os.getenv('MANAGER_CHAT_ID', 0))