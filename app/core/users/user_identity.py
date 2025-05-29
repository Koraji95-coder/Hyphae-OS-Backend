import json
import os

ROLES_PATH = os.path.join(os.path.dirname(__file__), "roles.json")

class UserIdentity:
    def __init__(self):
        try:
            with open(ROLES_PATH, "r") as f:
                self.roles = json.load(f)
        except Exception:
            self.roles = {}

    def get_role(self, username):
        return self.roles.get(username.lower(), "sporeling")
