# 🎞 CINÉMA — Movie RAG Search Engine

A semantic movie search engine that lets you describe a feeling, a premise, or a vague memory — and finds the film. Powered by vector embeddings + Retrieval-Augmented Generation (RAG) via Groq.

---

## How It Works

### The Pipeline

```
movies.csv
    │
    ▼
retrieval.py        → loads and prepares movie documents from the CSV
    │
    ▼
embedder.py         → chunks documents, generates vector embeddings,
                      stores them in a local ChromaDB vector database
    │
    ▼
ChromaDB (local)    → persisted on disk, queried at search time
    │
    ▼
streamlit_app.py    → takes a user query, embeds it, finds the closest
                      matching movies by vector similarity
    │
    ▼
rag.py (GroqClient) → feeds the retrieved movie overviews + the query
                      into a Groq LLM to generate a curator-style analysis
```

### Key Concepts

**Vector Embeddings** — Each movie overview is converted into a numerical vector that captures its semantic meaning. When you search, your query is embedded the same way, and the database finds movies whose vectors are closest to yours. This means searches like *"a soldier lost in a ruined world"* can match films without those exact words.

**RAG (Retrieval-Augmented Generation)** — Rather than asking an LLM to recall movies from memory (which leads to hallucinations), the app first retrieves real movies from the database, then passes those overviews as context to the LLM. The model only analyses what was actually found.

**ChromaDB** — A lightweight, file-based vector database that persists to disk. On first run it is built from scratch; on subsequent runs it is loaded instantly without re-embedding.

---

## Project Structure

```
movie_retrieval_rag/
├── backend/
│   ├── streamlit_app.py   # Main UI — run this to launch the app
│   ├── rag.py             # GroqClient, PromptBuilder, CLI demo entry point
│   ├── embedder.py        # Embedding logic + ChromaDB read/write
│   ├── retrieval.py       # CSV loading, document prep, chunking
│   ├── config.py          # Paths and collection name constants
│   ├── context.txt        # System prompt / persona fed to the LLM
│   └── data/
│       └── movies.csv     # Source movie dataset
```

---

## Requirements

- Python 3.10+
- A [Groq API key](https://console.groq.com) (free tier available)

---

## Setup

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd movie_retrieval_rag/backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you hit a `torchvision` error, install the CPU-only build (lighter and sufficient for embeddings):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 4. Set your Groq API key

Create a `.env` file in the directory:

```
GROQ_API_KEY=your_key_here
```

---

## Running the App

### Streamlit UI (recommended)

```bash
streamlit run streamlit_app.py
```

On first launch, the app will automatically build the vector database from `movies.csv` — this takes a minute or two. Every subsequent launch skips this step and starts instantly.

### CLI demo (rag.py)

Runs a hardcoded test query end-to-end in the terminal, also auto-building the DB if needed:

```bash
python rag.py
```

---

## Using the App

1. Open the browser tab that Streamlit launches (usually `http://localhost:8501`)
2. Type anything in the search bar — a mood, a plot premise, a character type, a feeling
3. Adjust **Results to retrieve** in the sidebar (1–10) to control how many films appear
4. Toggle **Generate AI Analysis** to get a short curator note about the results
5. Each result shows the film's title, year, rating, genres, match percentage, and overview

### Search tips

The search understands meaning, not just keywords. Try things like:

- *"A loner receives a letter that changes his fate forever"*
- *"Two strangers fall in love across an impossible distance"*
- *"A quiet town hides a secret beneath its surface"*
- *"They had one night to pull off the impossible"*

---

## Configuration

All file paths and the ChromaDB collection name live in `config.py`. Edit there if you move files or rename the dataset.

`context.txt` controls the personality and instructions given to the LLM when generating the AI analysis. Edit it to change the tone or focus of the curator responses.

