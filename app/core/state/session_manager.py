import os
import getpass
from backend.app.shared.users.user_identity import UserIdentity

class SessionManager:
    """
    Tracks user session metadata including profile, context flags, memory, and role identity.
    Designed as a singleton used across the app.
    """

    def __init__(self):
        self._context = {}     # Arbitrary runtime flags (e.g., feature toggles, state)
        self._profile = {}     # Dict-based user profile
        self._memory = {}      # Transient in-session memory, if needed
        self.user_identity = UserIdentity()  # Handles role resolution

    # === Profile Handling ===

    def set_user_profile(self, profile: dict):
        """
        Set the session's user profile. Example keys: name, device_id, email.
        """
        self._profile = profile
        self._context["username"] = profile.get("name", "unknown")

    def get_user_profile(self) -> dict:
        """
        Returns the full user profile dictionary.
        """
        return self._profile

    def get_user_name(self) -> str:
        """
        Retrieves the current username from profile, env, or system.
        """
        return (
            self._profile.get("name")
            or os.environ.get("USER")
            or getpass.getuser()
            or "member"
        )

    def get_user_role(self) -> str:
        """
        Resolves the user's role via the identity service.
        """
        return self.user_identity.get_role(self.get_user_name())

    # === Runtime Flags ===

    def get_flag(self, key: str):
        """
        Retrieve a temporary flag from session context.
        """
        return self._context.get(key)

    def set_flag(self, key: str, value):
        """
        Set a custom runtime flag.
        """
        self._context[key] = value

    # === Accessors ===

    def get_context(self) -> dict:
        """
        Get raw context flags dictionary.
        """
        return self._context

    def get_memory(self) -> dict:
        """
        Get in-session memory dictionary.
        """
        return self._memory

# === Global Singleton Instance ===
session = SessionManager()