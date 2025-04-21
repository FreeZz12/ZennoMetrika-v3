
import os
from dotenv import load_dotenv
from dataclasses import dataclass
load_dotenv()

@dataclass
class config:
    TWO_CAPTCHA_API_KEY = os.getenv('TWO_CAPTCHA_API_KEY')
