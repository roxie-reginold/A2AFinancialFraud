import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def analyze_dataset():
    print("Loading credit card fraud dataset...")
    try:
        # Load the dataset
        df = pd.read_csv('creditcard.csv')
        
        # Basic dataset information
        print("\n===== Dataset Information =====")
        print(f"Dataset shape: {df.shape}")
        print(f"Number of records: {df.shape[0]}")
        print(f"Number of features: {df.shape[1]}")
        
        # Check column names
        print("\n===== Column Names =====")
        print(df.columns.tolist())
        
        # Basic statistics
        print("\n===== Basic Statistics =====")
        print(df.describe())
        
        # Check for missing values
        print("\n===== Missing Values =====")
        missing_values = df.isnull().sum()
        print(missing_values[missing_values > 0] if any(missing_values > 0) else "No missing values found")
        
        # Fraud distribution
        print("\n===== Fraud Distribution =====")
        fraud_distribution = df['Class'].value_counts(normalize=True) * 100
        print("Class value counts:")
        print(df['Class'].value_counts())
        print(f"Percentage of normal transactions: {fraud_distribution[0]:.4f}%")
        print(f"Percentage of fraudulent transactions: {fraud_distribution[1]:.4f}%")
        
        # Feature correlation
        print("\n===== Feature Correlations with Class =====")
        correlations = df.corr()['Class'].sort_values(ascending=False)
        print(correlations)
        
        # Return the dataframe for further analysis
        return df
        
    except FileNotFoundError:
        print("ERROR: creditcard.csv not found. Please run 'git lfs pull' to download the dataset.")
        return None
    except Exception as e:
        print(f"ERROR: An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    # Run the analysis
    df = analyze_dataset()
    
    # If dataset successfully loaded, create and show a few visualizations
    if df is not None:
        # 1. Class distribution (Fraud vs. Non-Fraud)
        plt.figure(figsize=(6, 4))
        sns.countplot(x='Class', data=df)
        plt.title('Class Distribution (0: Non-Fraud, 1: Fraud)')
        plt.savefig('class_distribution.png')
        
        # 2. Amount distribution for fraud vs. non-fraud
        plt.figure(figsize=(10, 6))
        sns.histplot(df[df['Class']==0]['Amount'], kde=True, color='blue', label='Non-Fraud', stat='density', alpha=0.5)
        sns.histplot(df[df['Class']==1]['Amount'], kde=True, color='red', label='Fraud', stat='density', alpha=0.5)
        plt.title('Amount Distribution')
        plt.legend()
        plt.savefig('amount_distribution.png')
        
        # 3. Time vs Amount with fraud coloring
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='Time', y='Amount', hue='Class', data=df, alpha=0.6)
        plt.title('Time vs Amount (Colored by Class)')
        plt.savefig('time_amount_scatter.png')
        
        print("\nAnalysis complete. Visualizations saved as PNG files.")
