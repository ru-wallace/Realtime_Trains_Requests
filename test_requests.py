import requests
import os

from dotenv import load_dotenv

load_dotenv("./environment/.env")

username = os.environ.get("USER")
password = os.environ.get("PASSWORD")

print(username)
session = requests.Session()

session.auth = (username,password)

response = session.get("https://api.rtt.io/api/v1/json/search/bdg")

print(response.content)

