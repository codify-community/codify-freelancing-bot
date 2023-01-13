import os

from dotenv import load_dotenv

load_dotenv()

config = {
    'token' : os.getenv('token_bot'),
    'base_url' : os.getenv('base_url')
}   