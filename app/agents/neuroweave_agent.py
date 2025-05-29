"""NeuroweaveAgent 🧠
────────────────────────────────────────────
LLM-based predictive financial and market analyst.

This agent specializes in:
- Stock market trend analysis and prediction
- Pattern recognition in financial data
- Memory-based insight building over time
- Market signal processing and interpretation
- Risk assessment and opportunity identification

NeuroweaveAgent combines LLM capabilities with financial
domain knowledge to provide predictive insights.
"""

from backend.app.agents.base_llm_agent import BaseLLMAgent
from backend.app.agents.mycocore_agent import MycoCore
from backend.app.core.utils.ai_helpers import truncate_text, extract_json_from_response
from backend.app.core.memory.memory_router import MemoryRouter
from backend.app.core.ai.mood_engine import detect_mood
from backend.app.agent_features.financial_report import generate_prediction_report



class NeuroweaveAgent(BaseLLMAgent):
    """LLM-based predictive market analysis agent.
    
    This agent specializes in financial market analysis and prediction,
    building insights from historical data and user interactions.
    
    Attributes:
        Inherits all attributes from BaseLLMAgent
        prediction_history (List): History of previous predictions
        confidence_metrics (Dict): Metrics on prediction accuracy
    """
    def __init__(self):
        super().__init__(agent_name="Neuroweave")
        self.core = MycoCore()
        self.memory = MemoryRouter(mode="redis", encrypt=True)  # 🔐 Encrypted Redis memory

    def ask(self, prompt: str, pdf_text: Optional[str] = None) -> str:
        """Process a user question about market predictions.
        
        Args:
            prompt (str): User's market analysis question
            
        Returns:
            str: Generated prediction or analysis
        """
        if not self.core.is_safe():
            return "System is locked. Safe mode enabled."

        # Combine PDF text (if any) with prompt
        if pdf_text:
            prompt = f"{pdf_text}\n\n---\n\n{prompt}"

        mood = detect_mood(prompt)  # calls mood_engine
        self.memory.store_interaction(agent=self.agent_name, user=self.user, prompt=prompt, mood=mood)

        raw_response = self.handle_prompt(prompt)

        self.memory.store_response(agent=self.agent_name, user=self.user, response=raw_response)

        # Optionally wrap as PDF market report
        if "generate report" in prompt.lower():
            tickers, summaries = extract_from_response(raw_response)
            return generate_prediction_report(tickers, summaries, user=self.user)

        return raw_response

    def respond(self, input_text: str) -> str:
        """Provide a simple acknowledgment response.
        
        Args:
            input_text (str): User's input text
            
        Returns:
            str: Acknowledgment message
        """
        return f"🧠 Neuroweave acknowledges: '{input_text}' — processing signal..."
