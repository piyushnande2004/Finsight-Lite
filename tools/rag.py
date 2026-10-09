import os, glob, chromadb, pypdf

client = chromadb.PersistentClient(path="chroma_db")
col = client.get_or_create_collection("reports")

def ingest(pdf_path, chunk=1000):
    name = os.path.basename(pdf_path)
    reader = pypdf.PdfReader(pdf_path)
    total = len(reader.pages)
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        docs, metas, ids = [], [], []
        for j in range(0, len(text), chunk):
            piece = text[j:j + chunk]
            if piece.strip():
                docs.append(piece)
                metas.append({"source": name, "page": i + 1})
                ids.append(f"{name}-{i}-{j}")
        if docs:
            col.upsert(documents=docs, metadatas=metas, ids=ids)
        if (i + 1) % 10 == 0 or i + 1 == total:
            print(f"{name}: page {i + 1}/{total}", flush=True)

def search_report(question, k=4, source=None):
    kwargs = {"query_texts": [question], "n_results": k}
    if source:
        kwargs["where"] = {"source": source}
    r = col.query(**kwargs)
    return [{"text": d, "source": m["source"], "page": m["page"]}
            for d, m in zip(r["documents"][0], r["metadatas"][0])]

if __name__ == "__main__":
    for f in glob.glob("data/*.pdf"):
        ingest(f)
    print("Ingested", col.count(), "chunks")