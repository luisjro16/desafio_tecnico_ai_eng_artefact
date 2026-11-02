import os
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.database import query_db

PDF_PATH = "data/politicas_da_loja.pdf"

print("[Setup] A carregar e processar o PDF de políticas...")
loader = PyPDFLoader(PDF_PATH)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(splits, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) 

@tool
def consultar_base_dados(query_sql: str) -> str:
    """
    Executa uma consulta SQL na base de dados SQLite da loja (tabelas: categories, customers, orders, order_items, products, promotions).
    Usa esta ferramenta SEMPRE que precisar ver preços, stock, categorias ou o estado de um pedido.
    A base de dados usa a sintaxe SQLite. Retorna os dados em formato markdown.
    """
    return query_db(query_sql)

@tool
def consultar_politicas(pergunta: str) -> str:
    """
    Pesquisa no manual de políticas e procedimentos da Empório da Música.
    Usa esta ferramenta para responder a dúvidas sobre horários de funcionamento, regras de trocas, devoluções,
    formas de pagamento, prazos de envio e garantias.
    """
    resultados = retriever.invoke(pergunta)

    contexto = "\n\n".join([doc.page_content for doc in resultados])
    return contexto

tools = [consultar_base_dados, consultar_politicas]