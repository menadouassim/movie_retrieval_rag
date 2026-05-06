import os

from typing import Optional
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()





class ContextManager:
    #Manages context file loading and caching

    def __init__(self, context_file: str = "context.txt"):
        self.context_file = Path(context_file)
        self._context_cache: Optional[str] = None

    @property
    def context(self) -> str:
        #Lazy load and cache context.
        if self._context_cache is None:
            self._context_cache = self._load_context()
        return self._context_cache

    def _load_context(self) -> str:
        #Load context from file, return empty string if not found.
        try:
            return self.context_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"Context file not found: {self.context_file}")
            return ""


class PromptBuilder:
    #Constructs RAG prompts from context and chunks

    @staticmethod
    def build(context: str, question: str, chunks: list[str]) -> str:
        #Build a prompt from context, question, and retrieved chunks.
        lines = [context, "", "Vector DB Chunks:"]
        lines.extend(f"- {chunk}" for chunk in chunks)
        lines.append(f"\nQuestion: {question}\nResponse:")
        return "\n".join(lines)


class GroqClient:
    #Groq API client for RAG-based conversational AI.

    MODEL = "openai/gpt-oss-20b"
    SYSTEM_ROLE = "assistant"

    def __init__(self, context_file: str = "context.txt", api_key: Optional[str] = None):
        
        key = api_key or os.environ.get("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        self.client = Groq(api_key=key)
        self.context_manager = ContextManager(context_file)
        self.history: list[dict] = []

    def generate(self, question: str, chunks: list[str]) :
       
        prompt = PromptBuilder.build(self.context_manager.context, question, chunks)
        self.history.append({"role": "user", "content": prompt})

        response = self._get_completion()
        self.history.append({"role": self.SYSTEM_ROLE, "content": response})

        return response

    def _get_completion(self) -> str:
        #Fetch completion from Groq API
        completion = self.client.chat.completions.create(
            messages=self.history,
            model=self.MODEL,
        )
        return completion.choices[0].message.content

    def reset_history(self) -> None:
        #Clear conversation history.
        self.history.clear()


def _format_search_results(documents: list[str], preview_length: int = 100, max_items: int = 3) -> str:
    #Format search results for display.
    lines = [f" Found {len(documents)} relevant chunks"]
    for i, doc in enumerate(documents[:max_items], 1):
        preview = doc[:preview_length] + "..." if len(doc) > preview_length else doc
        lines.append(f"  {i}. {preview}")
    return "\n".join(lines)


def _run_rag_demo(
    client: GroqClient,
    question: str,
    search_results: dict,
    ) :
    #Run RAG demonstration with given question and search results.
    if not search_results.get("documents") or not search_results["documents"][0]:
        print("No results found in vector database")
        return

    print(_format_search_results(search_results["documents"][0]))
    print("\n Generating response...")
    
    response = client.generate(question, search_results["documents"][0])
    print(f"\n Response:\n{response}")


def main() -> None:
    #Run RAG system demonstration.
    try:
        from embedder import search_in_db, embed_and_store
        from config import (
            DB_PATH,
            COLLECTION_NAME,
            CHUNKS_PKL_PATH,
            DOCUMENTS_PKL_PATH,
            MOVIES_CSV_PATH,
        )
        from retrieval import load_or_create, prepare_documents, create_chunks

        # Initialize client
        client = GroqClient(context_file="context.txt")
        print("GroqClient initialized successfully")

        # Load/create data pipeline
        print("Creating/loading chunks...")
        documents = load_or_create(
            DOCUMENTS_PKL_PATH, prepare_documents, file_path=MOVIES_CSV_PATH
        )
        print(f" Loaded/prepared {len(documents)} documents")

        chunks = load_or_create(CHUNKS_PKL_PATH, create_chunks, documents=documents)
        print(f" Loaded/created {len(chunks)} chunks")

        # Embed and store
        print(" Embedding and storing chunks...")
        embed_and_store(CHUNKS_PKL_PATH, DB_PATH, COLLECTION_NAME)

        # Demonstrate RAG with a test question
        test_question = "What are the movies with the spider suit?"
        print(f" Searching for: '{test_question}'")
        
        results = search_in_db(test_question, DB_PATH, COLLECTION_NAME, k=4)
        _run_rag_demo(client, test_question, results)

    except Exception as e:
        print(f"Error during RAG demo: {e}")
        raise


if __name__ == "__main__":
    
    main()
