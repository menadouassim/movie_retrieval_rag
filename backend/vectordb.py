import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from typing import List, Dict, Any

class VectorDB:
    def __init__(self, path: str, collection_name: str, model_name: str):
        self.client = chromadb.PersistentClient(path=path)
        embedding_function = SentenceTransformerEmbeddingFunction(model_name=model_name)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )

    def add(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query_text: str, k: int = 5) :
        results = self.collection.query(
            query_texts=[query_text],
            n_results=k
        )
        return results

    def get_all_documents(self) :
        return self.collection.get()

    def clear(self):
        self.client.delete_collection(name=self.collection.name)

   
