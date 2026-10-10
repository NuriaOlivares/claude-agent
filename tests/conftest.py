import sys
import os

# Without this, pytest cannot find claude_client, github_client, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))