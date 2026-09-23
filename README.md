# Railway Returns & Refunds — RAG Chatbot

A **Retrieval-Augmented Generation (RAG)** chatbot designed to answer customer questions about railway **returns and refund policies** using information retrieved from a provided PDF document.

The project implements an end-to-end RAG pipeline:

**PDF → Document Loading → Chunking → Embeddings → FAISS Vector Database → Query Embedding → Similarity Search → Retrieved Context → Groq LLM → Grounded Answer**

The system is intentionally designed to keep the LLM grounded in the retrieved document context. When the required information is not present in the retrieved context, the system is instructed to respond with **`I DONT KNOW`** instead of inventing an answer.

---

## Features

- **PDF document ingestion** using `PyPDFLoader`
- **Text chunking** with `RecursiveCharacterTextSplitter`
- **Sentence embeddings** using the Hugging Face `all-MiniLM-L6-v2` model through `sentence-transformers`
- Local **FAISS vector database** for similarity search
- Retrieval of the **top 5 relevant chunks** for each user query
- **Groq LLM** integration for answer generation
- Environment-based API key configuration with **python-dotenv**
- CLI-based conversational interface
- Grounded-answer prompting designed to reduce unsupported responses and hallucinations
- Persistent local storage of the FAISS index and document chunks

---

## Project Objective

The objective is to build a simple customer-facing Q&A assistant for **Central Railways** that can answer questions related to **refund policies** from an authoritative PDF source.

Instead of sending a user question directly to an LLM, the application first searches the indexed document for relevant information. The retrieved information is then supplied to the LLM as context for answer generation.

This approach allows the application to use a domain-specific knowledge source without requiring the knowledge to be embedded directly into the model.

---

## Architecture

```text
                    ┌──────────────────────┐
                    │ Railway Refund PDF   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   PyPDFLoader        │
                    │  Document Loading     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ RecursiveCharacter   │
                    │ Text Splitter        │
                    │ chunk=500 / overlap50│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ SentenceTransformer  │
                    │ all-MiniLM-L6-v2     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FAISS           │
                    │   Vector Database    │
                    └──────────┬───────────┘
                               │
             User Question    │
                    │          │
                    ▼          │
          ┌────────────────┐   │
          │ Query Embedding│   │
          └───────┬────────┘   │
                  │            │
                  └──────┬─────┘
                         ▼
               ┌──────────────────┐
               │ Similarity Search│
               │    Top-K = 5     │
               └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │ Retrieved Context│
               └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │    Groq LLM      │
               │ Grounded Prompt  │
               └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │     Answer       │
               └──────────────────┘
```

---

## How the RAG Pipeline Works

### 1. Load the PDF

`ingest.py` scans the `data/` directory for PDF files and loads them using `PyPDFLoader`.

```python
loader = PyPDFLoader(str(file))
docs.extend(loader.load())
```

The current project contains:

```text
data/Railway-Returns-and-Refunds.pdf
```

---

### 2. Split the Document into Chunks

The loaded documents are divided into smaller pieces using `RecursiveCharacterTextSplitter`.

Current configuration:

```text
Chunk size:     500
Chunk overlap:   50
```

The overlap helps preserve contextual continuity between neighboring chunks.

---

### 3. Generate Embeddings

Each text chunk is converted into a numerical vector using:

```text
all-MiniLM-L6-v2
```

The model is loaded through `SentenceTransformer`.

Embeddings are generated with normalized vectors:

```python
model.encode(
    texts,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)
```

---

### 4. Store Vectors in FAISS

The generated vectors are stored in a local **FAISS** index using:

```python
faiss.IndexFlatIP(dim)
```

The project stores two artifacts:

```text
store/
├── faiss_index
└── chunks
```

`faiss_index` stores the vector index, while `chunks` contains the original LangChain document chunks serialized with `pickle`.

---

### 5. Embed the User Query

When the user enters a question, the same `all-MiniLM-L6-v2` embedding model converts the question into a vector.

This is important because the query and document chunks must be represented in the same embedding space for similarity search.

---

### 6. Retrieve Relevant Chunks

The query vector is searched against the FAISS index.

The retriever currently uses:

```python
retriever(query, k=5)
```

Therefore, the application retrieves the **top 5 most similar document chunks**.

---

### 7. Generate the Answer

The retrieved chunks and the user's question are passed to the Groq API.

The system prompt instructs the LLM to:

- Answer only using the supplied context
- Avoid inventing information
- Return **`I DONT KNOW`** when the answer is not available in the context

The current model is configured through the `MODEL_NAME` environment variable and defaults to:

```text
openai/gpt-oss-120b
```

---

## Project Structure

```text
rag-project-2-main/
│
├── data/
│   └── Railway-Returns-and-Refunds.pdf
│
├── store/
│   ├── chunks
│   └── faiss_index
│
├── ingest.py
├── retriever.py
├── rag_chain.py
├── main.py
├── requirements.txt
├── pyproject.toml
├── uv.lock
└── README.md
```

