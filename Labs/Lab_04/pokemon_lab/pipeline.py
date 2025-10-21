from update_portfolio import update_portfolio
from generate_summary import summarize

print("[pipeline] Starting production run ...")
print("[pipeline] Step 1: Update portfolio (ETL) ...")
update_portfolio("./card_inventory", "./card_set_lookup", "card_portfolio.csv")
print("[pipeline] Step 2: Generate summary (report) ...")
summarize("card_portfolio.csv")
print("[pipeline] Done.")
