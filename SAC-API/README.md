# SAC-API (MVP) - Atendimento automático com RAG + OpenAI

## Requisitos
- Python 3.10+
- Ter uma chave OpenAI (`OPENAI_API_KEY`)

## Instalação
1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. Copiar `.env.example` para `.env` e definir `OPENAI_API_KEY`.

## Executando
    export FLASK_APP=app.main
export FLASK_ENV=development
flask run --host=127.0.0.1 --port=5000

Acesse `http://127.0.0.1:5000/chat`

## Endpoints
- `POST /ask` — body: `{ "question": "..." }` → resposta JSON `{ "answer": "...", "source": "..." }`
- `GET /chat` — interface web
