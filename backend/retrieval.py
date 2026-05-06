import json
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from config import DATA_DIR, MOVIES_CSV_PATH, DOCUMENTS_PKL_PATH, CHUNKS_PKL_PATH


@dataclass
class Document:
    id: int
    contenu: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Chunk:
    chunk_id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

def parse_genres(genres_str: str) :
    #Parses a JSON string of genres into a list of genre names
    if not isinstance(genres_str, str):
        return []
    try:
        genres_list = json.loads(genres_str)
        return [genre['name'] for genre in genres_list if 'name' in genre]
    except (json.JSONDecodeError, TypeError):
        return []

def prepare_documents(file_path: Path = MOVIES_CSV_PATH) :
    #Loads movie data from a CSV file and transforms it into a list of Document objects.
    if not file_path.exists():
        print(f"File not found at {file_path}")
        return []

    
    df = pd.read_csv(file_path)
    documents = []

    for index, row in df.iterrows():
        try:
            release_year = pd.to_datetime(row['release_date']).year
        except (ValueError, TypeError):
            release_year = None

        doc = Document(
            id=index,
            contenu=row['overview'] if pd.notna(row['overview']) else "",
            metadata={
                "titre": row.get('title'),
                "annee": release_year,
                "link": row.get('homepage'),
                "note": row.get('vote_average'),
                "genres": parse_genres(row.get('genres', '[]'))
            }
        )
        documents.append(doc)

    
    return documents

def create_chunks(documents: List[Document]) :
    
    #Creates chunks from documents.
    #For this dataset, each document is treated as a single chunk as the content is small.
    #already checked and the max token count for the overview is around 250
    chunks = [
        Chunk(
            chunk_id=f"chunk_{doc.id}",
            text=doc.contenu,
            metadata=doc.metadata
        )
        for doc in documents
    ]
    
    return chunks

def load_or_create(pkl_path: Path, creation_func, *args, **kwargs) -> Any:
    
    #Loads an object from a pickle file if it exists else it creates it using the provided function and saves it to the pickle file.
 
    if pkl_path.exists():
        
        with open(pkl_path, 'rb') as f:
            return pickle.load(f)
    
    data = creation_func(*args, **kwargs)
    pkl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pkl_path, 'wb') as f:
        pickle.dump(data, f)
    
    return data

def main():
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    movie_documents = load_or_create(DOCUMENTS_PKL_PATH, prepare_documents, file_path=MOVIES_CSV_PATH)

    if movie_documents:
        print(f"Successfully loaded/prepared {len(movie_documents)} documents.")
        print("Example of a formatted document:\n" + json.dumps(movie_documents[0].__dict__, indent=2, ensure_ascii=False))
        movie_chunks = load_or_create(CHUNKS_PKL_PATH, create_chunks, documents=movie_documents)

        if movie_chunks:
            print(f"Successfully loaded/created {len(movie_chunks)} chunks.")
            print("Example of a formatted chunk:\n" + json.dumps(movie_chunks[20].__dict__, indent=2, ensure_ascii=False))
if __name__ == '__main__':
    main()