import os, glob, chromadb, pypdf

client = chromadb.PersistentClient(path="chroma_db")
col = client.get_or_create_collection("reports")

def ingest(pdf_path, chunk=1000):
    name = os.path.basename(pdf_path)
    reader = pypdf.PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for j in range(0, len(text), chunk):
            piece = text[j:j + chunk]
            if piece.strip():
                col.upsert(documents=[piece],
                           metadatas=[{"source": name, "page": i + 1}],
                           ids=[f"{name}-{i}-{j}"])

def search_report(question, k=4):
    r = col.query(query_texts=[question], n_results=k)
    return [{"text": d, "source": m["source"], "page": m["page"]}
            for d, m in zip(r["documents"][0], r["metadatas"][0])]

if __name__ == "__main__":
    for f in glob.glob("data/*.pdf"):
        ingest(f)
    print("Ingested", col.count(), "chunks")