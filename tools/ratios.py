def safe_div(a, b):
    if a is None or not b:
        return None
    return round(a / b, 4)

def calculate_ratios(revenue, net_income, equity, total_debt,
                     current_assets, current_liabilities, prev_revenue=None):
    nm = safe_div(net_income, revenue)
    growth = None
    if revenue is not None and prev_revenue:
        growth = round((revenue - prev_revenue) / prev_revenue * 100, 2)
    return {
        "net_margin_pct": None if nm is None else round(nm * 100, 2),
        "roe_pct": None if safe_div(net_income, equity) is None else round(net_income / equity * 100, 2),
        "debt_to_equity": safe_div(total_debt, equity),
        "current_ratio": safe_div(current_assets, current_liabilities),
        "revenue_growth_pct": growth,
    }