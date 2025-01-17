import os
from dotenv import load_dotenv


load_dotenv()

def get_config(key: str, default=""):
    data = os.getenv(key)
    if data is None:
        return default
    return data

def set_config(key: str, value: str):
    os.environ[key] = value
    return os.environ[key]
