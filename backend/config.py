from pathlib import Path
# Define constants for file paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHUNKS_PKL_PATH = DATA_DIR / "pkl/movie_chunks.pkl"
DB_PATH = str(DATA_DIR / "chroma_db")
COLLECTION_NAME = "movies"
MODEL_NAME = 'all-MiniLM-L6-v2'



# Define constants for file paths


MOVIES_CSV_PATH = DATA_DIR / "tmdb_5000_movies.csv"
DOCUMENTS_PKL_PATH = DATA_DIR / "pkl/movie_documents.pkl"
CHUNKS_PKL_PATH = DATA_DIR / "pkl/movie_chunks.pkl"