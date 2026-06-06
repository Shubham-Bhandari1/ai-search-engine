from elasticsearch import Elasticsearch
import mysql.connector

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql@2006",
    database="ai_search"
)

cursor = db.cursor(dictionary=True)

# Get all products from MySQL
cursor.execute("SELECT * FROM products")
products = cursor.fetchall()

# Create Elasticsearch index
if es.indices.exists(index="products"):
    es.indices.delete(index="products")
    print("Old index deleted")

es.indices.create(index="products", mappings={
    "properties": {
        "name":        { "type": "text" },
        "description": { "type": "text" },
        "category":    { "type": "keyword" },
        "brand":       { "type": "keyword" },
        "price":       { "type": "float" },
        "rating":      { "type": "float" }
    }
})
print("Index created")

# Load all products into Elasticsearch
for product in products:
    es.index(index="products", id=product["id"], document={
        "name":        product["name"],
        "description": product["description"],
        "category":    product["category"],
        "brand":       product["brand"],
        "price":       float(product["price"]),
        "rating":      float(product["rating"])
    })
    print(f"Indexed: {product['name']}")

cursor.close()
db.close()
print("All products loaded into Elasticsearch!")