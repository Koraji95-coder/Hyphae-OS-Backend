"""BaseLLMAgent 🧠
────────────────────────────────────────────
Shared GPT/memory/mood logic for all agents.
"""

from shared.ai.gpt_client import GPTClient
from shared.state.session_manager import session
from shared.state.mood_state_tracker import get_user_mood, set_user_mood
from shared.memory.memory_router import MemoryRouter
from shared.ai.mood_engine import detect_mood, mood_wrapped_prompt
from backend.app.core.utils.logger import get_logger
from backend.app.core.utils.ai_helpers import truncate_text, extract_json_from_response

from backend.app.agents.mycocore_agent import Mycocore



class BaseLLMAgent:
    def __init__(self, agent_name: str):
        self.name = agent_name
        self.username = session.get_user_name()
        self.role = session.get_user_role()
        self.device_id = session.get_user_profile().get("device_id", "unknown")
        self.memory = MemoryRouter(mode=os.getenv("MEMORY_MODE", "sql"), encrypt=encrypt_memory)
        self.gpt = GPTClient(agent=agent_name)
        

        # ✅ Injected core dependencies
        self.logger = get_logger(agent_name)
        self.session = session
        self.core = Mycocore()

    def handle_prompt(self, prompt: str) -> str:
        """Handles GPT logic w/ mood + memory context."""
        # Store the prompt in memory

        # Get response from GPT
        reply = self.gpt.ask(wrapped_prompt)

        # Store the response in memory
        self.memory.store_response(
            agent=self.name,
            user=self.username,
            response=reply
        )
        try:
            mood = detect_mood(prompt)
            set_user_mood(self.username, mood)
            wrapped_prompt = mood_wrapped_prompt(prompt, mood)
            self.logger.info(f"[{self.name}] Prompt mood: {mood}; Wrapped: {wrapped_prompt}")
            reply = self.gpt.ask(wrapped_prompt)
            return reply
        except Exception as e:
            self.logger.error(f"[{self.name}] Error during GPT ask: {e}")
            return f"⚠️ Error generating reply: {e}"