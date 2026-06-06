from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
import mysql.connector

# Load the AI model
# This model converts text into numbers (vectors) that represent meaning
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql@2006",  # change this
        database="ai_search"
    )

def generate_embedding(text: str):
    # Converts any text into a list of 384 numbers that represent its meaning
    # Similar meanings = similar numbers
    embedding = model.encode(text)
    return embedding.tolist()

def setup_ai_index():
    # Delete old index if exists
    if es.indices.exists(index="products_ai"):
        es.indices.delete(index="products_ai")
        print("Old AI index deleted")

    # Create new index with vector search support
    es.indices.create(index="products_ai", mappings={
        "properties": {
            "name":        { "type": "text" },
            "description": { "type": "text" },
            "category":    { "type": "keyword" },
            "brand":       { "type": "keyword" },
            "price":       { "type": "float" },
            "rating":      { "type": "float" },
            "embedding": {
                # This stores the AI vector (384 numbers per product)
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"
            }
        }
    })
    print("AI index created")

    # Load products from MySQL
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Index each product with its AI embedding
    for product in products:
        # Combine name and description for better AI understanding
        text = f"{product['name']} {product['description']}"

        # Generate AI vector for this product
        embedding = generate_embedding(text)

        es.index(index="products_ai", id=product["id"], document={
            "name":        product["name"],
            "description": product["description"],
            "category":    product["category"],
            "brand":       product["brand"],
            "price":       float(product["price"]),
            "rating":      float(product["rating"]),
            "embedding":   embedding
        })
        print(f"AI indexed: {product['name']}")

    cursor.close()
    db.close()
    print("All products loaded with AI embeddings!")

def ai_search(query: str):
    # Convert the user's query into AI vector
    query_embedding = generate_embedding(query)

    # Search Elasticsearch using vector similarity
    # Finds products whose meaning is closest to the query meaning
    response = es.search(index="products_ai", body={
        "knn": {
            "field": "embedding",
            "query_vector": query_embedding,
            "k": 5,                    # return top 5 results
            "num_candidates": 50       # consider top 50 candidates
        }
    })

    # Format results
    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "id":          hit["_id"],
            "score":       hit["_score"],
            "name":        hit["_source"]["name"],
            "description": hit["_source"]["description"],
            "category":    hit["_source"]["category"],
            "brand":       hit["_source"]["brand"],
            "price":       hit["_source"]["price"],
            "rating":      hit["_source"]["rating"]
        })

    return results

# Run setup when this file is executed directly
if __name__ == "__main__":
    setup_ai_index()