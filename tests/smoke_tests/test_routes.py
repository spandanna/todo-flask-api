import os

from dotenv import load_dotenv

load_dotenv()

api_url = os.getenv("API_URL") + "/v1"
