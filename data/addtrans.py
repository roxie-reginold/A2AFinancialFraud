# %%
from google.cloud import bigquery

project_id = "fraud-detection-adkhackathon"
dataset_id = "fraud_data"
table_id = "transactions"

client = bigquery.Client()
dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")

# Create dataset if it doesn't exist
try:
    client.get_dataset(dataset_ref)
    print(f"✅ Dataset exists: {dataset_id}")
except:
    client.create_dataset(dataset_ref)
    print(f"✅ Created dataset: {dataset_id}")

# Define full table path and schema
full_table_id = f"{project_id}.{dataset_id}.{table_id}"
schema = [
    bigquery.SchemaField("transaction_id", "STRING"),
    bigquery.SchemaField("amount", "FLOAT"),
    bigquery.SchemaField("country", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("risk_score", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("flagged", "BOOLEAN"),
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
]

# Create table if it doesn't exist
try:
    client.get_table(full_table_id)
    print(f"✅ Table exists: {full_table_id}")
except:
    table = bigquery.Table(full_table_id, schema=schema)
    client.create_table(table)
    print(f"✅ Created table: {full_table_id}")

# %%
import pandas as pd
import json
import time
from tqdm import tqdm
from google.cloud import pubsub_v1, bigquery

# --- CONFIGURATION ---
project_id = "fraud-detection-adkhackathon"
topic_id = "transactions-topic"
table_id = "fraud-detection-adkhackathon.fraud_data.transactions"

# Initialize clients
publisher = pubsub_v1.PublisherClient()
bq_client = bigquery.Client()
topic_path = publisher.topic_path(project_id, topic_id)

# --- LOAD DATA ---
df = pd.read_csv("creditcard.csv")

# Balanced sample: 100 fraud, 100 non-fraud
fraud_df = df[df['Class'] == 1].sample(n=100, replace=True, random_state=42)
nonfraud_df = df[df['Class'] == 0].sample(n=100, random_state=42)
sample_df = pd.concat([fraud_df, nonfraud_df]).sample(frac=1, random_state=42).reset_index(drop=True)

# --- LOOP TO PUBLISH + STORE ---
for index, row in tqdm(sample_df.iterrows(), total=sample_df.shape[0]):
    timestamp = time.time()
    transaction = {
        "transaction_id": str(index),
        "amount": float(row["Amount"]),
        "timestamp": timestamp,
        "label": int(row["Class"])
    }

    # Publish to Pub/Sub
    message = json.dumps(transaction).encode("utf-8")
    future = publisher.publish(topic_path, data=message)
    future.result()  # Wait for publish to complete

    # Insert into BigQuery
    row_to_insert = {
        "transaction_id": transaction["transaction_id"],
        "amount": transaction["amount"],
        "country": None,
        "risk_score": None,
        "flagged": bool(transaction["label"]),
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(timestamp))
    }

    errors = bq_client.insert_rows_json(table_id, [row_to_insert])
    if errors:
        print(f"❌ BigQuery insert error at row {index}: {errors}")
    else:
        print(f"✅ Row {index} published + inserted")

    time.sleep(0.1)  # Optional: simulate streaming delay

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv("creditcard.csv")

# 1. Class Distribution
print("✅ Class Distribution:")
print(df['Class'].value_counts())
print()

# 2. Average Transaction Amounts
print("✅ Average Amounts:")
print("Fraudulent:", round(df[df['Class'] == 1]['Amount'].mean(), 2))
print("Non-Fraudulent:", round(df[df['Class'] == 0]['Amount'].mean(), 2))
print()

# 3. Amount Distribution Plot
plt.figure(figsize=(10, 5))
sns.histplot(df[df['Class'] == 0]['Amount'], bins=50, label='Non-Fraud', color='blue', kde=True)
sns.histplot(df[df['Class'] == 1]['Amount'], bins=50, label='Fraud', color='red', kde=True)
plt.legend()
plt.title('Distribution of Transaction Amounts')
plt.xlabel('Amount')
plt.ylabel('Frequency')
plt.show()

# 4. Feature Correlation with Class
corr_matrix = df.corr()
class_corr = corr_matrix['Class'].drop('Class').sort_values()

print("✅ Features Most Negatively Correlated with Fraud:")
print(class_corr.head(5))
print()

print("✅ Features Most Positively Correlated with Fraud:")
print(class_corr.tail(5))

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load dataset
df = pd.read_csv("creditcard.csv")

# Step 2: Compute correlation matrix
corr_matrix = df.corr()

# Step 3: Heatmap of all feature correlations
plt.figure(figsize=(16, 12))
sns.heatmap(corr_matrix, cmap='coolwarm', annot=False, fmt=".2f")
plt.title("📈 Correlation Heatmap: All Features")
plt.tight_layout()
plt.show()

# Step 4: Class correlation — fraud indicator strength
class_corr = corr_matrix['Class'].drop('Class').sort_values()

print("\n✅ Most Positively Correlated Features with Fraud:")
print(class_corr.tail(5))

print("\n✅ Most Negatively Correlated Features with Fraud:")
print(class_corr.head(5))

# Step 5: Monitoring Agent Recommendations
print("\n🚨 Recommended Features to Use in Monitoring Agent:")
print("- V11, V4, V2 (strong negative correlation with Class=1)")
print("- V14, V10, V12 (strong positive correlation)")
print("- Amount (also useful if above threshold e.g. > $200)")

# %%
