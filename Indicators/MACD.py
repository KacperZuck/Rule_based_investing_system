import pandas as pd

def count( df):

    return pd.DataFrame({
        f"MACD": df["EMA 12"] - df["EMA 26"]
    })

