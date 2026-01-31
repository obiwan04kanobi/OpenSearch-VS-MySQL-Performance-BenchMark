import pymysql
import json
import time
import argparse

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'benchuser',
    'password': 'BenchPass123!',
    'database': 'testdb'
}

def create_table(table_name='products'):
    """Create products table with indexes"""
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            id INT PRIMARY KEY,
            name VARCHAR(255),
            description TEXT,
            category VARCHAR(50),
            price DECIMAL(10,2),
            brand VARCHAR(100),
            sku VARCHAR(50),
            created_at DATETIME,
            FULLTEXT idx_name_desc (name, description),
            FULLTEXT idx_name (name),
            FULLTEXT idx_description (description),
            INDEX idx_category (category),
            INDEX idx_price (price),
            INDEX idx_created (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✓ Table '{table_name}' created with FULLTEXT indexes")

def load_data(filename='products.json', table_name='products'):
    """Load data into MySQL"""
    print(f"Loading data from {filename}...")
    with open(filename, 'r') as f:
        products = json.load(f)
    
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    start_time = time.time()
    
    insert_query = f"""
        INSERT INTO {table_name} (id, name, description, category, price, brand, sku, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    batch_size = 1000
    for i in range(0, len(products), batch_size):
        batch = products[i:i+batch_size]
        values = [
            (p['id'], p['name'], p['description'], p['category'], 
             p['price'], p['brand'], p['sku'], p['created_at'])
            for p in batch
        ]
        cursor.executemany(insert_query, values)
        conn.commit()
        
        if i % 10000 == 0 or i + batch_size >= len(products):
            print(f"Inserted {min(i+batch_size, len(products))}/{len(products)} records...")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    
    print(f"\n✓ Successfully loaded {count} products")
    print(f"✓ Total time: {elapsed:.2f} seconds")
    print(f"✓ Throughput: {count/elapsed:.0f} docs/sec")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load data into MySQL')
    parser.add_argument('-f', '--file', type=str, default='products.json',
                        help='Input JSON file (default: products.json)')
    parser.add_argument('-t', '--table', type=str, default='products',
                        help='MySQL table name (default: products)')
    
    args = parser.parse_args()
    
    create_table(args.table)
    load_data(args.file, args.table)
