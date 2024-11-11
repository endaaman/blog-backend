import os
from dotenv import load_dotenv

load_dotenv()

BLOG_DATA_DIR = os.getenv('BLOG_DATA_DIR', './data')
CF_API_TOKEN = os.getenv('CF_API_TOKEN', '')
APP_ENV= os.getenv('APP_ENV', 'dev')
