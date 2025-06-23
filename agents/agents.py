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
from google.adk.models.lite_llm import LiteLlm # For multi-model support
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
print(f"Google API Key set: {'Yes' if os.environ.get('GOOGLE_API_KEY') else 'No (REPLACE PLACEHOLDER!)'}")

# Configure ADK to use API keys directly (not Vertex AI for this multi-model setup)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# %%
# --- Define Model Constants for easier use ---

# More supported models can be referenced here: https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_0_PRO = "gemini-2.5-pro-preview-05-06"


print("\nEnvironment configured.")
# %%
# Install required Google Cloud libraries
!pip install --quiet google-cloud-pubsub google-cloud-bigquery google-cloud-aiplatform

# %%
from google.cloud import pubsub_v1

project_id = "fraud-detection-adkhackathon"
topic_id = "transactions-topic"
subscription_id = "transactions-sub"

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()

topic_path = publisher.topic_path(project_id, topic_id)
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Create topic
try:
    publisher.create_topic(name=topic_path)
    print(f"Topic created: {topic_path}")
except Exception as e:
    print(f"Topic exists or error: {e}")

# Create subscription
try:
    subscriber.create_subscription(name=subscription_path, topic=topic_path)
    print(f"Subscription created: {subscription_path}")
except Exception as e:
    print(f"Subscription exists or error: {e}")

# %%
from google.cloud import aiplatform

aiplatform.init(project=project_id, location="us-central1")

# List existing models
models = aiplatform.Model.list()
print("Available models in Vertex AI:")
for model in models:
    print(model.display_name)

# %%
# import pandas as pd
# import json
# import time
# from google.cloud import pubsub_v1

# # CONFIG

# publisher = pubsub_v1.PublisherClient()
# topic_path = publisher.topic_path(project_id, topic_id)

# # Load dataset
# df = pd.read_csv('creditcard.csv')

# # Send each row as a message
# for index, row in df.iterrows():
#     transaction = {
#         'transaction_id': str(index),
#         'amount': row['Amount'],
#         'time': row['Time'],
#         'features': row.drop(['Amount', 'Time', 'Class']).to_dict(),
#         'label': int(row['Class'])  # fraud or not
#     }
#     message = json.dumps(transaction).encode('utf-8')
#     future = publisher.publish(topic_path, data=message)
#     print(f"Published transaction {index}, message ID: {future.result()}")
    
#     time.sleep(0.1)  # small delay to simulate streaming

# %%
import pandas as pd
import json
import time
from google.cloud import pubsub_v1

# CONFIG
project_id = "fraud-detection-adkhackathon"
topic_id = "transactions-topic"
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# ✅ Load your dataset
df = pd.read_csv("creditcard.csv")

# ✅ Mix 100 fraud + 100 non-fraud cases
fraud_df = df[df['Class'] == 1].sample(n=100, replace=True)
nonfraud_df = df[df['Class'] == 0].sample(n=100)
sample_df = pd.concat([fraud_df, nonfraud_df]).sample(frac=1).reset_index(drop=True)

# ✅ Publish sample data
for index, row in sample_df.iterrows():
    transaction = {
        "transaction_id": str(index),
        "amount": float(row["Amount"]),
        "country": "US",  # Add your own logic if needed
        "timestamp": time.time(),
        "label": int(row["Class"])
    }

    message = json.dumps(transaction).encode("utf-8")
    future = publisher.publish(topic_path, data=message)
    
    print(f"Published transaction {index}, label: {transaction['label']}")
    time.sleep(0.1)  # Optional: Simulate live traffic

# %%

# delete and recreate
from google.cloud import pubsub_v1

project_id = "fraud-detection-adkhackathon"
topic_id = "transactions-topic"
subscription_id = "transactions-sub"

subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()

subscription_path = subscriber.subscription_path(project_id, subscription_id)
topic_path = publisher.topic_path(project_id, topic_id)

# ✅ Delete the subscription (correct usage)
try:
    subscriber.delete_subscription(subscription=subscription_path)
    print(f"✅ Deleted subscription: {subscription_id}")
except Exception as e:
    print(f"⚠️ Could not delete subscription: {e}")

# ✅ Recreate the subscription
try:
    subscriber.create_subscription(name=subscription_path, topic=topic_path)
    print(f"✅ Recreated subscription: {subscription_id}")
except Exception as e:
    print(f"⚠️ Could not recreate subscription: {e}")
# %%
