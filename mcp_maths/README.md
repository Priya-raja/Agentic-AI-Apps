# Semantic Search with FAISS & Ollama: A RAG Foundation

A practical implementation of semantic search using vector embeddings and FAISS indexing. This project demonstrates the **retrieval** component of RAG (Retrieval-Augmented Generation) systems.

## 🎯 What This Does

Converts text documents into semantic vectors, indexes them with FAISS, and enables intelligent similarity-based search. Unlike keyword matching, this finds semantically related content even with different wording.

**Example:**
- Query: `"AI for biology"`
- Finds: `"Machine Learning in Neuroscience"`, `"Deep Learning for Medical Diagnosis"`
- Why: All are semantically similar in vector space

## 🧠 Key Concepts

### Vector Embeddings
Text → 3072-dimensional vector using Ollama's phi3 model. Similar texts produce similar vectors.

### Semantic Space
Higher dimensions allow capturing complex semantic relationships. Distance between vectors = semantic similarity.

### FAISS Index
Fast similarity search library that efficiently finds nearest neighbors in high-dimensional space.

### RAG Pipeline
```
Retrieval (this project) → Augmented Context → Generation (LLM)
```

## 📋 Prerequisites

- Python 3.8+
- Ollama running locally on port 11434
- Phi3 model downloaded in Ollama

## 🚀 Installation

**1. Clone the repository:**
```bash
git clone <your-repo>
cd mcp_maths
```

**2. Create virtual environment:**
```bash
python -m venv mcp_maths
source mcp_maths/bin/activate  # Mac/Linux
# or
mcp_maths\Scripts\activate  # Windows
```

**3. Install dependencies:**
```bash
pip install faiss-cpu requests numpy
```

Or with uv:
```bash
uv pip install faiss-cpu requests numpy
```

**4. Start Ollama:**
```bash
ollama serve
# In another terminal:
ollama pull phi3
```

## 💻 Usage

**Run semantic search:**
```bash
python ollama-embedding-model.py
```

**Output example:**
```
Generating embeddings for titles...
Detected embedding dimension: 3072
✓ Index built with 34 vectors

Searching for: 'AI for biology'
Top 3 results:

1. Novel Machine Learning Algorithm Changes Neuroscience Forever
   Distance: 1668.1989 | Similarity: 0.0006

2. Mind-Blowing New AI Model Revolutionizes Biology Research
   Distance: 1764.5807 | Similarity: 0.0006

3. Breakthrough in Quantum Computing Achieved by Tech Giants
   Distance: 2165.3535 | Similarity: 0.0005
```

**Add custom searches:**
```python
from faiss_search import search

# Search for anything
search('quantum computing applications', k=5)
search('renewable energy innovations', k=3)
```

## 📊 How It Works

### Step 1: Embed Documents
```python
# Convert text → vector
response = requests.post("http://localhost:11434/api/embeddings", json={
    "model": "phi3",
    "prompt": "Your text here"
})
embedding = response.json()['embedding']  # 3072-dim vector
```

### Step 2: Index with FAISS
```python
# Store all vectors in efficient index
index = faiss.IndexFlatL2(3072)
index.add(embeddings)  # Super fast nearest neighbor search
```

### Step 3: Search
```python
# Query vector finds closest documents
distances, indices = index.search(query_vector, k=3)
# Returns indices of 3 most similar documents
```

## 🔬 Understanding the Numbers

**Distance:** L2 Euclidean distance in 3072D space
- Smaller = more similar
- Example: 1668 vs 2165 → first result is more relevant

**Similarity Score:** `1 / (1 + distance)`
- Converts distance to 0-1 scale
- Higher = more similar

## 🎓 Project Structure

```
embedding-model/
├── faiss_search.py      # Main semantic search engine
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## 📈 Next Steps: Building RAG

Extend this to a full RAG pipeline:

```python
def rag_query(question, k=3):
    """Retrieve docs, then augment LLM context"""
    # Step 1: Retrieve relevant docs
    indices, distances = search(question, k=k)
    
    # Step 2: Build context
    context = "\n".join([titles[idx] for idx in indices])
    
    # Step 3: Augment LLM prompt
    rag_prompt = f"""Based on these documents:
{context}

Answer: {question}"""
    
    return rag_prompt
```

## 🛠️ Customization

**Add more documents:**
```python
titles = [
    "Your document 1",
    "Your document 2",
    "...",
]
```

**Change number of results:**
```python
search("query", k=10)  # Top 10 instead of 3
```

**Use different Ollama models:**
```python
"model": "mistral"  # or any model in your Ollama
```

**Persist index to disk:**
```python
faiss.write_index(index, "my_index.faiss")
index = faiss.read_index("my_index.faiss")
```

## ⚙️ Technical Details

- **Embedding Model:** Ollama Phi3 (3072 dimensions)
- **Distance Metric:** L2 Euclidean
- **Index Type:** FAISS IndexFlatL2
- **Documents:** 34 sample titles across 6 domains

## 🤔 Common Issues

**ModuleNotFoundError: No module named 'faiss'**
```bash
pip install faiss-cpu
```

**Connection refused (Ollama not running)**
```bash
ollama serve
```

**Dimension mismatch**
Code auto-detects embedding dimension from first embedding.

## 📚 Learn More

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Ollama](https://ollama.ai)
- [RAG Systems](https://docs.langchain.com/use_cases/qa_answering/getting_started)
- [Vector Embeddings](https://platform.openai.com/docs/guides/embeddings)

## 🎯 Use Cases

✅ Document search & recommendation  
✅ Content discovery  
✅ Question answering (with RAG)  
✅ Semantic text analysis  
✅ Duplicate detection  
✅ Knowledge base retrieval  

## 📝 License

Open source - feel free to use and modify

## 🤝 Contributing

Found a bug or want to improve? Feel free to submit issues or PRs!

---

**Built with:** Python • FAISS • Ollama • Vector Embeddings