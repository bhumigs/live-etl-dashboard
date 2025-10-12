import os
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data


def run_etl():
    os.makedirs("data", exist_ok=True)
    df = extract_data("data/worldometer_data.csv")
    df = transform_data(df)
    load_data(df, target_path="data/etl_output.csv")
    print("✅ ETL completed successfully.")


# Optional: run immediately if executed directly
if __name__ == "__main__":
    run_etl()
