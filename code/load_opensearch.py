from opensearchpy import OpenSearch, helpers
import json
import time
import argparse

client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True,
    use_ssl=False,
    verify_certs=False
)

def create_index(index_name='products'):
    """Create index with mappings"""
    if client.indices.exists(index=index_name):
        print(f"Deleting existing index: {index_name}")
        client.indices.delete(index=index_name)
    
    index_body = {
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'refresh_interval': '30s'
        },
        'mappings': {
            'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'text', 'analyzer': 'standard'},
                'description': {'type': 'text', 'analyzer': 'standard'},
                'category': {'type': 'keyword'},
                'price': {'type': 'float'},
                'brand': {'type': 'keyword'},
                'sku': {'type': 'keyword'},
                'created_at': {'type': 'date'}
            }
        }
    }
    
    client.indices.create(index=index_name, body=index_body)
    print(f"✓ Created index: {index_name}")

def bulk_load_data(filename='products.json', index_name='products'):
    """Bulk load data into OpenSearch"""
    print(f"Loading data from {filename}...")
    with open(filename, 'r') as f:
        products = json.load(f)
    
    actions = [
        {
            '_index': index_name,
            '_id': product['id'],
            '_source': product
        }
        for product in products
    ]
    
    print(f"Starting bulk insert of {len(actions)} documents...")
    start_time = time.time()
    
    success, failed = helpers.bulk(client, actions, chunk_size=1000, raise_on_error=False)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"✓ Successfully indexed: {success}")
    print(f"✓ Failed: {len(failed) if failed else 0}")
    print(f"✓ Time taken: {elapsed:.2f} seconds")
    print(f"✓ Throughput: {success/elapsed:.0f} docs/sec")
    
    client.indices.refresh(index=index_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load data into OpenSearch')
    parser.add_argument('-f', '--file', type=str, default='products.json',
                        help='Input JSON file (default: products.json)')
    parser.add_argument('-i', '--index', type=str, default='products',
                        help='OpenSearch index name (default: products)')
    
    args = parser.parse_args()
    
    create_index(args.index)
    bulk_load_data(args.file, args.index)
    
    print("\n✓ Index stats:")
    print(client.cat.count(index=args.index, format='json'))
