from openai import OpenAI
from agents import Agent

class AI_Agent:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.agent = Agent(
            name="Des",
            instructions="You are a helpful assistant",
            model="gpt-4o-mini"
        )

    def ask(self, message):
        """Invia un messaggio all'AI e ottiene una risposta."""
        try:
            # Utilizzo dell'Agent SDK
            response = self.agent.run(message)
            return response
        except Exception as e:
            # Fallback all'API standard di OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": message}],
                max_tokens=150
            )
            return response.choices[0].message.content