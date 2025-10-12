import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Path to the cleaned CSV
cleaned_file = os.path.join("data", "cleaned", "cleaned_worldometer_data.csv")

# Load the cleaned data
df = pd.read_csv(cleaned_file)

# Quick look at data
print(df.head())
print(df.info())

# Example visualizations:

# 1. Distribution of a numeric column (e.g., total cases)
if "total_cases" in df.columns:
    plt.figure(figsize=(10, 6))
    sns.histplot(df["total_cases"], bins=30, kde=True)
    plt.title("Distribution of Total Cases")
    plt.xlabel("Total Cases")
    plt.ylabel("Frequency")
    plt.show()

# 2. Top 10 countries by total cases
if "country" in df.columns and "total_cases" in df.columns:
    top10 = df.sort_values("total_cases", ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x="country", y="total_cases", data=top10)
    plt.title("Top 10 Countries by Total Cases")
    plt.xticks(rotation=45)
    plt.show()
