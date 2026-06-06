import csv
import mysql.connector
import re

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql@2006",  # change this
    database="ai_search"
)
cursor = db.cursor()

# Add image_url column if it doesn't exist
try:
    cursor.execute("ALTER TABLE products ADD COLUMN image_url VARCHAR(500)")
    db.commit()
    print("Added image_url column")
except:
    print("image_url column already exists")

# Clear existing sample data
cursor.execute("DELETE FROM products")
db.commit()
print("Cleared old sample data")

# Clean price function
# CSV has prices like "₹999" or "1,299" — we need just the number
def clean_price(price_str):
    if not price_str:
        return 0.0
    # Remove currency symbols, commas, spaces
    cleaned = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(cleaned)
    except:
        return 0.0

# Clean rating function
# CSV has ratings like "4.5" or "4,5" or "NA"
def clean_rating(rating_str):
    if not rating_str or rating_str == "NA":
        return 0.0
    cleaned = rating_str.replace(',', '.')
    try:
        return float(cleaned)
    except:
        return 0.0

# Clean category function
# CSV has categories like "Electronics|Headphones|Over-Ear"
# We just want the first part "Electronics"
def clean_category(category_str):
    if not category_str:
        return "General"
    return category_str.split('|')[0].strip()

# Load CSV and insert into MySQL
count = 0
skipped = 0

with open('../data/amazon.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        name        = row['product_name'][:255]  # max 255 chars
        description = row['about_product']
        category    = clean_category(row['category'])
        price       = clean_price(row['discounted_price'])
        rating      = clean_rating(row['rating'])
        image_url   = row['img_link']

        # Skip rows with missing important data
        if not name or not description:
            skipped += 1
            continue

        cursor.execute("""
            INSERT INTO products 
            (name, description, category, price, rating, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, description, category, price, rating, image_url))

        count += 1
        if count % 100 == 0:
            db.commit()  # commit every 100 rows for speed
            print(f"Loaded {count} products...")

db.commit()
cursor.close()
db.close()

print(f"Done! Loaded {count} products, skipped {skipped} incomplete rows")