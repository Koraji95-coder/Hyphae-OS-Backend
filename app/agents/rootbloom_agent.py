"""RootbloomAgent 🌸
────────────────────────────────────────────
Journaling + scheduling assistant.
Emotionally intelligent personal aide.
"""

from backend.app.agents.base_llm_agent import BaseLLMAgent
from backend.app.agents.mycocore_agent import MycoCore
from backend.app.core.utils.ai_helpers import truncate_text, extract_json_from_response


class RootbloomAgent(BaseLLMAgent):
    def __init__(self):
        super().__init__(agent_name="Rootbloom")
        self.core = MycoCore()

    def ask(self, prompt: str) -> str:
        if not self.core.is_safe():
            return "🌸 Rootbloom is offline. Safe mode is active."
        return self.handle_prompt(prompt)

    def respond(self, input_text: str) -> str:
        return f"📅 Rootbloom says: '{input_text}' — added to your life log."
