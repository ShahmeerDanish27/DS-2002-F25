import os, sys, json, glob
import pandas as pd

def _load_lookup_data(lookup_dir: str) -> pd.DataFrame:
    """Load all JSONs, normalize, and compute market value safely."""
    frames = []
    for path in glob.glob(os.path.join(lookup_dir, "*.json")):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rows = data.get("data", [])
        if not rows:
            continue

        df = pd.json_normalize(rows)

        # Safely get holofoil/normal prices (avoid passing None into fillna)
        holo = pd.to_numeric(df.get("tcgplayer.prices.holofoil.market"), errors="coerce")
        normal = pd.to_numeric(df.get("tcgplayer.prices.normal.market"),  errors="coerce")
        df["card_market_value"] = holo.fillna(normal).fillna(0.0)

        # Standardize columns
        df = df.rename(columns={
            "id": "card_id",
            "name": "card_name",
            "number": "card_number",
            "set.id": "set_id",
            "set.name": "set_name",
        })
        keep = ["card_id", "card_name", "card_number", "set_id", "set_name", "card_market_value"]
        df = df[[c for c in keep if c in df.columns]].copy()
        frames.append(df)

    if not frames:
        return pd.DataFrame(columns=["card_id","card_name","card_number","set_id","set_name","card_market_value"])

    lookup = pd.concat(frames, ignore_index=True)
    lookup = (lookup.sort_values("card_market_value", ascending=False)
                    .drop_duplicates(subset=["card_id"], keep="first")
                    .reset_index(drop=True))
    return lookup

def _load_inventory_data(inventory_dir: str) -> pd.DataFrame:
    """Load CSV(s) and create card_id = set_id-number."""
    frames = []
    for path in glob.glob(os.path.join(inventory_dir, "*.csv")):
        frames.append(pd.read_csv(path))
    if not frames:
        return pd.DataFrame(columns=[
            "card_name","set_id","card_number","binder_name","page_number","slot_number","card_id"
        ])
    inv = pd.concat(frames, ignore_index=True)
    inv["set_id"] = inv["set_id"].astype(str)
    inv["card_number"] = inv["card_number"].astype(str)
    inv["card_id"] = inv["set_id"] + "-" + inv["card_number"]
    return inv

def _coalesce(df: pd.DataFrame, out_col: str, prefer: str, fallback: str) -> None:
    """Prefer one column, fallback to another; create out_col."""
    if prefer in df.columns and fallback in df.columns:
        df[out_col] = df[prefer].where(df[prefer].notna(), df[fallback])
    elif prefer in df.columns:
        df[out_col] = df[prefer]
    elif fallback in df.columns:
        df[out_col] = df[fallback]
    else:
        df[out_col] = pd.NA

def update_portfolio(inventory_dir: str, lookup_dir: str, output_file: str) -> None:
    lookup = _load_lookup_data(lookup_dir)
    inv = _load_inventory_data(inventory_dir)

    if inv.empty:
        cols = ["index","binder_name","page_number","slot_number",
                "card_id","card_name","set_name","card_number","card_market_value"]
        pd.DataFrame(columns=cols).to_csv(output_file, index=False)
        print("ERROR: No inventory CSVs found or inventory is empty.", file=sys.stderr)
        return

    keep_lookup = ["card_id","card_name","set_name","card_number","card_market_value"]
    lookup_slim = lookup[keep_lookup] if not lookup.empty else pd.DataFrame(columns=keep_lookup)

    merged = pd.merge(inv, lookup_slim, on="card_id", how="left", suffixes=("_inv","_look"))

    # Coalesce card_name/card_number to single columns (prefer lookup)
    _coalesce(merged, "card_name",   "card_name_look",   "card_name_inv")
    _coalesce(merged, "card_number", "card_number_look", "card_number_inv")

    # Ensure numeric and set_name fallback
    if "card_market_value" not in merged.columns:
        merged["card_market_value"] = 0.0
    merged["card_market_value"] = pd.to_numeric(merged["card_market_value"], errors="coerce").fillna(0.0)
    merged["set_name"] = merged.get("set_name", pd.Series(["NOT_FOUND"]*len(merged))).fillna("NOT_FOUND")

    # Build index column
    merged["index"] = (
        merged["binder_name"].astype(str) + ":" +
        merged["page_number"].astype(str) + ":" +
        merged["slot_number"].astype(str)
    )

    final_cols = ["index","binder_name","page_number","slot_number",
                  "card_id","card_name","set_name","card_number","card_market_value"]
    for c in final_cols:
        if c not in merged.columns:
            merged[c] = 0.0 if c == "card_market_value" else ""

    merged[final_cols].to_csv(output_file, index=False)
    print(f"Wrote portfolio: {output_file}")

def main():
    update_portfolio("./card_inventory", "./card_set_lookup", "card_portfolio.csv")

def test():
    update_portfolio("./card_inventory_test", "./card_set_lookup_test", "test_card_portfolio.csv")

if __name__ == "__main__":
    print("Starting update_portfolio.py in TEST mode ...", file=sys.stderr)
    test()
