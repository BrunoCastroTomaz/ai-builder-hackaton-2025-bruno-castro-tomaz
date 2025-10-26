"""
OpenAIService
Responsável por chamadas de geração (chat/completion) para a OpenAI.
- Usa a API oficial openai (python).
- Encapsula sistema + usuário e converte resposta para string.
- Tem tratamento básico de erros e fallback.
"""

import os
import openai
from typing import List, Dict

class OpenAIService:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        openai.api_key = self.api_key
        self.model = model

    def _make_messages(self, system_prompt: str, user_prompt: str) -> List[Dict]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def generate(self,
                 user_prompt: str,
                 system_prompt: str = "Você é um assistente jurídico especializado no Código de Defesa do Consumidor (Brasil). Responda de forma empática, clara e cite a fonte.",
                 max_tokens: int = 512,
                 temperature: float = 0.2) -> str:
        """
        Gera uma resposta usando a API de chat completions.
        Retorna o texto gerado (string).
        """
        messages = self._make_messages(system_prompt, user_prompt)
        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            # Extrai conteúdo do primeiro choice
            content = resp["choices"][0]["message"]["content"]
            return content.strip()
        except Exception as e:
            # Log simples
            print("OpenAI generate error:", e)
            # Retorno amigável para a API externa
            return "Desculpe, houve um erro ao gerar a resposta. Por favor tente novamente mais tarde."
