"""SporelinkAgent 🛰️
────────────────────────────────────────────
Market/news intelligence fetcher and tagger.
Future: Real-time sentiment & stock linking.
"""

from backend.app.agents.base_llm_agent import BaseLLMAgent
from backend.app.agents.mycocore_agent import MycoCore
from backend.app.core.utils.ai_helpers import truncate_text, extract_json_from_response

class SporelinkAgent(BaseLLMAgent):
    def __init__(self):
        super().__init__(agent_name="Sporelink")
        self.core = MycoCore()

    def ask(self, prompt: str) -> str:
        if not self.core.is_safe():
            return "🛰️ Sporelink disabled in safe mode."
        return self.handle_prompt(prompt)


    def fetch_news(self):
        return "[WIP] Fetching headlines from NewsAPI..."

    def respond(self, input_text: str) -> str:
        return f"📡 Sporelink acknowledges: '{input_text}'"
