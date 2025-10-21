import sys
import pandas as pd

def summarize(csv_path: str) -> None:
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Could not find {csv_path}")
        return

    # Fill missing numeric safely
    if "card_market_value" not in df.columns:
        print("No 'card_market_value' column found.")
        return

    total_value = float(df["card_market_value"].fillna(0.0).sum())

    mvi = None
    if {"card_name","card_id","card_market_value"}.issubset(df.columns) and not df.empty:
        mvi = df.loc[df["card_market_value"].fillna(0.0).idxmax()]

    print(f"Total Portfolio Value: ${total_value:,.2f}")
    if mvi is not None:
        print(f"Most Valuable Card: {mvi['card_name']} ({mvi['card_id']}) - ${float(mvi['card_market_value']):,.2f}")

def main():
    # Production mode: read card_portfolio.csv
    summarize("card_portfolio.csv")

def test():
    # Test mode: read test_card_portfolio.csv
    summarize("test_card_portfolio.csv")

if __name__ == "__main__":
    # Default to TEST behavior when invoked directly during `make Test`
    test()
