from faker import Faker
import json
import argparse

fake = Faker()
Faker.seed(42)

def generate_products(num_records=10000):
    """Generate sample product data for benchmarking"""
    print(f"Generating {num_records} products...")
    products = []
    
    for i in range(num_records):
        if i % 10000 == 0 and i > 0:
            print(f"Generated {i}/{num_records}...")
        
        product = {
            'id': i + 1,
            'name': fake.catch_phrase(),
            'description': fake.text(max_nb_chars=500),
            'category': fake.random_element(['Electronics', 'Clothing', 'Food', 'Books', 'Home']),
            'price': round(fake.random.uniform(10, 1000), 2),
            'brand': fake.company(),
            'sku': fake.bothify(text='???-########'),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now').isoformat()
        }
        products.append(product)
    
    # Determine output filename based on size
    if num_records <= 10000:
        filename = 'products.json'
    else:
        filename = 'products_large.json'
    
    print(f"Saving to {filename}...")
    with open(filename, 'w') as f:
        json.dump(products, f, indent=2)
    
    print(f"✓ Successfully generated {num_records} products")
    print(f"✓ Saved to {filename}")
    return products

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate product data for benchmarking')
    parser.add_argument('-n', '--num-records', type=int, default=10000,
                        help='Number of records to generate (default: 10000)')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output filename (default: auto-determined)')
    
    args = parser.parse_args()
    generate_products(args.num_records)
