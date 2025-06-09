from langgraph.graph import Graph
from openai import OpenAI

"""
Placeholder agent file for Week 1 setup.
"""

class BaseAgent:
    def __init__(self, name, agents=None, openai_api_key=None):
        self.name = name
        self.agents = agents or {}
        self.client = OpenAI(api_key=openai_api_key)

    def understand_intent(self, user_input):
        """
        Uses ChatGPT to classify the user input as either 'subsystem' or 'entire_scanner'.
        """
        prompt = (
            "Classify the following user request as either 'subsystem' or 'entire_scanner'. "
            "Respond with only one of these two words.\n\n"
            f"User input: {user_input}\nClassification:"
        )
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1,
            temperature=0
        )
        classification = response.choices[0].message.content.strip().lower()
        return classification

    def route_request(self, user_input):
        """
        Routes the user input to the appropriate agent based on intent.
        """
        intent = self.understand_intent(user_input)
        agent = self.agents.get(intent)
        if intent == "subsystem" and "subsystem" in self.agents:
            return self.agents["subsystem"].handle(user_input)
        elif intent == "entire_scanner" and "scanner" in self.agents:
            return self.agents["scanner"].handle("Design the whole MR scanner: " + user_input)
        else:
            return f"No agent found for intent: {intent}"

    def handle(self, user_input):
        """
        Entry point for handling user input.
        """
        return self.route_request(user_input)
