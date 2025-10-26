import os

class TextLoader:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "..", "data", "cdc_articles.txt")

    def load_docs(self):
        """
        Lê o arquivo e transforma em lista de docs.
        Formato do arquivo: blocos separados por linha '---' contendo:
        ID: Art. XX
        META: título opcional
        TEXTO: linhas do artigo
        """
        p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "cdc_articles.txt"))
        with open(p, "r", encoding="utf-8") as f:
            content = f.read().strip()
        blocks = [b.strip() for b in content.split("\n---\n") if b.strip()]
        docs = []
        for i, b in enumerate(blocks):
            lines = b.splitlines()
            doc_id = f"doc_{i}"
            meta = lines[0] if lines else ""
            text = "\n".join(lines[1:]) if len(lines) > 1 else ""
            docs.append({"id": doc_id, "meta": meta, "text": text})
        return docs
