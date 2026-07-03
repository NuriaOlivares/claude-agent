from dotenv import load_dotenv
load_dotenv()

import os
from anthropic import Anthropic

api_key = os.environ.get("ANTHROPIC_API_KEY", "")

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY is not set. Check your .env file.")

client = Anthropic(api_key=api_key)


def ask_claude(system_prompt: str, user_message: str) -> str:
    """
    Send a message to Claude and return its response as a string.
    
    system_prompt: the instructions that define Claude's role and rules
    user_message: the actual content we want Claude to analyze
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    return message.content[0].text


if __name__ == "__main__":
    response = ask_claude(
        system_prompt="You are a helpful assistant.",
        user_message="Say hello in one sentence."
    )
    print(response)