from dotenv import load_dotenv 
import os


load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

GITHUB_API_BASE = "https://api.github.com"