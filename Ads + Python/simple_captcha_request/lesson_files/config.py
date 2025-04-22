
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class config:
    TWO_CAPTCHA_API_KEY: str = os.getenv('TWO_CAPTCHA_API_KEY')
