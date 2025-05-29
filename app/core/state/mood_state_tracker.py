from typing import Dict
import threading

class MoodStateTracker:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_tracker()
            return cls._instance

    def _init_tracker(self):
        self._user_moods: Dict[str, str] = {}

    def set_mood(self, user_id: str, mood: str):
        self._user_moods[user_id] = mood

    def get_mood(self, user_id: str) -> str:
        return self._user_moods.get(user_id, "neutral")

    def clear_mood(self, user_id: str):
        self._user_moods.pop(user_id, None)

mood_tracker = MoodStateTracker()

def get_user_mood(user_id: str) -> str:
    return mood_tracker.get_mood(user_id)

def set_user_mood(user_id: str, mood: str):
    mood_tracker.set_mood(user_id, mood)