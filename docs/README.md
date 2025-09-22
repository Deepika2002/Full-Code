# ImpactAnalyzer Backend System

A comprehensive backend system for analyzing code impact and automating test flows in software development projects.

## Architecture Overview

The system consists of four microservices:

- **MS-Index**: Dependency graph indexing and vector embeddings
- **MS-MR**: Merge request analysis and impact assessment  
- **MS-Common**: Frontend API gateway and data aggregation
- **MS-AI**: AI-powered analysis and reasoning engine

## Quick Start

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd impact-analyzer/backend
   ```

2. **Run setup script**
   ```bash
   python setup.py
   ```

3. **Update environment variables**
   ```bash
   # Edit .env file with your actual credentials
   nano .env
   ```

4. **Start all services**
   ```bash
   python start_all_services.py
   ```

5. **Test the services**
   ```bash
   python test_services.py
   ```

## Service Details

### MS-Index (Port 8001)
- **Purpose**: Ingest dependency graphs, clone repositories, generate embeddings
- **Key Endpoints**:
  - `POST /index/ingest-graph` - Ingest dependency graph from IntelliJ plugin
  - `POST /index/rebuild-embeddings` - Rebuild embeddings for a project

### MS-MR (Port 8002)  
- **Purpose**: Analyze merge requests for impact assessment
- **Key Endpoints**:
  - `POST /mr/analyze` - Analyze MR impact using git diff
  - `GET /mr/{mr_id}/analysis` - Get analysis results

### MS-Common (Port 8003)
- **Purpose**: Frontend-facing API gateway
- **Key Endpoints**:
  - `GET /stats/yesterday` - Yesterday's statistics
  - `GET /stats/current` - Current project statistics
  - `GET /impact-map` - Impact analysis data
  - `GET /test-flows` - Test flow information

### MS-AI (Port 8004)
- **Purpose**: AI-powered analysis engine
- **Key Endpoints**:
  - `POST /analysis/impact` - Generate impact analysis
  - `POST /analysis/test-coverage` - Analyze test coverage

## Database Schema

### Core Tables

- **MRTable**: Merge request data and analysis results
- **TestFlowsTable**: Test flow definitions and status
- **DailyMetricsTable**: Daily project metrics
- **ChangedClassNames**: Changed classes per MR
- **DependencyGraph**: Dependency graph metadata
- **VectorMetadata**: Vector embeddings metadata

## IntelliJ Plugin Integration

The system integrates with the GraphNet IntelliJ plugin:

### Button 1: Generate Dependency Graph
- Extracts project dependency structure
- Sends to `POST /index/ingest-graph`
- Creates vector embeddings for similarity search

### Button 2: Send Git Diff
- Captures git diff and MR metadata
- Sends to `POST /mr/analyze`
- Triggers AI-powered impact analysis

## Frontend Integration

Update the existing React frontend to consume backend APIs:

```javascript
// Replace static data with API calls
const API_BASE_URL = 'http://localhost:8003';

// Example: Get yesterday's stats
const response = await fetch(`${API_BASE_URL}/stats/yesterday`);
const data = await response.json();
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/impact_analyzer

# API Keys  
OPENAI_API_KEY=your_openai_key_here
IMPACT_ANALYZER_API_KEY=dev-key-123

# Vector Store
VECTOR_STORE_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Service URLs
MS_INDEX_URL=http://localhost:8001
MS_MR_URL=http://localhost:8002
MS_COMMON_URL=http://localhost:8003
MS_AI_URL=http://localhost:8004
```

## Development Workflow

1. **Start Services**: Use `python start_all_services.py`
2. **Test Plugin**: Use GraphNet plugin buttons in IntelliJ
3. **Verify Data**: Check MySQL database for stored results
4. **Test Frontend**: Update frontend to consume APIs
5. **Monitor Logs**: Check service logs for debugging

## API Authentication

All endpoints support optional API key authentication:

```bash
curl -H "X-Impact-Analyzer-Api-Key: dev-key-123" \
     http://localhost:8003/stats/current
```

## Testing

### Unit Tests
```bash
# Run tests for each service
cd ms_index && python -m pytest tests/
cd ms_mr && python -m pytest tests/
cd ms_common && python -m pytest tests/
cd ms_ai && python -m pytest tests/
```

### Integration Tests
```bash
# Run full integration test suite
python test_services.py
```

### End-to-End Testing

1. Use IntelliJ plugin to send dependency graph
2. Create a test MR and send git diff
3. Verify data appears in frontend
4. Check database for stored analysis

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure MySQL is running
   - Check DATABASE_URL in .env
   - Verify database exists

2. **Vector Embeddings Not Working**
   - Check if sentence-transformers is installed
   - Verify VECTOR_STORE_PATH is writable
   - Falls back to mock embeddings if model fails

3. **AI Analysis Failing**
   - Check OPENAI_API_KEY is set
   - Verify API key has sufficient credits
   - Falls back to mock analysis if API fails

4. **Plugin Connection Issues**
   - Ensure services are running on correct ports
   - Check firewall settings
   - Verify API key matches

### Logs

Service logs are written to stdout. For persistent logging:

```bash
# Start with log files
python start_all_services.py > logs/services.log 2>&1 &
```

## Production Deployment

### Security Considerations

1. **Change default API keys**
2. **Use environment-specific database credentials**
3. **Enable HTTPS for production**
4. **Implement rate limiting**
5. **Add input validation and sanitization**

### Scaling Considerations

1. **Database connection pooling**
2. **Redis for caching**
3. **Load balancer for multiple instances**
4. **Separate vector store service**
5. **Async task queues for heavy operations**

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## License

[Your License Here]