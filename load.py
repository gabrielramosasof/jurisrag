import os
import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, Back, Style, init
from langchain_community.document_loaders import DirectoryLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from tqdm import tqdm

# Initialize colorama for cross-platform color support
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
    """Validate that all required environment variables and directories exist."""
    print_info("Validating environment...")

    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print_error("OpenAI API key not configured!")
        print_color("Please follow these steps:", Fore.YELLOW)
        print("1. Open the .env file in this directory")
        print("2. Replace 'your_openai_api_key_here' with your actual OpenAI API key")
        print("3. Get your API key from: https://platform.openai.com/api-keys")
        print("4. Save the .env file and run this script again")
        sys.exit(1)

    print_success("OpenAI API key found")
    logger.debug(f"API key starts with: {api_key[:20]}...")
    return True

def load_documents(data_dir="/Users/gabrielramos/Downloads/DRIVE_DO_BELISARIO"):
    """Load all .docx documents from the specified directory."""
    start_time = time.time()
    print_info(f"Loading documents from: {data_dir}")

    # Validate directory exists
    if not os.path.exists(data_dir):
        print_error(f"Directory not found: {data_dir}")
        print("Please verify the path exists and contains .docx files.")
        sys.exit(1)

    # Count files first for progress indication
    print_info("Scanning directory for .docx files...")
    docx_files = list(Path(data_dir).rglob("*.docx"))
    num_files = len(docx_files)

    if num_files == 0:
        print_error(f"No .docx files found in {data_dir}")
        print("Please verify the directory contains .docx documents.")
        sys.exit(1)

    print_success(f"Found {num_files} .docx files")
    logger.info(f"File list: {[str(f) for f in docx_files[:10]]}..." if num_files > 10 else f"Files: {docx_files}")

    try:
        loader = DirectoryLoader(
            data_dir,
            glob="**/*.docx",
            loader_cls=Docx2txtLoader,
            show_progress=True,
            use_multithreading=True
        )

        print_info("Loading document contents...")
        print_color("This may take several minutes for large document collections", Fore.YELLOW)

        documents = loader.load()

        elapsed = time.time() - start_time

        if not documents:
            print_warning("Files found but no content loaded")
            print("This may indicate issues with the .docx files.")
            sys.exit(1)

        print_success(f"Successfully loaded {len(documents)} documents in {elapsed:.2f}s")
        print_info(f"Average: {elapsed/len(documents):.3f}s per document")
        logger.info(f"Loaded {len(documents)} documents, total size: {sum(len(doc.page_content) for doc in documents)} characters")

        return documents

    except Exception as e:
        print_error(f"Error loading documents: {str(e)}")
        logger.exception("Full traceback:")
        print_color("\nTroubleshooting steps:", Fore.YELLOW)
        print("1. Verify all .docx files are valid and not corrupted")
        print("2. Check file permissions")
        print("3. Ensure docx2txt is installed: pip install docx2txt")
        sys.exit(1)

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into smaller chunks for embedding."""
    start_time = time.time()
    print_info("Splitting documents into chunks...")
    print_color(f"   Chunk size: {chunk_size} characters", Fore.CYAN)
    print_color(f"   Chunk overlap: {chunk_overlap} characters", Fore.CYAN)

    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        chunks = text_splitter.split_documents(documents)

        elapsed = time.time() - start_time

        if not chunks:
            print_error("No chunks created from documents")
            sys.exit(1)

        avg_chunks = len(chunks) / len(documents)
        print_success(f"Created {len(chunks)} chunks from {len(documents)} documents in {elapsed:.2f}s")
        print_info(f"Average: {avg_chunks:.1f} chunks per document")
        logger.info(f"Chunk sizes - min: {min(len(c.page_content) for c in chunks)}, max: {max(len(c.page_content) for c in chunks)}, avg: {sum(len(c.page_content) for c in chunks)/len(chunks):.0f}")

        return chunks

    except Exception as e:
        print_error(f"Error splitting documents: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)

def create_vectorstore(chunks):
    """Create FAISS vectorstore from document chunks using OpenAI embeddings."""
    start_time = time.time()
    print_info("Creating embeddings and vectorstore...")
    print_color(f"   Processing {len(chunks)} chunks", Fore.CYAN)
    print_warning("This may take several minutes and will consume OpenAI API credits")

    try:
        embeddings = OpenAIEmbeddings()

        # Create vectorstore with progress indication
        print_info("Generating embeddings from OpenAI...")
        print_color("   This is the slowest step - please be patient", Fore.YELLOW)

        vectorstore = FAISS.from_documents(chunks, embeddings)

        embedding_time = time.time() - start_time

        # Save vectorstore
        vectorstore_path = "vectorstore"
        print_info(f"Saving vectorstore to: {vectorstore_path}/")

        vectorstore.save_local(vectorstore_path)

        total_time = time.time() - start_time

        # Verify save was successful
        if os.path.exists(vectorstore_path) and os.path.isdir(vectorstore_path):
            files = os.listdir(vectorstore_path)
            file_sizes = sum(os.path.getsize(os.path.join(vectorstore_path, f)) for f in files if os.path.isfile(os.path.join(vectorstore_path, f)))
            print_success(f"Vectorstore saved successfully ({len(files)} files, {file_sizes/1024/1024:.2f} MB)")
            print_info(f"Embedding generation: {embedding_time:.2f}s ({len(chunks)/embedding_time:.2f} chunks/s)")
            print_info(f"Total time: {total_time:.2f}s")
            logger.info(f"Vectorstore created: {len(chunks)} chunks, {file_sizes} bytes, {total_time:.2f}s")
        else:
            print_warning("Vectorstore directory not found after save")

        return vectorstore

    except Exception as e:
        print_error(f"Error creating vectorstore: {str(e)}")
        logger.exception("Full traceback:")
        print_color("\nPossible causes:", Fore.YELLOW)
        print("1. Invalid OpenAI API key")
        print("2. Insufficient API credits")
        print("3. Network connectivity issues")
        print("4. Rate limiting from OpenAI")
        print("\nPlease check your OpenAI account and try again.")
        sys.exit(1)

if __name__ == "__main__":
    overall_start = time.time()

    print_header("📚 JURISRAG - Document Loading and Embedding Pipeline")
    print()
    logger.info("Starting document loading pipeline")

    try:
        # Validate environment
        validate_environment()
        print()

        # Load documents
        docs = load_documents()
        print()

        # Split into chunks
        chunks = split_documents(docs)
        print()

        # Create and save vectorstore
        vectorstore = create_vectorstore(chunks)
        print()

        overall_time = time.time() - overall_start

        print_header("🎉 SUCCESS! Vectorstore created and saved successfully")
        print()
        print_success(f"Total pipeline time: {overall_time:.2f}s ({overall_time/60:.2f} minutes)")
        print_color("\nStatistics:", Fore.CYAN, Style.BRIGHT)
        print(f"  • Documents processed: {len(docs)}")
        print(f"  • Chunks created: {len(chunks)}")
        print(f"  • Average chunks per doc: {len(chunks)/len(docs):.1f}")
        print(f"  • Processing speed: {len(docs)/(overall_time/60):.2f} docs/min")
        print()
        print_color("Next steps:", Fore.GREEN, Style.BRIGHT)
        print("1. Run 'python main.py' to start the interactive Q&A system")
        print("2. Ask questions about your legal documents")
        print()
        logger.info(f"Pipeline completed successfully in {overall_time:.2f}s")

    except KeyboardInterrupt:
        print()
        print_warning("Process interrupted by user")
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {str(e)}")
        logger.exception("Unexpected error - full traceback:")
        sys.exit(1)
