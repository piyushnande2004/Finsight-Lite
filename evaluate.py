import time, re
from agents.graph import app_graph

TESTS = [("Infosys", "INFY.NS"), ("TCS", "TCS.NS")]
KEYS = ["net_margin_pct", "roe_pct", "debt_to_equity", "current_ratio", "revenue_growth_pct"]

rows, passed, total, times = [], 0, 0, []

for name, ticker in TESTS:
    start = time.time()
    try:
        out = app_graph.invoke({"company": name, "ticker": ticker})
        secs = round(time.time() - start, 1)
        r, memo = out["ratios"], out["memo"]
        c1 = all(r.get(k) is not None for k in KEYS)
        c2 = bool(re.search(rf"{name.lower()}\.pdf,\s*p\.?\s*\d+", memo, re.IGNORECASE))
        c3 = c1 and f"{r['net_margin_pct']:.2f}" in memo and f"{r['roe_pct']:.2f}" in memo
        c4 = any(w in memo for w in ["Strong", "Neutral", "Weak"])
    except Exception as e:
        secs, c1, c2, c3, c4 = round(time.time() - start, 1), False, False, False, False
        print("Error for", name, ":", e)
    checks = [c1, c2, c3, c4]
    passed += sum(checks)
    total += len(checks)
    times.append(secs)
    mark = lambda x: "PASS" if x else "FAIL"
    rows.append(f"| {name} | {mark(c1)} | {mark(c2)} | {mark(c3)} | {mark(c4)} | {secs} |")
    print(name, checks, secs)
    time.sleep(5)

lines = [
    "# Evaluation results", "",
    "| Company | All 5 ratios fetched | Memo cites the correct company's report | Memo numbers match code | Verdict present | Time (s) |",
    "|---|---|---|---|---|---|",
] + rows + [
    "",
    f"**Checks passed: {passed}/{total} ({round(100 * passed / total)}%)**",
    f"**Average time per report: {round(sum(times) / len(times), 1)} s**",
]
open("EVAL.md", "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))