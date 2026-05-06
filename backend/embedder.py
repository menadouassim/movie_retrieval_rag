from vectordb import VectorDB
from pathlib import Path
import pickle
from dataclasses import dataclass, field
from typing import Any
from config import CHUNKS_PKL_PATH, DB_PATH, COLLECTION_NAME, MODEL_NAME



@dataclass
class Chunk:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    chunk_id: int = 0


def embed_and_store(pkl_path: str, db_path: str, collection_name: str):
    """Embeds chunks from a pickle file and stores them in the VectorDB."""
    vectordb = VectorDB(path=db_path, collection_name=collection_name, model_name=MODEL_NAME)
    
    if vectordb.collection.count() > 0:
        print("VectorDB already contains documents.")
        return

    with open(pkl_path, 'rb') as f:
        chunks = pickle.load(f)

    texts = [chunk.text for chunk in chunks]
    metadatas = []
    for chunk in chunks:
        meta = {"text": chunk.text}
        if isinstance(chunk.metadata, dict):
            # Flatten the metadata dictionary
            for key, value in chunk.metadata.items():
                if isinstance(value, list):
                    # Convert list to a string to be safe with chromadb
                    meta[key] = ", ".join(map(str, value))
                else:
                    meta[key] = value
        metadatas.append(meta)
    ids = [str(chunk.chunk_id) for chunk in chunks]

    # Add to the VectorDB
    vectordb.add(texts=texts, metadatas=metadatas, ids=ids)
    print(f"VectorDB created with {vectordb.collection.count()} documents.")


def search_in_db(question: str, db_path: str, collection_name: str, k: int = 4):
    """Searches for a question in the VectorDB."""
    vectordb = VectorDB(path=db_path, collection_name=collection_name, model_name=MODEL_NAME)
    results = vectordb.search(query_text=question, k=k)
    return results


if __name__ == "__main__":
    # 1. Embed chunks and store them in the VectorDB
    embed_and_store(pkl_path=CHUNKS_PKL_PATH, db_path=DB_PATH, collection_name=COLLECTION_NAME)

    # 2. Perform a search
    question = "a guy with spider abilities fights crime"
    search_results = search_in_db(question, db_path=DB_PATH, collection_name=COLLECTION_NAME, k=4)

    print(f"\nSearch results for: '{question}'")
    if search_results and search_results['documents']:
        for i, doc in enumerate(search_results['documents'][0]):
            metadata = search_results['metadatas'][0][i]
            distance = search_results['distances'][0][i]
            print(f"Content: {doc}")
            print(f"Metadata: {metadata}")
            print(f"Distance: {distance}")
            print("-" * 20)

