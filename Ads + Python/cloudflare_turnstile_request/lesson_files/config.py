
from dataclasses import dataclass
import os
import sys
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

logger.remove()
logger.add(
    sys.stdout,
    level='DEBUG',
    colorize=True,
    format='<light-cyan>{time:DD-MM HH:mm:ss}</light-cyan> | <level> {level: <3} </level><dim><white> {file}:{function}: {line}</white></dim>  - <light-white>{message}</light-white>'
)

@dataclass
class config:
    TWO_CAPTCHA_API_KEY = os.getenv('TWO_CAPTCHA_API_KEY')
    PROXY = os.getenv('PROXY')
    LINK_IP_CHANGE = os.getenv('LINK_IP_CHANGE')


