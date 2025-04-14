from dataclasses import dataclass
from keyring import get_password

@dataclass
class settings:
    ankr_api_key: str = get_password("ankr", "key")


