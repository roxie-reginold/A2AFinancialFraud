#!/usr/bin/env python3
"""
BigQuery Schema Fix Script

This script fixes the schema mismatch issues found in the recovery logs.
The main issue is that the code is trying to insert 'processed_at' field
but the tables expect different timestamp field names.
"""

import json
import logging
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQuerySchemaFixer:
    """Fix BigQuery schema issues for fraud detection tables."""
    
    def __init__(self, project_id: str, dataset_id: str = "fraud_detection"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.dataset_ref = self.client.dataset(dataset_id)
    
    def analyze_recovery_files(self):
        """Analyze recovery files to understand schema issues."""
        recovery_files = [
            "/Users/innovation/Documents/a2aFinancialFraud/recovery/failed_analysis_results_20250615_210431.json",
            "/Users/innovation/Documents/a2aFinancialFraud/recovery/failed_alerts_20250615_210438.json"
        ]
        
        issues = {}
        
        for file_path in recovery_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                table_type = data.get('table_type')
                error_details = json.loads(data.get('error_details', '[]'))
                
                issues[table_type] = {
                    'errors': error_details,
                    'sample_records': data.get('records', [])
                }
                
                logger.info(f"Found issues in {table_type} table:")
                for error in error_details:
                    for err in error.get('errors', []):
                        logger.info(f"  - {err['message']}")
                        
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        return issues
    
    def get_current_table_schema(self, table_name: str):
        """Get current schema of a BigQuery table."""
        try:
            table_ref = self.dataset_ref.table(table_name)
            table = self.client.get_table(table_ref)
            return [(field.name, field.field_type, field.mode) for field in table.schema]
        except NotFound:
            logger.warning(f"Table {table_name} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting schema for {table_name}: {e}")
            return None
    
    def create_corrected_schema(self):
        """Create corrected table schemas based on recovery file analysis."""
        
        # Analysis Results Table - Use 'analyzed_at' instead of 'processed_at'
        analysis_schema = [
            bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("analysis_method", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("risk_score", "FLOAT64", mode="REQUIRED"),
            bigquery.SchemaField("risk_level", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("fraud_indicators", "STRING", mode="REPEATED"),
            bigquery.SchemaField("recommendations", "STRING", mode="REPEATED"),
            bigquery.SchemaField("analysis_summary", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("confidence_score", "FLOAT64", mode="NULLABLE"),
            bigquery.SchemaField("processing_time_ms", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("analyzed_at", "TIMESTAMP", mode="REQUIRED"),
            # Add processed_at field to match what code is sending
            bigquery.SchemaField("processed_at", "TIMESTAMP", mode="NULLABLE"),
        ]
        
        # Alerts Table - Use 'created_at' and add 'processed_at'
        alerts_schema = [
            bigquery.SchemaField("alert_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("priority", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("urgency", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("alert_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("notification_channels", "STRING", mode="REPEATED"),
            bigquery.SchemaField("alert_status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("acknowledged_by", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("resolution_notes", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("resolved_at", "TIMESTAMP", mode="NULLABLE"),
            # Add processed_at field to match what code is sending
            bigquery.SchemaField("processed_at", "TIMESTAMP", mode="NULLABLE"),
        ]
        
        return {
            "fraud_analysis": analysis_schema,
            "fraud_alerts": alerts_schema
        }
    
    def update_table_schema(self, table_name: str, new_schema):
        """Update a table's schema by adding missing fields."""
        try:
            table_ref = self.dataset_ref.table(table_name)
            table = self.client.get_table(table_ref)
            
            # Get current field names
            current_fields = {field.name for field in table.schema}
            
            # Add new fields that don't exist
            updated_schema = list(table.schema)
            
            for new_field in new_schema:
                if new_field.name not in current_fields:
                    updated_schema.append(new_field)
                    logger.info(f"Adding field '{new_field.name}' to table {table_name}")
            
            # Update table schema
            table.schema = updated_schema
            table = self.client.update_table(table, ["schema"])
            
            logger.info(f"✓ Successfully updated schema for table {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating schema for {table_name}: {e}")
            return False
    
    def create_table_if_not_exists(self, table_name: str, schema):
        """Create table if it doesn't exist."""
        try:
            table_ref = self.dataset_ref.table(table_name)
            
            # Check if table exists
            try:
                self.client.get_table(table_ref)
                logger.info(f"Table {table_name} already exists")
                return True
            except NotFound:
                pass
            
            # Create table
            table = bigquery.Table(table_ref, schema=schema)
            table = self.client.create_table(table)
            logger.info(f"✓ Created table {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating table {table_name}: {e}")
            return False
    
    def fix_all_schemas(self):
        """Fix all identified schema issues."""
        logger.info("Starting BigQuery schema fix...")
        
        # Analyze current issues
        issues = self.analyze_recovery_files()
        logger.info(f"Found issues in tables: {list(issues.keys())}")
        
        # Get corrected schemas
        corrected_schemas = self.create_corrected_schema()
        
        # Create dataset if it doesn't exist
        try:
            self.client.get_dataset(self.dataset_ref)
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = "US"
            dataset.description = "Fraud detection system data warehouse"
            self.client.create_dataset(dataset)
            logger.info(f"Created dataset {self.dataset_id}")
        
        # Fix each table
        success_count = 0
        for table_name, schema in corrected_schemas.items():
            # Try to update existing table schema
            if self.get_current_table_schema(table_name):
                if self.update_table_schema(table_name, schema):
                    success_count += 1
            else:
                # Create table if it doesn't exist
                if self.create_table_if_not_exists(table_name, schema):
                    success_count += 1
        
        logger.info(f"Schema fix complete: {success_count}/{len(corrected_schemas)} tables updated")
        
        # Test the fix by trying to reprocess failed records
        self.test_schema_fix(issues)
    
    def test_schema_fix(self, issues):
        """Test the schema fix by attempting to insert failed records."""
        logger.info("Testing schema fix with failed records...")
        
        for table_type, issue_data in issues.items():
            table_name = "fraud_analysis" if table_type == "analysis_results" else "fraud_alerts"
            records = issue_data.get('sample_records', [])
            
            if not records:
                continue
            
            try:
                table_ref = self.dataset_ref.table(table_name)
                table = self.client.get_table(table_ref)
                
                # Try to insert one record
                test_record = records[0]
                errors = self.client.insert_rows_json(table, [test_record])
                
                if errors:
                    logger.warning(f"Still have errors in {table_name}: {errors}")
                else:
                    logger.info(f"✓ Schema fix verified for {table_name}")
                    
            except Exception as e:
                logger.error(f"Error testing {table_name}: {e}")

def main():
    """Main function to fix BigQuery schema issues."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if not project_id:
        logger.error("GOOGLE_CLOUD_PROJECT environment variable not set")
        return
    
    try:
        fixer = BigQuerySchemaFixer(project_id)
        fixer.fix_all_schemas()
        logger.info("BigQuery schema fix completed successfully!")
        
    except Exception as e:
        logger.error(f"Schema fix failed: {e}")
        raise

if __name__ == "__main__":
    main()