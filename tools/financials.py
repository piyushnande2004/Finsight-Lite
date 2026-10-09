import yfinance as yf
from tools.ratios import calculate_ratios

def _val(df, label, col=0):
    try:
        return float(df.loc[label].iloc[col])
    except Exception:
        return None

def get_financials(ticker):
    t = yf.Ticker(ticker)
    inc, bs = t.financials, t.balance_sheet
    ratios = calculate_ratios(
        revenue=_val(inc, "Total Revenue"),
        net_income=_val(inc, "Net Income"),
        equity=_val(bs, "Stockholders Equity"),
        total_debt=_val(bs, "Total Debt"),
        current_assets=_val(bs, "Current Assets"),
        current_liabilities=_val(bs, "Current Liabilities"),
        prev_revenue=_val(inc, "Total Revenue", 1),
    )
    ratios["source"] = f"Yahoo Finance via yfinance ({ticker})"
    return ratios