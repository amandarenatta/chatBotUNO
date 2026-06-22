import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import config

@st.cache_resource
def get_embeddings():
    """Retorna o modelo de embeddings (em cache para evitar recarregamento)."""
    return HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

def is_indexed():
    """Verifica se o índice FAISS já existe localmente."""
    
    index_file = os.path.join(config.DB_FAISS_PATH, "index.faiss")
    pkl_file = os.path.join(config.DB_FAISS_PATH, "index.pkl")
    return os.path.exists(index_file) and os.path.exists(pkl_file)

def build_index():
    """Lê o PDF, faz o chunking, gera embeddings e salva o índice FAISS."""
    if not os.path.exists(config.PDF_PATH):
        raise FileNotFoundError(f"Arquivo PDF de regras não encontrado em: {config.PDF_PATH}")

    
    loader = PyPDFLoader(config.PDF_PATH)
    documents = loader.load()


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)

    
    embeddings = get_embeddings()
    db = FAISS.from_documents(chunks, embeddings)

    
    os.makedirs(config.DB_FAISS_PATH, exist_ok=True)
    db.save_local(config.DB_FAISS_PATH)
    return db

def load_index():
    """Carrega o índice FAISS local."""
    embeddings = get_embeddings()
    return FAISS.load_local(
        config.DB_FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

def get_vectorstore():
    """Retorna o vectorstore, criando-o se necessário."""
    if is_indexed():
        return load_index()
    else:
        return build_index()

def expand_query_in_portuguese(query: str) -> str:
    """Expande a query do usuário com sinônimos locais em português para otimizar a busca no PDF."""
    q = query.lower()
    expansions = []
    if "gritar uno" in q or "falar uno" in q or "esqueceu" in q or "esqueci" in q:
        expansions.extend(["gritar UNO", "penalidade", "esquecer de falar", "comprar duas cartas"])
    if "+4" in q or "comprar quatro" in q or "mais quatro" in q:
        expansions.extend(["Coringa Comprar Quatro", "desafio", "jogar ilegalmente", "comprar 4 cartas"])
    if "+2" in q or "comprar duas" in q or "mais duas" in q:
        expansions.extend(["Comprar Duas", "acumular +2", "comprar 2 cartas"])
    if "começo" in q or "começa" in q or "início" in q or "distribui" in q:
        expansions.extend(["distribuir 7 cartas", "mão inicial", "preparação do jogo"])
    if "inverter" in q or "sentido" in q or "direção" in q:
        expansions.extend(["carta Inverter", "sentido horário", "sentido anti-horário"])
    if "pular" in q or "bloqueio" in q or "passa" in q:
        expansions.extend(["carta Pular", "perder a vez", "próximo jogador"])

    if expansions:
        return f"{query}, " + ", ".join(expansions)
    return query

def answer_question(query: str, vectorstore, api_key: str):
    """Realiza a busca semântica e gera a resposta utilizando o Gemini com fallback automático entre modelos."""
    
    search_query = expand_query_in_portuguese(query)
    
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 7})
    docs = retriever.invoke(search_query)

    
    context = "\n\n".join([doc.page_content for doc in docs])

    
    template = """Voce é o Fiscal Oficial do UNO (ou Manual Inteligente do UNO). Seu objetivo é responder as duvidas dos jogadores usando contexto de regras fornecido. O usuario fara perguntas, entao interprete sinonimos e variações. Baseie-se estritamente no contexto fornecido e nao invente mecanicas . Se, e somente se, o assunto da pergunta for completamente bizarro ou totalmente ausente do contexto responde "Desculpe, nao encontrei essa regra no manual oficial".

Contexto de regras:
{context}

Pergunta do jogador: {question}

Resposta do Fiscal:"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    models_to_try = [
        config.GEMINI_MODEL,  
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.5-flash"
    ]
    
    
    unique_models = []
    for model in models_to_try:
        if model and model not in unique_models:
            unique_models.append(model)

    last_exception = None
    is_429 = False

    
    for model_name in unique_models:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.0,
                max_tokens=1024
            )
            chain = prompt | llm
            response = chain.invoke({"context": context, "question": query})
            return response.content.strip(), docs
        except Exception as e:
            last_exception = e
            err_msg = str(e).upper()
            if any(term in err_msg for term in ["429", "RESOURCE_EXHAUSTED", "QUOTA", "LIMIT"]):
                is_429 = True
            
            continue

    
    if is_429:
        raise RuntimeError(
            "Limite de cota de requisições excedido (Erro 429). A cota gratuita diária ou por minuto da API "
            "do Gemini foi temporariamente atingida. Por favor, aguarde cerca de 1 minuto antes de enviar uma nova "
            "pergunta."
        )
    else:
        raise RuntimeError(
            f"Erro ao processar com os modelos disponíveis do Gemini: {last_exception}"
        )
