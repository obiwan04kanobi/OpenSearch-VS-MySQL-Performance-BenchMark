# OpenSearch vs MySQL Performance Benchmark

> A comprehensive performance comparison demonstrating when to use OpenSearch vs MySQL for search operations at scale.

[![AWS](https://img.shields.io/badge/AWS-EC2-orange)](https://aws.amazon.com/ec2/)
[![OpenSearch](https://img.shields.io/badge/OpenSearch-2.11.1-blue)](https://opensearch.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue)](https://www.mysql.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/)

## 📊 Benchmark Results

### 10,000 Records
![](/images/3.png)
----------------------
![](/images/2.png)

### 100,000 Records
![](/images/1.png)

**Key Insight**: OpenSearch maintains consistent sub-10ms performance while MySQL degrades 10x as dataset grows from 10K → 100K records.

## 🎯 What This Project Demonstrates

- **Infrastructure as Code**: Automated AWS infrastructure deployment
- **Database Performance Analysis**: Systematic benchmarking methodology
- **Technology Trade-offs**: When to choose search engines vs relational databases
- **Scalability Patterns**: How systems behave as data volume increases
- **SRE Best Practices**: Monitoring, testing, and infrastructure optimization

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     AWS EC2 Spot Instance           │
│   (t3.large - 8GB RAM, 2 vCPUs)     │
│                                      │
│  ┌──────────────┐  ┌──────────────┐│
│  │  OpenSearch  │  │   MySQL 8.0  ││
│  │    2.11.1    │  │   InnoDB     ││
│  │              │  │              ││
│  │  Port: 9200  │  │  Port: 3306  ││
│  └──────────────┘  └──────────────┘│
│                                      │
│  Python Benchmark Scripts            │
└─────────────────────────────────────┘
         │
         ↓
    SSM Access (No SSH)
```

**Technology Stack**:
- **Compute**: AWS EC2 Spot Instance (70% cost savings)
- **Search Engine**: OpenSearch 2.11.1 (single-node cluster)
- **Database**: MySQL 8.0 Community (with FULLTEXT indexes)
- **Language**: Python 3.9 with opensearch-py, pymysql, faker
- **IaC**: CloudFormation
- **Access**: AWS Systems Manager (SSM)

## 📋 Prerequisites

- AWS Account with EC2, VPC, and CloudFormation permissions
- AWS CLI installed and configured
- Session Manager plugin for AWS CLI
- Existing VPC and subnet

## 🚀 Quick Start

### 1. Deploy Infrastructure

```bash
# Clone the repository
git clone https://github.com/obiwan04kanobi/OpenSearch-VS-MySQL-Performance-BenchMark.git
cd OpenSearch-VS-MySQL-Performance-BenchMark

# Deploy CloudFormation stack
aws cloudformation create-stack \
  --stack-name opensearch-mysql-bench \
  --template-body file://infrastructure.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=vpc-xxxxxxxxx \
    ParameterKey=SubnetId,ParameterValue=subnet-xxxxxxxxx \
    ParameterKey=InstanceType,ParameterValue=t3.large \
    ParameterKey=MySQLRootPassword,ParameterValue=MySecurePass123! \
    ParameterKey=MySQLBenchPassword,ParameterValue=BenchPass123! \
  --capabilities CAPABILITY_IAM

# Wait for stack creation (takes 5-10 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name opensearch-mysql-bench

# Get instance ID
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name opensearch-mysql-bench \
  --query 'Stacks.Outputs[?OutputKey==`InstanceId`].OutputValue' \
  --output text)

echo "Instance ID: $INSTANCE_ID"
```

### 2. Connect to Instance

```bash
# Connect via SSM (no SSH key needed!)
aws ssm start-session --target $INSTANCE_ID
```

### 3. Install Python Dependencies

```bash
# Inside the EC2 instance
pip3 install opensearch-py pymysql faker
```

### 4. Run 10K Benchmark

```bash
# Generate 10,000 products (~30 seconds)
python3 generate_data.py -n 10000

# Load into OpenSearch
python3 load_opensearch.py -f products.json -i products

# Load into MySQL
python3 load_mysql.py -f products.json -t products

```


### 5. Run 100K Benchmark

```bash
# Generate 100,000 products (~2 minutes)
python3 generate_data.py -n 100000

# Load into OpenSearch
python3 load_opensearch.py -f products_large.json -i products_large

# Load into MySQL
python3 load_mysql.py -f products_large.json -t products_large

```

## 📁 Project Files

| File | Description |
|------|-------------|
| `generate_data.py` | Generate products with configurable size (CLI arg: -n) |
| `load_opensearch.py` | Bulk load products into OpenSearch (CLI args: -f, -i) |
| `load_mysql.py` | Batch insert products into MySQL (CLI args: -f, -t) |

## 🔍 Benchmark Queries

The benchmark tests real-world search scenarios:

### OpenSearch Queries
1. **Full-text search**: Match queries with relevance scoring
2. **Multi-field search**: Search across name and description
3. **Wildcard search**: Pattern matching (`*able*`)
4. **Filtered queries**: Boolean filters with category + price range
5. **Aggregations**: Category breakdown and statistics
6. **Complex aggregations**: Nested aggregations with multiple metrics
7. **Range queries**: Price range with sorting

### MySQL Queries
1. **FULLTEXT search**: `MATCH...AGAINST` syntax
2. **LIKE wildcard**: Pattern matching with `%`
3. **Indexed filters**: WHERE clauses on indexed columns
4. **GROUP BY aggregations**: Category statistics
5. **Range queries**: BETWEEN with ORDER BY

## 📈 Performance Insights

### Why OpenSearch Scales Better

1. **Inverted Index**: Pre-computed term → document mappings
2. **Horizontal Scalability**: Ready for sharding across nodes
3. **Query Caching**: Results and filter caches
4. **Document-Oriented**: No table scans required

### Why MySQL Struggles at Scale

1. **FULLTEXT limitations**: Less efficient than inverted indexes
2. **LIKE queries**: Require full table scans
3. **Row-based storage**: Must scan entire rows for text search
4. **Linear degradation**: Performance decreases with data growth

### When to Use Each

**Use OpenSearch when**:
- Building search features (autocomplete, faceted search, typeahead)
- Text-heavy queries across multiple fields
- Need relevance scoring and ranking
- Analyzing logs or time-series data
- Dataset > 100K records with heavy search traffic
- Fuzzy matching and typo tolerance required

**Use MySQL when**:
- Need ACID transactions and strong consistency
- Relational data with complex JOINs
- Simple lookups by ID or indexed columns
- Traditional CRUD operations
- Dataset < 10K records
- Transactional workloads

## 💰 Cost Analysis

Running this benchmark on AWS:

| Resource | Specification | Cost |
|----------|--------------|------|
| EC2 Spot Instance | t3.large | ~$0.03/hour (70% savings) |
| EBS Volume | 50GB gp3 | ~$4/month |
| Data Transfer | Within VPC | Free |
| **Total** | **Full benchmark** | **< $1** |

## 🧪 Test Data Schema

```json
{
  "id": 1,
  "name": "Innovative solution",
  "description": "Lorem ipsum dolor sit amet...",
  "category": "Electronics",
  "price": 299.99,
  "brand": "TechCorp Inc",
  "sku": "ABC-12345678",
  "created_at": "2024-06-15T10:30:00"
}
```

## 🛠️ Customization

### Change Dataset Size

Edit the generation scripts:
```python
# Generate any dataset size
python3 generate_data.py -n 50000
```

### Add Custom Queries

Add to benchmark scripts:
```python
test_queries.append({
    'name': 'Custom fuzzy search',
    'query': {
        'query': {
            'fuzzy': {
                'name': {'value': 'innovativ', 'fuzziness': 2}
            }
        }
    }
})
```

### Modify Instance Type

Update CloudFormation parameters:
```bash
--parameters ParameterKey=InstanceType,ParameterValue=m5.xlarge
```

## 🧹 Cleanup

Delete all AWS resources:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name opensearch-mysql-bench

# Verify deletion
aws cloudformation wait stack-delete-complete \
  --stack-name opensearch-mysql-bench
```

## What You'll Learn

- ✅ Setting up production-grade search infrastructure
- ✅ Performance testing methodology
- ✅ Database trade-off analysis
- ✅ CloudFormation/IaC best practices
- ✅ AWS EC2 Spot instances for cost optimization
- ✅ Python automation for DevOps/SRE tasks
- ✅ When to choose search engines vs databases

## License

MIT License - feel free to use for learning and portfolio projects

## Acknowledgments

- [OpenSearch Project](https://opensearch.org/) for the excellent search engine
- [AWS](https://aws.amazon.com/) for cost-effective spot instances
- [Faker](https://faker.readthedocs.io/) for realistic test data generation
