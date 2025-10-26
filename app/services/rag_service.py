import os
import faiss
import numpy as np
from app.services.embedding_service import EmbeddingService
from app.services.openai_service import OpenAIService
from app.utils.text_loader import TextLoader

class RagService:
    def __init__(self):
        # Carrega textos do CDC e cria/recupera index FAISS
        self.loader = TextLoader()
        self.docs = self.loader.load_docs()  # lista de dicts {id, text, meta}
        self.embed_svc = EmbeddingService()
        self.openai = OpenAIService()
        self.index = None
        self.doc_embeddings = None
        self._build_or_load_index()

    def _build_or_load_index(self):
        # Cria embeddings e um index FAISS simples (in-memory)
        texts = [d["text"] for d in self.docs]
        embeddings = self.embed_svc.embed(texts)
        self.doc_embeddings = np.vstack(embeddings).astype('float32')
        dim = self.doc_embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(self.doc_embeddings)
        self.index = index

    def _search(self, question, k=1):
        q_emb = self.embed_svc.embed(question)[0].astype('float32')
        D, I = self.index.search(np.expand_dims(q_emb, axis=0), k)
        results = []
        for idx in I[0]:
            if idx < len(self.docs):
                results.append(self.docs[idx])
        return results

    def answer_question(self, question):
        # Busca trecho mais similar
        hits = self._search(question, k=1)
        if not hits:
            return ("Não encontrei informações específicas no Código de Defesa do Consumidor sobre isso. Posso te ajudar a buscar outro tipo de orientação?", "")
        context = hits[0]["text"]
        # meta pode conter 'Art. 49' etc — se não, tente extrair da primeira linha do meta
        #source = hits[0].get("meta", hits[0].get("id", ""))
        system_instr = (
            "Você é um agente de atendimento virtual especializado no Código de Defesa do Consumidor (Brasil). "
            "Use apenas o contexto fornecido abaixo para responder. Seja empático e cite o artigo do qual o trecho foi extraído.\n\n"
            "REGRAS OBRIGATÓRIAS:\n"
            "1) Sempre estruture a resposta assim:\nResposta: [texto]\nFonte: Art. XX\n\n"
            "2) Se não houver base suficiente no contexto, responda exatamente: "
            "'Não encontrei informações específicas no Código de Defesa do Consumidor sobre isso.'"
        )
        user_prompt = (
            f"Contexto (trecho da lei):\n{context}\n\n"
            f"Pergunta do cliente: {question}\n\n"
            "Responda conforme as regras obrigatórias acima."
        )
        resp_text = self.openai.generate(user_prompt, system_prompt=system_instr)
        return (resp_text)
