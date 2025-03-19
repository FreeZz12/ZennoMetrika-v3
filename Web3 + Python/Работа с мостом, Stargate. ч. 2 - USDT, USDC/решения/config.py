import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    private_key = os.getenv('PK')
    ankr_api_key = os.getenv('ANKR_API_KEY')

config = Config()