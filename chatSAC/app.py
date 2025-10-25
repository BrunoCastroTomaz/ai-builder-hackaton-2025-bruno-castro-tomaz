from flask import Flask, request, jsonify, render_template, url_for
from flask_cors import CORS
import base64
import os
import sys
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from dotenv import load_dotenv
from google import genai
from google.genai import types
import uuid # Módulo para gerar um ID único de sessão
import json # Para lidar com a serialização do histórico

# Configuração da chave da API do Gemini
# Carrega o arquivo .env
load_dotenv()

# Obtém a chave GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("A chave GEMINI_API_KEY não foi configurada!")

# Configurações de pastas locais
txt_folder = "txt_files"  # Diretório com os arquivos TXT para leitura
if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)
    print(f"Crie o diretório '{txt_folder}' e adicione arquivos TXT para teste.")
    sys.exit(0)


# Verificar se o banco de vetores já foi criado para evitar duplicação de leitura e armazenamento
docs = []
text = ""

if not os.path.exists("./chroma_db_nccn") or not os.listdir("./chroma_db_nccn"):
    
    # Tentando ler e processar os documentos apenas uma vez
    # Itera sobre todos os arquivos na pasta com a extensao .txt
    for txt_name in os.listdir(txt_folder):
        if txt_name.endswith('.txt'):
            print(f"Lendo arquivo TXT: {txt_name}")
            txt_path = os.path.join(txt_folder, txt_name)
            with open(txt_path, 'r', encoding='utf-8') as file:
                text = file.read()
                docs.append(Document(page_content=text))
                #reiniciar variavel text para evitar redundancia
                text = ""
    
    # Divisão de texto em partes menores
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(docs)
    
    # Criação de embeddings e banco de vetores local
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    vectorstore = Chroma.from_documents(docs, embedding=embedding_function, persist_directory="./chroma_db_nccn")

    print(f"Número de documentos no banco de vetores: {vectorstore._collection.count()}")


embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)
vectorstore = Chroma(persist_directory="./chroma_db_nccn", embedding_function=embedding_function)


#app = Flask(__name__)
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
# Para usar 'session' no Flask (necessário para um ID de sessão estável), você precisa de uma chave secreta
app.secret_key = os.urandom(24)

last_answer = ""

# Função para gerar prompts
def generate_rag_prompt(query, context, last_answer=""):
    escaped_context = context.replace("'", "").replace('"', "").replace("\n", " ")
    escaped_last_answer = last_answer.replace("'", "").replace('"', "").replace("\n", " ")

    prompt = f"""
    Você é um assistente virtual especializado em realizar atendimentos para uma pizzaria, utilizando o contexto de referência fornecido. 
    **Seja claro, conciso e amigável em suas respostas.** 
    **Jamais responda utilizando a expressão 'com base no texto fornecido' ou similares em suas respostas.**
    * **Priorize a relevância:** Se a informação for muito extensa, forneça um resumo conciso.
    * **Adapte a linguagem:** Utilize termos simples e evite jargões técnicos.
    * **Seja proativo:** Se não encontrar a resposta exata, tente:
        * **Generalizar:** Oferecer uma resposta mais ampla sobre o tópico.
        * **Inferir:** Fazer suposições lógicas com base no contexto.
        * **Redirecionar:** Sugerir outras fontes de informação.
    * **Demonstre empatia:** Se não souber a resposta, seja transparente e ofereça alternativas.
    
    **Última Resposta:** '{escaped_last_answer}'
    **Pergunta:** '{query}'
    **Contexto:** '{escaped_context}'
    
    **Resposta:**
    """
    
    return prompt

# Função para buscar contexto relevante no banco de vetores
def get_relevant_context_from_db(query):
    context = ""
    vector_db = Chroma(persist_directory="./chroma_db_nccn", embedding_function=embedding_function)
    search_results = vector_db.similarity_search(query, k=6)
    #print(f"resultados extraidos do banco de dados:\n {search_results}")  
    for result in search_results:
        context += result.page_content + "\n"
    return context

# Função para gerar resposta usando streaming do Gemini
def generate_answer(prompt: str) -> str:
    """
    Gera uma resposta do modelo Gemini em modo streaming e retorna a string completa.
    """
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # Use o modelo fornecido no seu código
    model = "gemini-flash-latest" 
    
    # Prepara o conteúdo com o prompt RAG
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    
    # Configuração de geração (incluindo thinking_config)
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=-1,
        ),
    )

    full_answer = ""
    
    # Chama o modelo em modo streaming
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # Concatena os pedaços de texto em uma única string
        full_answer += chunk.text
    
    # Retorna a resposta completa
    return full_answer


@app.route('/chatSAC', methods=['POST'])
def chatSAC():
    #lógica de resposta verificando se há cardápio no sistema
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:#query
        return jsonify({"error": "A consulta não pode estar vazia"}), 400
    try:
        context = get_relevant_context_from_db(prompt)#query
        rag_prompt = generate_rag_prompt(query=prompt, context=context)
        # Chama a função generate_answer (agora implementada com streaming)
        answer = generate_answer(prompt=rag_prompt)
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Erro ao processar o prompt: {e}")  # Loga qualquer exceção
        return jsonify({"erro": "Erro ao processar o prompt."}), 500


@app.route('/')
def index():
    return render_template('index.html', title='ChatSAC')

# Função para reiniciar os embeddings ao encerrar o programa
def reset_embeddings():
    if os.path.exists("./chroma_db_nccn"):
        print("Removendo banco de vetores para reinicialização...")
        for file in os.listdir("./chroma_db_nccn"):
            file_path = os.path.join("./chroma_db_nccn", file)
            os.remove(file_path)
        print("Banco de vetores reinicializado.")


if __name__ == '__main__':    
    app.run(debug=True)