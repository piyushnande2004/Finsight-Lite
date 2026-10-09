import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.financials import get_financials
from tools.rag import search_report

load_dotenv()
llm = ChatGoogleGenerativeAI(model=os.getenv("MODEL", "gemini-2.0-flash"))

class State(TypedDict, total=False):
    company: str
    ticker: str
    ratios: dict
    flags: list
    passages: list
    memo: str

def data_agent(s):
    return {"ratios": get_financials(s["ticker"])}

def risk_agent(s):
    r, flags = s["ratios"], []
    if r.get("debt_to_equity") and r["debt_to_equity"] > 2:
        flags.append("High leverage: debt-to-equity above 2")
    if r.get("current_ratio") and r["current_ratio"] < 1:
        flags.append("Liquidity risk: current ratio below 1")
    if r.get("net_margin_pct") is not None and r["net_margin_pct"] < 5:
        flags.append("Thin profitability: net margin below 5%")
    if r.get("revenue_growth_pct") is not None and r["revenue_growth_pct"] < 0:
        flags.append("Revenue is declining")
    return {"flags": flags}

def research_agent(s):
    return {"passages": search_report(f"{s['company']} business model, risks and outlook")}

def writer_agent(s):
    ctx = "\n".join(f"[{p['source']} p.{p['page']}] {p['text']}" for p in s["passages"])
    prompt = f"""You are a financial analyst. Write a short investment memo for {s['company']}.
Use ONLY the data below. Do not calculate anything yourself; use the ratios as given.
Cite report passages like (source, page). If data is missing, say so.

RATIOS (computed by code): {s['ratios']}
RISK FLAGS (rule-based): {s['flags']}
ANNUAL REPORT EXCERPTS:
{ctx}

Sections: Business Overview, Financial Health, Risks, Verdict (Strong / Neutral / Weak)."""
    return {"memo": llm.invoke(prompt).content}

g = StateGraph(State)
g.add_node("data", data_agent)
g.add_node("risk", risk_agent)
g.add_node("research", research_agent)
g.add_node("writer", writer_agent)
g.set_entry_point("data")
g.add_edge("data", "risk")
g.add_edge("risk", "research")
g.add_edge("research", "writer")
g.add_edge("writer", END)
app_graph = g.compile()

if __name__ == "__main__":
    out = app_graph.invoke({"company": "Infosys", "ticker": "INFY.NS"})
    print(out["ratios"])
    print(out["flags"])
    print(out["memo"])