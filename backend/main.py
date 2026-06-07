from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import Elasticsearch
from ai_search import ai_search, generate_embedding
import mysql.connector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

es = Elasticsearch("http://localhost:9200")

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql@2006",
        database="ai_search"
    )

@app.get("/")
def home():
    return {"message": "AI Search Engine is running!"}

@app.get("/search")
def search(q: str):
    response = es.search(index="products", body={
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["name", "description", "category", "brand"],
                "fuzziness": "AUTO"
            }
        }
    })

    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "id":    hit["_id"],
            "score": hit["_score"],
            **hit["_source"]
        })

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }

@app.get("/ai-search")
def smart_search(q: str):
    results = ai_search(q)
    return {
        "query": q,
        "type": "AI Semantic Search",
        "total_results": len(results),
        "results": results
    }

@app.get("/hybrid-search")
def hybrid_search(q: str):
    # Step 1 — Keyword search
    keyword_response = es.search(index="products", body={
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["name^3", "description", "category^2", "brand"],
                "fuzziness": "AUTO"
            }
        },
        "size": 20
    })

    # Step 2 — AI semantic search
    query_embedding = generate_embedding(q)

    ai_response = es.search(index="products_ai", body={
        "knn": {
            "field": "embedding",
            "query_vector": query_embedding,
            "k": 20,
            "num_candidates": 100
        }
    })

    # Step 3 — Merge both results
    combined = {}

    # Add keyword results
    for hit in keyword_response["hits"]["hits"]:
        pid = hit["_id"]
        combined[pid] = {
            "id": pid,
            "keyword_score": hit["_score"],
            "ai_score": 0,
            **hit["_source"]
        }

    # Add AI results
    for hit in ai_response["hits"]["hits"]:
        pid = hit["_id"]
        # Skip weak AI matches below 30% similarity
        if hit["_score"] < 0.3:
            continue
        if pid in combined:
            combined[pid]["ai_score"] = hit["_score"]
        else:
            combined[pid] = {
                "id": pid,
                "keyword_score": 0,
                "ai_score": hit["_score"],
                **hit["_source"]
            }

    # Step 4 — Calculate final score (50% keyword + 50% AI)
    for pid in combined:
        keyword = combined[pid]["keyword_score"]
        ai = combined[pid]["ai_score"]
        combined[pid]["final_score"] = (0.5 * keyword) + (0.5 * ai)

    # Step 5 — Sort by final score and return top 20
    results = sorted(
        combined.values(),
        key=lambda x: x["final_score"],
        reverse=True
    )[:20]

    return {
        "query": q,
        "type": "Hybrid Search",
        "total_results": len(results),
        "results": results
    }