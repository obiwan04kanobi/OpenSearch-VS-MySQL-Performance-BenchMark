from opensearchpy import OpenSearch
import pymysql
import time
import statistics
import argparse

# ---------- Config ----------

# MySQL connection
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'benchuser',
    'password': 'BenchPass123!',
    'database': 'testdb',
}

# OpenSearch client
os_client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True,
    use_ssl=False,
    verify_certs=False,
)


# ---------- OpenSearch benchmark ----------

def benchmark_opensearch(index_name: str):
    print("\n" + "=" * 70)
    print(f"OPENSEARCH BENCHMARKS (index: {index_name})")
    print("=" * 70 + "\n")

    test_queries = [
        {
            'name': 'Full-text search (single term)',
            'query': {'query': {'match': {'description': 'innovative'}}},
        },
        {
            'name': 'Full-text search (multi-word)',
            'query': {'query': {'match': {'description': 'innovative technology solution'}}},
        },
        {
            'name': 'Multi-field search',
            'query': {
                'query': {
                    'multi_match': {
                        'query': 'technology',
                        'fields': ['name^2', 'description'],
                    }
                }
            },
        },
        {
            'name': 'Wildcard search',
            'query': {'query': {'wildcard': {'name': '*able*'}}},
        },
        {
            'name': 'Filter by category + price range',
            'query': {
                'query': {
                    'bool': {
                        'filter': [
                            {'term': {'category': 'Electronics'}},
                            {'range': {'price': {'gte': 100, 'lte': 500}}},
                        ]
                    }
                }
            },
        },
        {
            'name': 'Aggregation: Category breakdown',
            'query': {
                'size': 0,
                'aggs': {
                    'categories': {
                        'terms': {'field': 'category', 'size': 10},
                    }
                },
            },
        },
        {
            'name': 'Aggregation: Price stats by category',
            'query': {
                'size': 0,
                'aggs': {
                    'categories': {
                        'terms': {'field': 'category'},
                        'aggs': {
                            'avg_price': {'avg': {'field': 'price'}},
                            'max_price': {'max': {'field': 'price'}},
                        },
                    }
                },
            },
        },
        {
            'name': 'Range query with sorting',
            'query': {
                'query': {'range': {'price': {'gte': 50, 'lte': 200}}},
                'sort': [{'price': 'desc'}],
                'size': 100,
            },
        },
    ]

    results = []

    for test in test_queries:
        times = []
        hits = 0
        for _ in range(10):
            start = time.time()
            resp = os_client.search(index=index_name, body=test['query'])
            end = time.time()
            times.append((end - start) * 1000)
            hits = resp['hits']['total']['value']

        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)

        results.append(
            {
                'query': test['name'],
                'avg_ms': round(avg_time, 2),
                'min_ms': round(min_time, 2),
                'max_ms': round(max_time, 2),
                'hits': hits,
            }
        )

        print(f"{test['name']:<45}")
        print(
            f"  Avg: {avg_time:7.2f}ms | Min: {min_time:7.2f}ms | "
            f"Max: {max_time:7.2f}ms | Hits: {hits:6}"
        )

    return results


# ---------- MySQL benchmark ----------

def benchmark_mysql(table_name: str):
    print("\n" + "=" * 70)
    print(f"MYSQL BENCHMARKS (table: {table_name})")
    print("=" * 70 + "\n")

    test_queries = [
        {
            'name': 'Full-text search (single term)',
            'query': f"""
                SELECT * FROM {table_name}
                WHERE MATCH(description)
                AGAINST('innovative' IN NATURAL LANGUAGE MODE)
            """,
        },
        {
            'name': 'Full-text search (multi-word)',
            'query': f"""
                SELECT * FROM {table_name}
                WHERE MATCH(description)
                AGAINST('innovative technology solution' IN NATURAL LANGUAGE MODE)
            """,
        },
        {
            'name': 'Full-text multi-field search',
            'query': f"""
                SELECT * FROM {table_name}
                WHERE MATCH(name, description)
                AGAINST('technology' IN NATURAL LANGUAGE MODE)
            """,
        },
        {
            'name': 'LIKE wildcard search',
            'query': f"""
                SELECT * FROM {table_name}
                WHERE name LIKE '%able%'
            """,
        },
        {
            'name': 'Filter by category + price range',
            'query': f"""
                SELECT * FROM {table_name}
                WHERE category = 'Electronics'
                  AND price >= 100
                  AND price <= 500
            """,
        },
        {
            'name': 'Aggregation: Category breakdown',
            'query': f"""
                SELECT category, COUNT(*) AS count
                FROM {table_name}
                GROUP BY category
            """,
        },
        {
            'name': 'Aggregation: Price stats by category',
            'query': f"""
                SELECT category,
                       AVG(price) AS avg_price,
                       MAX(price) AS max_price
                FROM {table_name}
                GROUP BY category
            """,
        },
        {
            'name': 'Range query with sorting',
            'query': f"""
                SELECT *
                FROM {table_name}
                WHERE price >= 50
                  AND price <= 200
                ORDER BY price DESC
                LIMIT 100
            """,
        },
    ]

    results = []

    for test in test_queries:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        times = []
        row_count = 0
        for _ in range(10):
            start = time.time()
            cursor.execute(test['query'])
            rows = cursor.fetchall()
            end = time.time()
            times.append((end - start) * 1000)
            row_count = len(rows)

        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)

        results.append(
            {
                'query': test['name'],
                'avg_ms': round(avg_time, 2),
                'min_ms': round(min_time, 2),
                'max_ms': round(max_time, 2),
                'hits': row_count,
            }
        )

        print(f"{test['name']:<45}")
        print(
            f"  Avg: {avg_time:7.2f}ms | Min: {min_time:7.2f}ms | "
            f"Max: {max_time:7.2f}ms | Hits: {row_count:6}"
        )

        cursor.close()
        conn.close()

    return results


# ---------- Comparison ----------

def compare_results(os_results, mysql_results, dataset_label: str):
    print("\n" + "=" * 70)
    print(f"PERFORMANCE COMPARISON ({dataset_label})")
    print("=" * 70 + "\n")
    print(f"{'Query Type':<45} {'OpenSearch':<15} {'MySQL':<15} {'Winner'}")
    print("-" * 95)

    for i in range(min(len(os_results), len(mysql_results))):
        os_time = os_results[i]['avg_ms']
        my_time = mysql_results[i]['avg_ms']

        if os_time < my_time:
            winner = f"OpenSearch ({my_time / os_time:.1f}x faster)"
        elif my_time < os_time:
            winner = f"MySQL ({os_time / my_time:.1f}x faster)"
        else:
            winner = "Tie"

        print(
            f"{os_results[i]['query']:<45} "
            f"{os_time:>10.2f}ms    {my_time:>10.2f}ms    {winner}"
        )


# ---------- CLI entrypoint ----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark OpenSearch vs MySQL for any dataset size."
    )
    parser.add_argument(
        "--os-index",
        default="products",
        help="OpenSearch index name (default: products)",
    )
    parser.add_argument(
        "--mysql-table",
        default="products",
        help="MySQL table name (default: products)",
    )
    parser.add_argument(
        "--label",
        default="custom dataset",
        help="Label to show in comparison header (e.g. '10K records')",
    )

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("OPENSEARCH vs MYSQL PERFORMANCE BENCHMARK")
    print(f"Dataset: {args.label}")
    print("=" * 70)

    os_results = benchmark_opensearch(args.os_index)
    mysql_results = benchmark_mysql(args.mysql_table)
    compare_results(os_results, mysql_results, args.label)