### File Responsibilities

| File / Directory | Purpose |
|---|---|
| `data/` | Contains source PDF documents |
| `store/` | Stores generated document chunks and FAISS index |
| `ingest.py` | Loads PDFs, chunks text, creates embeddings, and builds FAISS index |
| `retriever.py` | Embeds user queries and retrieves relevant chunks from FAISS |
| `rag_chain.py` | Combines retrieved context with the question and calls the Groq LLM |
| `main.py` | Provides the CLI chatbot interface |
| `requirements.txt` | Python dependencies |
| `pyproject.toml` | Project metadata and Python requirement |
| `uv.lock` | Dependency lock file |

---

## Technologies Used

### AI / Generative AI

- **Retrieval-Augmented Generation (RAG)**
- **Large Language Models (LLMs)**
- **Sentence Transformers**
- **Vector Embeddings**
- **Semantic Similarity Search**
- **Prompt Engineering**

### Frameworks & Libraries

- **LangChain Community**
- **LangChain Text Splitters**
- **FAISS**
- **PyPDF**
- **NumPy**
- **Groq Python SDK**
- **python-dotenv**

### Models

- **all-MiniLM-L6-v2** — document and query embeddings
- **openai/gpt-oss-120b** — default Groq generation model configured by the project

---

## Installation

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd rag-project-2-main
```

### 2. Create a Virtual Environment

Using Python's built-in virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The project's `requirements.txt` includes:

```text
langchain
langchain-community
langchain-text-splitters
faiss-cpu
sentence-transformers
pypdf
python-dotenv
groq
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
MODEL_NAME=openai/gpt-oss-120b
```

### Important Security Rule

Never commit `.env` or API keys to GitHub.

Add the following to `.gitignore`:

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
```

If an API key is accidentally pushed to GitHub, revoke/rotate the key immediately.

---

## Build the Vector Database

Before asking questions, the source documents must be ingested and indexed.

Run:

```bash
python ingest.py
```

The ingestion process will:

1. Find PDF files inside `data/`
2. Load the documents
3. Split documents into chunks
4. Generate embeddings using `all-MiniLM-L6-v2`
5. Create a FAISS index
6. Save the FAISS index to `store/faiss_index`
7. Save document chunks to `store/chunks`

You should see progress messages similar to:

```text
Loading..: Railway-Returns-and-Refunds.pdf
Loaded X document pages.
Split into X chunks.
Created embeddings for X chunks.
Processed X document pages into X chunks and stored into FAISS vector DB
```

The exact numbers depend on the source PDF.

---

## Run the Chatbot

Once the vector database has been created, run:

```bash
python main.py
```

The application starts a command-line chatbot.

Example:

```text
Hello from rag-project!

Ask a question: What is the refund policy?

Answer:
...
```

To stop the application:

```text
exit
```

or

```text
quit
```

---

## Example Query Flow

Suppose the user asks:

```text
What are the refund rules for a cancelled ticket?
```

The system performs the following steps:

```text
User Question
      ↓
Query Embedding
      ↓
FAISS Similarity Search
      ↓
Top 5 Relevant Chunks
      ↓
Context + Question
      ↓
Groq LLM
      ↓
Grounded Answer
```

The LLM does not receive the entire PDF directly. It receives the retrieved context selected by the vector search process.

---

## Detailed Code Flow

### `ingest.py`

Responsible for the **offline ingestion pipeline**:

```text
PDF
 ↓
PyPDFLoader
 ↓
LangChain Documents
 ↓
RecursiveCharacterTextSplitter
 ↓
Text Chunks
 ↓
SentenceTransformer
 ↓
Embeddings
 ↓
FAISS Index
```

### `retriever.py`

Responsible for **query-time retrieval**:

```text
User Query
 ↓
all-MiniLM-L6-v2
 ↓
Query Embedding
 ↓
FAISS Similarity Search
 ↓
Top-K Chunks
```

### `rag_chain.py`

Responsible for **retrieval + generation**:

```text
Query
 ↓
Retriever
 ↓
Relevant Context
 ↓
Prompt Construction
 ↓
Groq Chat Completion
 ↓
Answer
```

### `main.py`

Responsible for the **CLI interface** and repeatedly accepting user questions until `exit` or `quit` is entered.

---

## Why RAG?

A conventional LLM can answer questions based on its learned knowledge, but that knowledge may not contain the specific policies required by a particular organization.

This project uses **RAG** to connect an LLM to an external knowledge source:

```text
Knowledge Source
      ↓
   Retrieval
      ↓
 Relevant Context
      ↓
      LLM
      ↓
 Grounded Answer
```

This makes the application suitable for domain-specific Q&A scenarios where answers should be based on a controlled document collection.

---

## Grounding Strategy

