import json
import os
from werkzeug.security import generate_password_hash

OUTPUT_PATH = os.path.join("app", "config", "admins.json")

admins = [
    {
        "email": "admin1@example.com",
        "password": generate_password_hash("123456"),
        "name": "Super Admin",
        "role": "ADMIN"
    },
    {
        "email": "admin2@example.com",
        "password": generate_password_hash("123456"),
        "name": "System Admin",
        "role": "ADMIN"
    }
]

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

with open(OUTPUT_PATH, "w") as f:
    json.dump(admins, f, indent=4)