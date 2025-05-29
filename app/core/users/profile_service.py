import uuid
from typing import Dict, Optional

class UserProfileService:
    def __init__(self):
        self._profiles: Dict[str, Dict] = {}
        self._device_mappings: Dict[str, str] = {}

    def create_profile(self, username: str, role: str) -> str:
        """Create a new user profile"""
        user_id = str(uuid.uuid4())
        self._profiles[user_id] = {
            "username": username,
            "role": role,
            "device_id": None
        }
        return user_id

    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by ID"""
        return self._profiles.get(user_id)

    def assign_device(self, user_id: str, device_id: str):
        """Assign a device to a user"""
        if user_id in self._profiles:
            self._profiles[user_id]["device_id"] = device_id
            self._device_mappings[device_id] = user_id

    def get_device_id(self) -> str:
        """Generate or get device ID"""
        return str(uuid.uuid4())

profile_service = UserProfileService()

def get_device_id() -> str:
    return profile_service.get_device_id()