The system prompt contains an explicit grounding instruction:

> Answer strictly only from the information provided in the context.

It also instructs the model to return:

```text
I DONT KNOW
```

when the requested answer cannot be found in the supplied context.

This is a simple **hallucination-reduction strategy**. It does not guarantee that an LLM will never produce an unsupported response, so retrieval quality and prompt design remain important.

---

## Configuration

### Change the LLM

The LLM model is controlled through:

```env
MODEL_NAME=openai/gpt-oss-120b
```

The value is passed to the Groq client in `rag_chain.py`.

### Change Number of Retrieved Chunks

The retriever currently defaults to five chunks:

```python
def retriever(query: str, k: int = 5):
```

You can experiment with different values of `k` depending on retrieval quality and context size.

### Change Chunk Size

Chunking is configured in `ingest.py`:

```python
RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

Changing chunk size or overlap requires rebuilding the FAISS index by running:

```bash
python ingest.py
```

---

## Troubleshooting

### `FAISS index or chunks are not found`

Run the ingestion pipeline first:

```bash
python ingest.py
```

Then start the chatbot:

```bash
python main.py
```

### `GROQ_API_KEY` error

Check that `.env` exists in the project root and contains a valid key:

```env
GROQ_API_KEY=your_groq_api_key
```

Also make sure `python-dotenv` is installed.

### Dependency installation problems

Make sure your virtual environment is active before running:

```bash
pip install -r requirements.txt
```

### Model download on first run

`all-MiniLM-L6-v2` is loaded through `sentence-transformers`. The embedding model may need to be downloaded the first time it is used.

### Retrieval quality is poor

Possible areas to experiment with include:

- **Chunk size**
- **Chunk overlap**
- Number of retrieved chunks (`k`)
- Source-document quality
- Embedding model
- Prompt design

After changing ingestion settings, rebuild the vector store with:

```bash
python ingest.py
```

---

## Current Limitations

This implementation is intentionally simple and has several limitations:

1. It currently operates through a **CLI interface** rather than a web UI.
2. The project indexes PDF documents found directly in the `data/` directory.
3. FAISS is used as a local vector index rather than a managed/vector database service.
4. The retriever uses a fixed default **top-K of 5** chunks.
5. There is no explicit retrieval score threshold or reranking stage.
6. The current implementation does not expose source citations in the generated answer.
7. The project is designed around the supplied railway refund-policy document rather than a broad multi-domain knowledge base.
8. The LLM is instructed to stay grounded, but prompt instructions alone cannot mathematically guarantee zero hallucinations.

---

## Possible Future Improvements

Potential extensions include:

- Add a **Streamlit** or **FastAPI** interface
- Display retrieved source chunks alongside answers
- Add document/page citations to responses
- Introduce a configurable **similarity threshold**
- Add a **reranking** stage after vector retrieval
- Support multiple document collections
- Add conversation history and session management
- Add evaluation for **retrieval accuracy** and **answer faithfulness**
- Use a production vector database such as a managed vector store
- Add automated document ingestion when new PDFs are uploaded
- Containerize the application with **Docker**
- Deploy the RAG application to **AWS**

---

## Security Considerations

- Keep API credentials in `.env` or another secure secret-management system.
- Never commit API keys to GitHub.
- Do not place sensitive customer information inside the repository.
- Review uploaded documents before indexing them into a production knowledge base.
- For production deployments, use appropriate IAM/secret-management controls and access restrictions.

---

## Learning Outcomes

This project demonstrates practical understanding of:

- **Retrieval-Augmented Generation (RAG)**
- **Document ingestion pipelines**
- **PDF processing**
- **Text chunking**
- **Vector embeddings**
- **FAISS vector search**
- **Semantic retrieval**
- **LLM integration**
- **Prompt engineering**
- **Grounded question answering**
- **Python project structuring**
- **Environment and API-key management**

---

## End-to-End Summary

```text
                    OFFLINE / INGESTION

PDF Documents
     │
     ▼
PyPDFLoader
     │
     ▼
Text Chunking
     │
     ▼
all-MiniLM-L6-v2
     │
     ▼
Vector Embeddings
     │
     ▼
FAISS Index ───────────────┐
     │                     │
     └── Stored Chunks ────┘
                           │
                           │
                    ONLINE / QUERY
                           │
User Question ─────────────┘
     │
     ▼
Query Embedding
     │
     ▼
FAISS Similarity Search
     │
     ▼
Top 5 Relevant Chunks
     │
     ▼
Context + User Question
     │
     ▼
Groq LLM
     │
     ▼
Grounded Answer
```

---

## Author

**Abhishek Kundley**  
AI / Generative AI Engineer

- **GitHub:** Add your GitHub profile URL
- **LinkedIn:** Add your LinkedIn profile URL

---

## License

Add an appropriate license before publishing the repository if you intend to distribute the project publicly.
