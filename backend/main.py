from fastapi import FastAPI
from elasticsearch import Elasticsearch
from ai_search import ai_search, generate_embedding
import mysql.connector

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    # ↑ Allows React (port 3000) to talk to FastAPI (port 8000)
    allow_methods=["*"],   # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers
)

es = Elasticsearch("http://localhost:9200")

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql@2006",  # change this
        database="ai_search"
    )

@app.get("/")
def home():
    return {"message": "AI Search Engine is running!"}

@app.get("/search")
def search(q: str):
    # Normal Elasticsearch keyword search
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
    # AI powered semantic search
    results = ai_search(q)

    return {
        "query": q,
        "type": "AI Semantic Search",
        "total_results": len(results),
        "results": results
    }