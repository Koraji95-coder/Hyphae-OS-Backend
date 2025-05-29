import json, os

# 🔐 RBAC role loader from JSON config
ROLES_FILE = os.path.join(os.path.dirname(__file__), "roles.json")

def load_roles():
    try:
        with open(ROLES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

ROLE_MAP = load_roles()

def get_user_role(email: str) -> str:
    return ROLE_MAP.get(email, "guest")  # default to guest

def is_authorized(email: str, required_role: str) -> bool:
    roles = ["guest", "user", "admin", "owner"]
    user_rank = roles.index(get_user_role(email)) if get_user_role(email) in roles else 0
    required_rank = roles.index(required_role)
    return user_rank >= required_rank
