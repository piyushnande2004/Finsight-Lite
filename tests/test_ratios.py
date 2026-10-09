from tools.ratios import calculate_ratios

def test_basic():
    r = calculate_ratios(1000, 100, 500, 250, 400, 200, prev_revenue=800)
    assert r["net_margin_pct"] == 10.0
    assert r["roe_pct"] == 20.0
    assert r["debt_to_equity"] == 0.5
    assert r["current_ratio"] == 2.0
    assert r["revenue_growth_pct"] == 25.0

def test_missing_data():
    r = calculate_ratios(None, None, 0, None, None, None)
    assert r["net_margin_pct"] is None