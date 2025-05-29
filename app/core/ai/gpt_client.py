import os
from openai import OpenAI
from shared.config.env_loader import get_env_variable, is_test_env

class GPTClient:
    def __init__(self, agent="HyphaeOS", model="gpt-4"):
        """
        Initializes the GPT client with the appropriate API key and model.

        Args:
            agent (str): Logical agent name (used in logs)
            model (str): OpenAI model to use (default: gpt-4)
        """
        self.agent_name = agent
        self.model = model
        self.test_mode = is_test_env()

        if self.test_mode:
            print(f"⚠️ GPTClient initialized in test mode for {agent}")
            self.api_key = "test-key"
            self.client = None
        else:
            try:
                self.api_key = get_env_variable("OPENAI_API_KEY", optional=False)
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"❌ GPTClient init failed: {e}")
                self.client = None

    def ask(self, prompt, temperature=0.7, system_message=None, max_tokens=500):
        """
        Sends a prompt to OpenAI (or returns fallback in test mode).

        Args:
            prompt (str): User message
            temperature (float): Creativity level
            system_message (str): Optional system prompt
            max_tokens (int): Max output tokens

        Returns:
            str or None: Response string
        """
        if self.test_mode or self.client is None:
            return f"[TEST MODE] {self.agent_name} would reply to: '{prompt}'"

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ GPTClient[{self.agent_name}] failed: {e}")
            return None