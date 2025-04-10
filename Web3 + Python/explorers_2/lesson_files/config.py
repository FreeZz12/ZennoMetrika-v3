import os
 
from dotenv import load_dotenv

load_dotenv()

class Config:
    ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')

config = Config()
