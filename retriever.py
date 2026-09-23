## Responsible for taking user question, query embedding, FAISS search, relevant chunks

from pathlib import Path
import pickle

import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"  ## this is a huggingface model

BASE_DIR = Path(__file__).resolve().parent
STORE_DIR = BASE_DIR/ "store"
INDEX_PATH = STORE_DIR/ "faiss_index"
CHUNKS_PATH = STORE_DIR / "chunks"

## load the model

model = SentenceTransformer(MODEL_NAME)

## Retriever function

def retriever(query: str, k: int=5):
    """
    Retrieve the top-k document chunks relavant to a query.

    PARAMETERS:
    1. query: str
        User NL query
    
    2. k: int=5
        number of similar chunks to retrieve. by default we have kept the value as 5.

    RETURNS:
    1. return: list[str]
        The text content of the retrieved chunks.
    """

    ## STEP 1: Validation step
    if (
        not INDEX_PATH.exists()
        or not CHUNKS_PATH.exists()
    ):
        raise FileNotFoundError(
            "FAISS index or chunks are not found. Please run the ingestion process first"
        )
    
    ## STEP 2: load original document chunks
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
    
    index = faiss.read_index(
        str(INDEX_PATH)
    )

    ## STEP 3: Convert user query into embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy= True,
        normalize_embeddings= True,
        show_progress_bar= False
    ).astype("float32")

    ## STEP 4: Search FAISS
    ## FAIS compares the query against all the indexed document vectors

    distancs, indices = index.search(query_embedding, k)

    ## STEP 5: Convert vector ID's back to document chunks
    results = []

    for i in indices[0]:
        results.append(
            chunks[i].page_content
        )
    
    return results