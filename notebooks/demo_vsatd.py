import sys
from agents.base_agent import BaseAgent

if __name__ == "__main__":
    user_text = input("Enter text for BaseAgent: ")
    agent = BaseAgent(user_text)
    print(f"BaseAgent created with: {user_text}")
