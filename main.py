# JURISRAG - RAG para conhecimentos jurídicos brasileiros

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from colorama import Fore, Style, init
from langchain_community.document_loaders import DirectoryLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# Initialize colorama
init(autoreset=True)

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jurisrag.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def print_color(message, color=Fore.WHITE, style=Style.NORMAL):
    """Print colored message to console"""
    print(f"{style}{color}{message}{Style.RESET_ALL}")

def print_header(message):
    """Print a header message"""
    print_color("=" * 70, Fore.CYAN, Style.BRIGHT)
    print_color(message, Fore.CYAN, Style.BRIGHT)
    print_color("=" * 70, Fore.CYAN, Style.BRIGHT)

def print_success(message):
    """Print success message"""
    print_color(f"✅ {message}", Fore.GREEN, Style.BRIGHT)
    logger.info(message)

def print_info(message):
    """Print info message"""
    print_color(f"ℹ️  {message}", Fore.BLUE)
    logger.info(message)

def print_warning(message):
    """Print warning message"""
    print_color(f"⚠️  {message}", Fore.YELLOW, Style.BRIGHT)
    logger.warning(message)

def print_error(message):
    """Print error message"""
    print_color(f"❌ {message}", Fore.RED, Style.BRIGHT)
    logger.error(message)

def validate_environment():
    """Validate that all required environment variables are configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print_error("OpenAI API key not configured!")
        print("Please configure your API key in the .env file before running.")
        print("See .env file for instructions.")
        sys.exit(1)
    return True

def load_documents(data_dir="/Users/gabrielramos/Downloads/DRIVE_DO_BELISARIO"):
    """Load all .docx documents from the specified directory."""
    print_info(f"Loading documents from: {data_dir}")

    if not os.path.exists(data_dir):
        print_error(f"Directory not found: {data_dir}")
        sys.exit(1)

    try:
        loader = DirectoryLoader(
            data_dir,
            glob="**/*.docx",
            loader_cls=Docx2txtLoader,
            show_progress=True
        )
        documents = loader.load()

        if not documents:
            print_error("No documents loaded")
            sys.exit(1)

        print_success(f"Loaded {len(documents)} documents")
        return documents

    except Exception as e:
        print_error(f"Error loading documents: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into smaller chunks for embedding."""
    print_info("Splitting documents into chunks...")

    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)

        if not chunks:
            print_error("No chunks created")
            sys.exit(1)

        print_success(f"Created {len(chunks)} chunks")
        return chunks

    except Exception as e:
        print_error(f"Error splitting documents: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

def create_vectorstore(chunks):
    """Create FAISS vectorstore from document chunks using OpenAI embeddings."""
    print_info("Creating embeddings and vectorstore...")

    try:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local("vectorstore")
        print_success("Vectorstore created and saved")
        return vectorstore

    except Exception as e:
        print_error(f"Error creating vectorstore: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

def load_vectorstore():
    """Load existing vectorstore from disk."""
    print_info("Loading vectorstore from disk...")

    if not os.path.exists("vectorstore"):
        print_error("Vectorstore not found!")
        print("Please run 'python load.py' first to create the vectorstore.")
        sys.exit(1)

    try:
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local(
            "vectorstore",
            embeddings,
            allow_dangerous_deserialization=True
        )
        print_success("Vectorstore loaded successfully")
        logger.info(f"Vectorstore loaded from disk")
        return vectorstore

    except Exception as e:
        print_error(f"Error loading vectorstore: {str(e)}")
        print("The vectorstore may be corrupted. Try running 'python load.py' again.")
        logger.exception("Full traceback:")
        sys.exit(1)

def create_rag_chain(vectorstore):
    """Create RAG chain for question answering."""
    print_info("Creating RAG chain...")

    try:
        # Use ChatOpenAI instead of deprecated OpenAI
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(
                search_kwargs={"k": 5}  # Retrieve top 5 most relevant chunks
            ),
            return_source_documents=True
        )

        print_success("RAG chain created successfully")
        logger.info("RAG chain created with gpt-3.5-turbo")
        return qa_chain

    except Exception as e:
        print_error(f"Error creating RAG chain: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

def main():
    """Main function to run the interactive JURISRAG Q&A system."""
    print_header("📚 JURISRAG - Sistema de Perguntas e Respostas Jurídicas")
    print()
    logger.info("Starting JURISRAG Q&A system")

    try:
        # Validate environment
        validate_environment()

        # Check if vectorstore exists
        if os.path.exists("vectorstore"):
            print_info("Found existing vectorstore, loading...")
            vectorstore = load_vectorstore()
        else:
            print_warning("No vectorstore found, creating new one...")
            print_warning("This will take a while and consume API credits.")
            print()

            docs = load_documents()
            chunks = split_documents(docs)
            vectorstore = create_vectorstore(chunks)

        # Create RAG chain
        qa_chain = create_rag_chain(vectorstore)

        print()
        print_header("✅ JURISRAG está pronto para responder perguntas!")
        print()
        print_color("Instruções:", Fore.CYAN, Style.BRIGHT)
        print("  • Digite sua pergunta sobre legislação brasileira")
        print("  • Digite 'sair' para encerrar o programa")
        print("  • Digite 'limpar' para limpar a tela")
        print()
        logger.info("Interactive Q&A session started")

        # Interactive Q&A loop
        question_count = 0
        while True:
            try:
                query = input(f"{Fore.GREEN}💬 Pergunta: {Style.RESET_ALL}").strip()

                if not query:
                    continue

                if query.lower() in ['sair', 'exit', 'quit']:
                    print()
                    print_success(f"Encerrando JURISRAG. {question_count} perguntas respondidas. Até logo!")
                    logger.info(f"Session ended. {question_count} questions answered.")
                    break

                if query.lower() in ['limpar', 'clear', 'cls']:
                    os.system('clear' if os.name != 'nt' else 'cls')
                    continue

                print()
                print_info("Processando sua pergunta...")
                logger.debug(f"Query: {query}")

                result = qa_chain({"query": query})
                question_count += 1

                print()
                print_color("📝 Resposta:", Fore.CYAN, Style.BRIGHT)
                print_color("-" * 70, Fore.CYAN)
                print(result['result'])
                print_color("-" * 70, Fore.CYAN)

                # Show source documents
                if result.get('source_documents'):
                    num_sources = len(result['source_documents'])
                    print()
                    print_info(f"Baseado em {num_sources} documentos relevantes")
                    logger.debug(f"Sources: {[doc.metadata for doc in result['source_documents']]}")

                print()

            except KeyboardInterrupt:
                print()
                print_warning("Interrompido pelo usuário")
                logger.info(f"Session interrupted. {question_count} questions answered.")
                break
            except Exception as e:
                print()
                print_error(f"Erro ao processar pergunta: {str(e)}")
                logger.exception("Error processing question:")
                print_warning("Tente fazer a pergunta de outra forma.")
                print()

    except Exception as e:
        print()
        print_error(f"Erro fatal: {str(e)}")
        logger.exception("Fatal error:")
        sys.exit(1)

if __name__ == "__main__":
    main()
