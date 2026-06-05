from fastapi import FastAPI
import mysql.connector

app = FastAPI()

# Database connection
def get_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql@2006", 
        database="ai_search"
    )
    return connection

@app.get("/")
def home():
    return {"message": "AI Search Engine is running!"}

@app.get("/search")
def search(q: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Search in name and description
    query = """
        SELECT * FROM products
        WHERE name LIKE %s
        OR description LIKE %s
        OR category LIKE %s
    """
    keyword = f"%{q}%"
    cursor.execute(query, (keyword, keyword, keyword))
    results = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }