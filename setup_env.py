import json
import os

try:
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]
except KeyError:
    print(os.environ)

with open("env", "w") as f:
    json.dump({"username": username, "password": password}, f)
