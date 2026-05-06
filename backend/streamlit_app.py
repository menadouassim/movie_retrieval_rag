import streamlit as st
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

try:
    from embedder import search_in_db
    from config import DB_PATH, COLLECTION_NAME
    from rag import GroqClient
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    st.error(f"Failed to load required modules: {e}")
    st.stop()


st.set_page_config(
    page_title="CINÉMA — Movie Search",
    page_icon="🎞",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #e8e0d4;
    }
    .stApp {
        background-color: #0c0b09;
        background-image:
            url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #111009 !important;
        border-right: 1px solid #2a2720;
    }
    [data-testid="stSidebar"] * { color: #a89f90 !important; }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #e8e0d4 !important;
        font-family: 'Playfair Display', serif !important;
        letter-spacing: 0.05em;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 13px;
        line-height: 1.8;
        color: #7a7268 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #2a2720 !important;
    }

    /* ── Slider ── */
    [data-testid="stSlider"] .stSlider > div > div {
        background: #3d3830 !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
        background: #c9a84c !important;
        border-color: #c9a84c !important;
    }

    /* ── Checkbox ── */
    [data-testid="stCheckbox"] label { color: #a89f90 !important; }

    /* ── Main header ── */
    .cinema-header {
        text-align: center;
        padding: 3rem 0 1rem;
        position: relative;
    }
    .cinema-eyebrow {
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.35em;
        color: #c9a84c;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .cinema-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(3rem, 7vw, 5.5rem);
        font-weight: 900;
        font-style: italic;
        line-height: 0.95;
        color: #f0e8da;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .cinema-title span { color: #c9a84c; }
    .cinema-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 14px;
        color: #5c5650;
        margin-top: 1rem;
        letter-spacing: 0.04em;
    }
    .cinema-rule {
        border: none;
        border-top: 1px solid #2a2720;
        margin: 2rem 0;
    }

    /* ── Search area ── */
    .stTextInput > div > div {
        background-color: #1a1814 !important;
        border: 1px solid #3a3630 !important;
        border-radius: 2px !important;
        color: #e8e0d4 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 15px !important;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div:focus-within {
        border-color: #c9a84c !important;
        box-shadow: 0 0 0 1px #c9a84c22 !important;
    }
    .stTextInput input { color: #e8e0d4 !important; }
    .stTextInput input::placeholder { color: #4a4640 !important; }
    .stTextInput label { display: none !important; }

    /* ── Button ── */
    .stButton > button {
        background-color: #c9a84c !important;
        color: #0c0b09 !important;
        border: none !important;
        border-radius: 2px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        letter-spacing: 0.2em !important;
        text-transform: uppercase !important;
        padding: 0.6rem 1.2rem !important;
        height: 100% !important;
        transition: background-color 0.2s, transform 0.1s !important;
    }
    .stButton > button:hover {
        background-color: #e0bc60 !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Movie card ── */
    .movie-card {
        border-top: 1px solid #2a2720;
        padding: 2rem 0;
        display: grid;
        grid-template-columns: 3rem 1fr auto;
        gap: 1.5rem;
        align-items: start;
        transition: background 0.2s;
    }
    .movie-rank {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #2a2720;
        line-height: 1;
        padding-top: 0.2rem;
        text-align: right;
    }
    .movie-main {}
    .movie-title-text {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #f0e8da;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }
    .movie-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin: 0.6rem 0;
    }
    .pill {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #a89f90;
        background: #1e1c18;
        border: 1px solid #2a2720;
        padding: 3px 10px;
        border-radius: 2px;
    }
    .pill-gold {
        color: #c9a84c;
        border-color: #c9a84c44;
        background: #c9a84c0d;
    }
    .movie-overview {
        font-size: 13px;
        line-height: 1.75;
        color: #7a7268;
        margin-top: 0.75rem;
        font-style: italic;
        max-width: 65ch;
    }
    .movie-score-wrap {
        text-align: center;
        min-width: 70px;
    }
    .score-number {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 900;
        line-height: 1;
    }
    .score-label {
        font-family: 'DM Mono', monospace;
        font-size: 9px;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #5c5650;
        margin-top: 2px;
    }

    /* ── AI response ── */
    .ai-block {
        border: 1px solid #2a2720;
        border-left: 3px solid #c9a84c;
        background: #111009;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 0 2px 2px 0;
    }
    .ai-label {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.3em;
        color: #c9a84c;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }
    .ai-text {
        font-size: 14px;
        line-height: 1.8;
        color: #a89f90;
    }

    /* ── Stats ── */
    .stat-block {
        border: 1px solid #2a2720;
        padding: 1.5rem;
        text-align: center;
        background: #111009;
    }
    .stat-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        font-weight: 900;
        color: #f0e8da;
        line-height: 1;
    }
    .stat-label {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #5c5650;
        margin-top: 0.4rem;
    }

    /* ── Section headers ── */
    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.35em;
        text-transform: uppercase;
        color: #5c5650;
        margin-bottom: 0.25rem;
    }
    .section-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #e8e0d4;
        margin: 0;
    }

    /* ── Hints ── */
    .hint-chip {
        display: inline-block;
        font-family: 'DM Sans', sans-serif;
        font-size: 12px;
        color: #7a7268;
        background: #1a1814;
        border: 1px solid #2a2720;
        border-radius: 2px;
        padding: 5px 12px;
        margin: 3px;
        cursor: default;
        transition: border-color 0.2s, color 0.2s;
    }
    .hint-chip:hover {
        border-color: #c9a84c44;
        color: #c9a84c;
    }

    /* ── No results ── */
    .empty-state {
        text-align: center;
        padding: 4rem 0;
        color: #3a3630;
    }
    .empty-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .empty-text {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.1rem;
    }

    /* ── Spinner / alerts ── */
    .stSpinner > div { border-top-color: #c9a84c !important; }
    .stAlert { background: #1a1814 !important; border-color: #2a2720 !important; }
    [data-testid="stMetric"] { background: #111009; padding: 1rem; border: 1px solid #2a2720; }
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        color: #f0e8da !important;
    }
    [data-testid="stMetricLabel"] {
        font-family: 'DM Mono', monospace !important;
        font-size: 10px !important;
        letter-spacing: 0.2em !important;
        text-transform: uppercase !important;
        color: #5c5650 !important;
    }

    /* ── Divider ── */
    hr { border-color: #1e1c18 !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_rag_client():
    try:
        client = GroqClient(context_file="context.txt")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize RAG client: {e}")
        st.warning(f"⚠️ RAG client unavailable. Running in search-only mode.\n{e}")
        return None


def format_metadata(metadata: Dict[str, Any]) -> Dict[str, str]:
    formatted = {}
    if "titre" in metadata:
        formatted["Title"] = str(metadata["titre"])
    if "annee" in metadata:
        formatted["Year"] = str(metadata["annee"]) if metadata["annee"] else "Unknown"
    if "note" in metadata:
        formatted["Rating"] = f"{metadata['note']}/10" if metadata["note"] else "N/A"
    if "genres" in metadata and metadata["genres"]:
        formatted["Genres"] = metadata["genres"]
    if "link" in metadata and metadata["link"]:
        formatted["Homepage"] = metadata["link"]
    return formatted


def get_score_color(pct: float) -> str:
    if pct >= 80:
        return "#c9a84c"
    elif pct >= 60:
        return "#a89f90"
    else:
        return "#5c5650"


def display_movie_card(metadata: Dict[str, Any], overview: str, distance: float, rank: int):
    fmt = format_metadata(metadata)
    similarity_pct = max(0, min(100, (1 - distance) * 100))
    color = get_score_color(similarity_pct)
    title = fmt.get("Title", "Unknown")
    year = fmt.get("Year", "")
    rating = fmt.get("Rating", "")
    genres = fmt.get("Genres", [])
    homepage = fmt.get("Homepage", "")

    pills_html = ""
    if year:
        pills_html += f'<span class="pill">{year}</span>'
    if rating and rating != "N/A":
        pills_html += f'<span class="pill pill-gold">★ {rating}</span>'
    if isinstance(genres, list):
        for g in genres[:4]:
            pills_html += f'<span class="pill">{g}</span>'

    # Separator line above card
    st.markdown('<div style="border-top:1px solid #2a2720;margin:0.5rem 0;"></div>', unsafe_allow_html=True)

    col_rank, col_main, col_score = st.columns([1, 10, 2])

    with col_rank:
        st.markdown(
            f'<div class="movie-rank">{rank:02d}</div>',
            unsafe_allow_html=True
        )

    with col_main:
        st.markdown(
            f'<div class="movie-title-text">{title}</div>'
            f'<div class="movie-pills">{pills_html}</div>'
            f'<div class="movie-overview">{overview if overview else "No overview available."}</div>',
            unsafe_allow_html=True
        )
        if homepage:
            st.markdown(
                f'<a href="{homepage}" target="_blank" style="font-family:\'DM Mono\',monospace;font-size:10px;'
                f'letter-spacing:0.15em;color:#c9a84c;text-decoration:none;display:inline-block;margin-top:0.4rem;">'
                f'VIEW PAGE \u2192</a>',
                unsafe_allow_html=True
            )

    with col_score:
        st.markdown(
            f'<div class="movie-score-wrap">'
            f'<div class="score-number" style="color:{color}">{similarity_pct:.0f}</div>'
            f'<div class="score-label">match %</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def search_movies(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    try:
        results = search_in_db(query, DB_PATH, COLLECTION_NAME, k=num_results)
        if not results or not results.get("documents") or not results["documents"][0]:
            return []
        formatted = []
        for i, doc in enumerate(results["documents"][0]):
            formatted.append({
                "overview": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "rank": i + 1
            })
        return formatted
    except Exception as e:
        logger.error(f"Search error: {e}")
        st.error(f"❌ Search error: {e}")
        return []


def load_database_stats() -> Dict[str, Any]:
    try:
        from config import DOCUMENTS_PKL_PATH
        import pickle
        if DOCUMENTS_PKL_PATH.exists():
            with open(DOCUMENTS_PKL_PATH, 'rb') as f:
                documents = pickle.load(f)
            all_genres = set()
            for doc in documents:
                if "genres" in doc.metadata:
                    all_genres.update(doc.metadata["genres"])
            ratings = [doc.metadata.get("note") for doc in documents if doc.metadata.get("note")]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            return {
                "total_movies": len(documents),
                "unique_genres": len(all_genres),
                "avg_rating": avg_rating
            }
    except Exception as e:
        logger.error(f"Stats error: {e}")
    return None


EXAMPLE_QUERIES = [
    "A loner receives a letter that changes his fate forever",
    "Two strangers fall in love across an impossible distance",
    "A city slowly realises something is terribly wrong",
    "One man must outrun the clock to save everyone he loves",
    "A quiet town hides a secret beneath its surface",
    "She discovers she was never who she thought she was",
    "An unlikely crew sets off on a journey with no return",
    "The past refuses to stay buried",
    "A child sees what the adults refuse to believe",
    "They had one night to pull off the impossible",
]


def main():
    # ── Sidebar ──────────────────────────────────────────
    with st.sidebar:
        st.markdown("## Settings")
        num_results = st.slider(
            "Results to retrieve",
            min_value=1, max_value=10, value=5,
            help="Number of movies returned per search"
        )
        use_ai_response = st.checkbox("Generate AI Analysis", value=True)

        st.markdown("---")
        st.markdown("### Hints")
        st.markdown(
            "<p style='font-size:12px;color:#5c5650!important;line-height:1.7;'>Not sure what to search for? Try describing a feeling, a premise, or a mood.</p>",
            unsafe_allow_html=True
        )
        for q in EXAMPLE_QUERIES:
            st.markdown(f"<span style='font-size:12px;color:#5c5650;display:block;padding:3px 0;border-top:1px solid #1e1c18;'>\u201c{q}\u201d</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "<p>Semantic vector search over a curated movie database. Describe any mood, premise, or feeling — the engine finds what fits.</p>",
            unsafe_allow_html=True
        )

    # ── Header ───────────────────────────────────────────
    st.markdown("""
    <div class="cinema-header">
        <div class="cinema-eyebrow">Semantic Movie Discovery</div>
        <h1 class="cinema-title">C<span>I</span>NÉM<span>A</span></h1>
        <p class="cinema-subtitle">Describe a feeling. Find the film.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="cinema-rule">', unsafe_allow_html=True)

    # ── Search bar ───────────────────────────────────────
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        query = st.text_input(
            "query",
            placeholder="A soldier wanders a ruined world looking for his son…",
            label_visibility="collapsed"
        )
    with col_btn:
        search_button = st.button("SEARCH")

    # ── Hint chips ───────────────────────────────────────
    hints_html = "".join(f'<span class="hint-chip">{q}</span>' for q in EXAMPLE_QUERIES[:6])
    st.markdown(f'<div style="margin-top:0.75rem">{hints_html}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="cinema-rule">', unsafe_allow_html=True)

    # ── Results ──────────────────────────────────────────
    if search_button and query:
        with st.spinner("Searching the archive…"):
            results = search_movies(query, num_results=num_results)

        if results:
            st.markdown(f"""
            <div style="margin-bottom:0.5rem">
                <div class="section-label">Search results</div>
                <div class="section-title">{len(results)} film{"s" if len(results) != 1 else ""} found</div>
            </div>
            """, unsafe_allow_html=True)

            for result in results:
                display_movie_card(
                    result["metadata"],
                    result["overview"],
                    result["distance"],
                    result["rank"]
                )

            # ── AI Response ──────────────────────────────
            if use_ai_response:
                rag_client = initialize_rag_client()
                if rag_client:
                    try:
                        with st.spinner("Composing analysis…"):
                            overviews = [r["overview"] for r in results]
                            response = rag_client.generate(query, overviews)
                            rag_client.reset_history()

                        st.markdown(f"""
                        <div class="ai-block">
                            <div class="ai-label">✦ AI Curator Note</div>
                            <div class="ai-text">{response}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        logger.error(f"AI response error: {e}")
                        st.error(f"Could not generate AI response: {e}")

        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🎞</div>
                <div class="empty-text">No films matched that description.<br>Try different words or a different feeling.</div>
            </div>
            """, unsafe_allow_html=True)

    elif search_button and not query:
        st.warning("Please enter something to search for.")

    # ── Stats ─────────────────────────────────────────────
    st.markdown('<hr class="cinema-rule">', unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:1.25rem">
        <div class="section-label">The Archive</div>
        <div class="section-title">Database</div>
    </div>
    """, unsafe_allow_html=True)

    stats = load_database_stats()
    if stats:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-block"><div class="stat-value">{stats["total_movies"]:,}</div><div class="stat-label">Films Indexed</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-block"><div class="stat-value">{stats["unique_genres"]}</div><div class="stat-label">Unique Genres</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-block"><div class="stat-value">{stats["avg_rating"]:.1f}</div><div class="stat-label">Avg. Rating / 10</div></div>', unsafe_allow_html=True)
    else:
        st.info("Database statistics unavailable.")


if __name__ == "__main__":
    main()