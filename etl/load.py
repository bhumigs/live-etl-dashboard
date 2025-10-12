import pandas as pd


def load_data(df, target_path):
    df.to_csv(target_path, index=False)
    print(f"✅ Data successfully loaded to {target_path}")
