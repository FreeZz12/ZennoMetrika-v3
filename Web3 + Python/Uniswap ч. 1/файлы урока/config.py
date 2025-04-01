import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    private_key = os.getenv('PK')

config = Config()