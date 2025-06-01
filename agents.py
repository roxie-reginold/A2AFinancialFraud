# %%
# @title Step 0: Setup and Installation
# Install ADK and LiteLLM for multi-model support

!pip install google-adk -q
!pip install litellm -q

print("Installation complete.")
# %%
# @title Import necessary libraries
import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm # For multi-model support (Commented out as litellm was not installed and to debug syntax error)
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")

# %%
# @title Configure API Keys (Replace with your actual keys!)
load_dotenv()
# --- IMPORTANT: Replace placeholders with your real API keys ---

# Gemini API Key (Get from Google AI Studio: https://aistudio.google.com/app/apikey)


# --- Verify Keys (Optional Check) ---
print("API Keys Set:")
print(f"Google API Key set: {'Yes' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'YOUR_GOOGLE_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")

# Configure ADK to use API keys directly (not Vertex AI for this multi-model setup)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# %%
