import faiss
import requests
import numpy as np

titles = [
    # AI & Machine Learning
    "Mind-Blowing New AI Model Revolutionizes Biology Research",
    "Novel Machine Learning Algorithm Changes Neuroscience Forever",
    "Deep Learning Networks Achieve Human-Level Image Recognition",
    "Transformer Models Transform Natural Language Processing",
    "AI-Powered Chatbots Revolutionize Customer Service Industry",
    "Computer Vision Breakthrough Enables Real-Time Medical Diagnosis",
    
    # Space & Astronomy
    "Scientists Discover Water on Mars: Implications for Future Missions",
    "James Webb Space Telescope Captures Most Distant Galaxy Ever",
    "SpaceX Successfully Lands Starship Prototype",
    "NASA Discovers Potentially Habitable Exoplanet 40 Light-Years Away",
    "China Achieves Historic Moon Landing on Far Side",
    
    # Quantum Computing
    "Breakthrough in Quantum Computing Achieved by Tech Giants",
    "Quantum Computers Solve Complex Problems in Minutes",
    "IBM Demonstrates Quantum Advantage Over Classical Computers",
    
    # Climate & Environment
    "Climate Change Effects Accelerating: New Study Reveals Alarming Trends",
    "Renewable Energy Sources Now Exceed Coal Power Globally",
    "Ocean Acidification Threatens Marine Ecosystems Worldwide",
    "Scientists Develop Carbon Capture Technology at Scale",
    
    # Biology & Medicine
    "CRISPR Gene Editing Cures Rare Genetic Diseases",
    "Researchers Discover New Cancer Treatment Using Immunotherapy",
    "mRNA Vaccine Technology Opens Door to New Therapeutics",
    "Brain Implant Allows Paralyzed Patient to Walk Again",
    "Breakthrough in Understanding Alzheimer's Disease Mechanisms",
    
    # Technology & Innovation
    "5G Networks Enable New Era of Internet Connectivity",
    "Graphene Materials Promise Revolutionary Tech Advances",
    "Brain-Computer Interface Technology Reaches New Heights",
    "Nanotechnology Breakthroughs in Drug Delivery Systems",
    
    # Physics
    "Gravitational Waves Detected Again, Confirming Einstein's Theory",
    "Scientists Achieve Nuclear Fusion Breakthrough",
    "Dark Matter Mystery Deepens with New Observations",
]

# Get the first embedding to determine dimension
print("Generating embeddings for titles...")
res = requests.post("http://localhost:11434/api/embeddings", json={
    "model": "phi3",
    "prompt": titles[0]
})
first_embedding = np.array(res.json()['embedding'], dtype='float32')
d = len(first_embedding)
print(f"Detected embedding dimension: {d}\n")

# Build the index with L2 distance
index = faiss.IndexFlatL2(d)

X = np.zeros(shape=(len(titles), d), dtype='float32')
X[0] = first_embedding
print(f"✓ Embedded: {titles[0][:50]}...")

# Continue with remaining titles
for i, title in enumerate(titles[1:], start=1):
    res = requests.post("http://localhost:11434/api/embeddings", json={
        "model": "phi3",
        "prompt": title
    })
    embedding = res.json()['embedding']
    X[i] = np.array(embedding, dtype='float32')
    print(f"✓ Embedded: {title[:50]}...")

index.add(X)
print(f"\n✓ Index built with {index.ntotal} vectors\n")


def search(query, k=3):
    """Search the index for similar titles"""
    print(f"Searching for: '{query}'")
    
    res = requests.post("http://localhost:11434/api/embeddings", json={
        "model": "phi3",
        "prompt": query
    })
    query_embedding = np.array(res.json()['embedding'], dtype='float32')
    
    # Search the index
    distances, indices = index.search(np.array([query_embedding]), k=k)
    
    print(f"\nTop {k} results:\n")
    for rank, (idx, distance) in enumerate(zip(indices[0], distances[0]), 1):
        similarity = 1 / (1 + distance)  # Convert distance to similarity score
        print(f"{rank}. {titles[idx]}")
        print(f"   Distance: {distance:.4f} | Similarity: {similarity:.4f}\n")
    
    return indices[0], distances[0]


if __name__ == "__main__":
    # Test different types of queries
    queries = [
        'recent advancements in ai for biology',
        'space exploration and missions',
        'quantum computing breakthroughs',
        'climate change and renewable energy',
        'medical treatments and health',
    ]
    
    for query in queries:
        search(query, k=3)
        print("-" * 80 + "\n")