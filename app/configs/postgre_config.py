from dataclasses import dataclass
from typing import Union

@dataclass
class PostgreConfig:
    host : str
    port : Union[str, int]
    database : str
    schema : str
    user : str
    password : str
    ssl_mode : str