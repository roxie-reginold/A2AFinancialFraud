#!/usr/bin/env python3
"""
Google Cloud Platform Resource Setup Script
Sets up Pub/Sub topics, subscriptions, and BigQuery resources for the fraud detection system.
"""

import os
import logging
from google.cloud import pubsub_v1
from google.cloud import bigquery
from google.cloud.exceptions import Conflict, NotFound
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_pubsub_resources(project_id: str):
    """Set up Pub/Sub topics and subscriptions."""
    try:
        # Initialize Pub/Sub clients
        publisher = pubsub_v1.PublisherClient()
        subscriber = pubsub_v1.SubscriberClient()
        
        # Define topics and subscriptions
        topics = [
            "transactions-topic",
            "flagged-transactions", 
            "analysis-results",
            "hybrid-analysis-results",
            "fraud-alerts"
        ]
        
        subscriptions = [
            ("transactions-topic", "transactions-sub"),
            ("flagged-transactions", "flagged-sub"),
            ("analysis-results", "analysis-sub"),
            ("fraud-alerts", "alerts-sub")
        ]
        
        # Create topics
        for topic_name in topics:
            topic_path = publisher.topic_path(project_id, topic_name)
            try:
                publisher.create_topic(request={"name": topic_path})
                logger.info(f"✅ Created topic: {topic_name}")
            except Conflict:
                logger.info(f"ℹ️  Topic already exists: {topic_name}")
            except Exception as e:
                logger.error(f"❌ Error creating topic {topic_name}: {e}")
        
        # Create subscriptions
        for topic_name, sub_name in subscriptions:
            topic_path = publisher.topic_path(project_id, topic_name)
            subscription_path = subscriber.subscription_path(project_id, sub_name)
            try:
                subscriber.create_subscription(
                    request={
                        "name": subscription_path,
                        "topic": topic_path,
                        "ack_deadline_seconds": 60
                    }
                )
                logger.info(f"✅ Created subscription: {sub_name} for topic: {topic_name}")
            except Conflict:
                logger.info(f"ℹ️  Subscription already exists: {sub_name}")
            except Exception as e:
                logger.error(f"❌ Error creating subscription {sub_name}: {e}")
                
        logger.info("🎯 Pub/Sub resources setup completed!")
        
    except Exception as e:
        logger.error(f"❌ Error setting up Pub/Sub resources: {e}")
        return False
    
    return True

def setup_bigquery_resources(project_id: str):
    """Set up BigQuery dataset and tables."""
    try:
        # Initialize BigQuery client
        client = bigquery.Client(project=project_id)
        
        # Create dataset
        dataset_id = "fraud_detection"
        dataset_ref = client.dataset(dataset_id)
        
        try:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset.description = "Fraud Detection System Data Warehouse"
            client.create_dataset(dataset)
            logger.info(f"✅ Created dataset: {dataset_id}")
        except Conflict:
            logger.info(f"ℹ️  Dataset already exists: {dataset_id}")
        except Exception as e:
            logger.error(f"❌ Error creating dataset: {e}")
        
        # Define table schemas
        tables_config = {
            "fraud_transactions": [
                bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("amount", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("features", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ],
            "fraud_analysis": [
                bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("risk_score", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("analysis_method", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("fraud_indicators", "STRING", mode="REPEATED"),
                bigquery.SchemaField("recommendations", "STRING", mode="REPEATED"),
                bigquery.SchemaField("analysis_summary", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("model_used", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ],
            "fraud_alerts": [
                bigquery.SchemaField("alert_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("alert_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("priority", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("risk_score", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("notifications_sent", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
            ],
            "fraud_reports": [
                bigquery.SchemaField("report_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("report_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("time_period", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("metrics", "JSON", mode="REQUIRED"),
                bigquery.SchemaField("summary", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            ]
        }
        
        # Create tables
        for table_name, schema in tables_config.items():
            table_ref = dataset_ref.table(table_name)
            try:
                table = bigquery.Table(table_ref, schema=schema)
                table.description = f"Fraud detection {table_name.replace('_', ' ')} data"
                client.create_table(table)
                logger.info(f"✅ Created table: {table_name}")
            except Conflict:
                logger.info(f"ℹ️  Table already exists: {table_name}")
            except Exception as e:
                logger.error(f"❌ Error creating table {table_name}: {e}")
        
        logger.info("🗄️  BigQuery resources setup completed!")
        
    except Exception as e:
        logger.error(f"❌ Error setting up BigQuery resources: {e}")
        return False
    
    return True

def verify_resources(project_id: str):
    """Verify that all resources were created successfully."""
    try:
        logger.info("🔍 Verifying resource setup...")
        
        # Verify Pub/Sub
        publisher = pubsub_v1.PublisherClient()
        subscriber = pubsub_v1.SubscriberClient()
        
        project_path = f"projects/{project_id}"
        topics = list(publisher.list_topics(request={"project": project_path}))
        subscriptions = list(subscriber.list_subscriptions(request={"project": project_path}))
        
        logger.info(f"📡 Found {len(topics)} topics and {len(subscriptions)} subscriptions")
        
        # Verify BigQuery
        client = bigquery.Client(project=project_id)
        datasets = list(client.list_datasets())
        dataset = client.get_dataset("fraud_detection")
        tables = list(client.list_tables(dataset))
        
        logger.info(f"🗄️  Found {len(datasets)} datasets and {len(tables)} tables in fraud_detection")
        
        logger.info("✅ Resource verification completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying resources: {e}")
        return False

def main():
    """Main setup function."""
    # Get project ID from environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not project_id:
        logger.error("❌ GOOGLE_CLOUD_PROJECT environment variable not set")
        sys.exit(1)
    
    logger.info(f"🚀 Setting up Google Cloud resources for project: {project_id}")
    
    # Check if we should bypass cloud validation (for development)
    bypass_validation = os.getenv("BYPASS_CLOUD_VALIDATION", "false").lower() == "true"
    
    if bypass_validation:
        logger.info("⚠️  BYPASS_CLOUD_VALIDATION is enabled - skipping actual resource creation")
        logger.info("ℹ️  In production, set BYPASS_CLOUD_VALIDATION=false")
        return
    
    # Setup resources
    success = True
    
    # Setup Pub/Sub
    if not setup_pubsub_resources(project_id):
        success = False
    
    # Setup BigQuery
    if not setup_bigquery_resources(project_id):
        success = False
    
    # Verify setup
    if success and not verify_resources(project_id):
        success = False
    
    if success:
        logger.info("🎉 All Google Cloud resources setup completed successfully!")
    else:
        logger.error("💥 Some resources failed to setup. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()