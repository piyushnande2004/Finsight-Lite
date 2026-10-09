import streamlit as st
from agents.graph import app_graph

st.set_page_config(page_title="FinSight Lite", page_icon="📊")
st.title("📊 FinSight Lite")
st.caption("Multi-agent AI financial research: data, risk, RAG and report agents")

company = st.text_input("Company name", "Infosys")
ticker = st.text_input("Ticker (for example INFY.NS or TCS.NS)", "INFY.NS")

if st.button("Analyze"):
    try:
        with st.spinner("Agents are working..."):
            out = app_graph.invoke({"company": company, "ticker": ticker})

        st.subheader("Key ratios (calculated by code, not by the LLM)")
        ratios = {k: v for k, v in out["ratios"].items() if k != "source"}
        st.table([ratios])
        st.caption(out["ratios"].get("source", ""))

        st.subheader("Risk flags (rule-based)")
        if out["flags"]:
            for f in out["flags"]:
                st.warning(f)
        else:
            st.success("No risk flags triggered")

        st.subheader("Investment memo")
        st.markdown(out["memo"])

        with st.expander("Sources retrieved from the annual report"):
            for p in out["passages"]:
                st.markdown(f"**{p['source']}, page {p['page']}**")
                st.write(p["text"][:400] + "...")
    except Exception as e:
        st.error(f"Something went wrong: {e}")