# ImpactAnalyzer - Complete System

A comprehensive code impact analysis system with IntelliJ plugin integration, AI-powered analysis, and real-time frontend dashboard.

## 🏗️ System Architecture

### Backend Services (Python/FastAPI)
- **MS-Index** (Port 8001): Dependency graph indexing and vector embeddings
- **MS-MR** (Port 8002): Merge request analysis and impact assessment
- **MS-Common** (Port 8003): Frontend API gateway and data aggregation
- **MS-AI** (Port 8004): AI-powered analysis and reasoning engine

### Frontend (React/TypeScript)
- Real-time dashboard with live data from backend APIs
- Impact analysis visualization
- Test flow management interface
- Developer-focused code change analysis

### IntelliJ Plugin Integration
- **GraphNet Plugin**: https://github.com/Afzal-dev2/GraphNet
- Two-button functionality for dependency graph extraction and git diff analysis

### Demo Project
- **Target Repository**: https://github.com/sinnedpenguin/angular-springboot-ecommerce
- Angular + Spring Boot e-commerce application for testing impact analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Git

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Run setup script**
   ```bash
   python setup.py
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and API keys
   ```

4. **Start all services**
   ```bash
   python start_all_services.py
   ```

5. **Test services**
   ```bash
   python test_services.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Update API URLs if needed
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

### IntelliJ Plugin Setup

1. **Download GraphNet Plugin**
   - Visit: https://github.com/Afzal-dev2/GraphNet
   - Follow installation instructions

2. **Configure Plugin**
   - Set backend URL to `http://localhost:8001` for dependency graphs
   - Set MR analysis URL to `http://localhost:8002` for git diff analysis

## 📊 Usage Workflow

### 1. Dependency Graph Analysis
1. Open the demo project in IntelliJ: https://github.com/sinnedpenguin/angular-springboot-ecommerce
2. Use GraphNet plugin **Button 1** to extract and send dependency graph
3. Backend processes the graph, creates embeddings, and stores in vector database

### 2. Merge Request Analysis
1. Make code changes in the demo project
2. Create a merge request or use git diff
3. Use GraphNet plugin **Button 2** to send git diff for analysis
4. AI service analyzes impact and generates recommendations

### 3. Frontend Dashboard
1. View real-time statistics on the dashboard
2. Analyze impact maps and affected components
3. Monitor test flows and coverage metrics
4. Review code change details and recommendations

## 🔧 Configuration

### Environment Variables

**Frontend (.env)**
```bash
VITE_API_BASE_URL=http://localhost:8003
VITE_API_KEY=dev-key-123
```

**Backend (.env)**
```bash
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/impact_analyzer

# API Keys
OPENAI_API_KEY=your_openai_key_here
IMPACT_ANALYZER_API_KEY=dev-key-123

# Services
MS_INDEX_URL=http://localhost:8001
MS_MR_URL=http://localhost:8002
MS_COMMON_URL=http://localhost:8003
MS_AI_URL=http://localhost:8004
```

### Database Schema

The system automatically creates the following tables:
- `mr_table`: Merge request data and analysis results
- `test_flows_table`: Test flow definitions and status
- `daily_metrics_table`: Daily project metrics
- `changed_class_names`: Changed classes per MR
- `dependency_graph`: Dependency graph metadata
- `vector_metadata`: Vector embeddings metadata

## 🧪 Testing

### Backend Testing
```bash
cd backend
python test_services.py
```

### Frontend Testing
```bash
npm run test
```

### End-to-End Testing
1. Start all backend services
2. Start frontend development server
3. Use IntelliJ plugin with demo project
4. Verify data flow through the entire system

## 📚 API Documentation

### Key Endpoints

**MS-Common (Frontend API)**
- `GET /stats/yesterday` - Yesterday's statistics
- `GET /stats/current` - Current project statistics
- `GET /impact-map` - Impact analysis data
- `GET /test-flows` - Test flow information

**MS-Index (Dependency Analysis)**
- `POST /index/ingest-graph` - Ingest dependency graph
- `POST /index/rebuild-embeddings` - Rebuild embeddings

**MS-MR (Merge Request Analysis)**
- `POST /mr/analyze` - Analyze MR impact
- `GET /mr/{mr_id}/analysis` - Get analysis results

**MS-AI (AI Analysis)**
- `POST /analysis/impact` - Generate impact analysis
- `POST /analysis/test-coverage` - Analyze test coverage

See `docs/API_DOCUMENTATION.md` for complete API specifications.

## 🔍 Features

### AI-Powered Analysis
- **Impact Assessment**: Automatically identifies affected classes and modules
- **Severity Scoring**: Calculates impact severity (0-10 scale)
- **Test Recommendations**: Suggests relevant test flows to execute
- **Coverage Analysis**: Estimates code coverage impact

### Vector Embeddings
- **FAISS Integration**: Fast similarity search for code components
- **Semantic Analysis**: Understanding code relationships beyond syntax
- **Context-Aware**: Leverages historical change patterns

### Real-Time Dashboard
- **Live Statistics**: Real-time project metrics and trends
- **Impact Visualization**: Interactive impact maps and dependency graphs
- **Test Management**: Monitor and control test flow execution
- **Developer Tools**: Code change analysis and recommendations

### IntelliJ Integration
- **Seamless Workflow**: Direct integration with development environment
- **One-Click Analysis**: Extract dependency graphs and analyze changes
- **Automated Processing**: Background analysis without interrupting development

## 🛠️ Development

### Project Structure
```
impact-analyzer/
├── backend/
│   ├── ms_index/          # Dependency indexing service
│   ├── ms_mr/             # MR analysis service
│   ├── ms_common/         # Frontend API gateway
│   ├── ms_ai/             # AI analysis service
│   ├── shared/            # Shared models and utilities
│   └── docs/              # Documentation
├── src/                   # Frontend React application
├── plugin/                # IntelliJ plugin (external repo)
└── docs/                  # System documentation
```

### Adding New Features

1. **Backend Services**: Add new endpoints to appropriate microservice
2. **Frontend Components**: Create new React components and integrate with API
3. **Database Schema**: Update models in `shared/models.py`
4. **AI Prompts**: Enhance prompts in `ms_ai/services/`

## 🚨 Troubleshooting

### Common Issues

1. **Services Not Starting**
   - Check if ports 8001-8004 are available
   - Verify MySQL is running and accessible
   - Check Python dependencies are installed

2. **Frontend API Errors**
   - Ensure backend services are running
   - Verify API URLs in `.env` file
   - Check browser console for detailed errors

3. **Plugin Connection Issues**
   - Confirm backend services are accessible
   - Verify API keys match between plugin and backend
   - Check firewall settings

4. **Database Connection Errors**
   - Verify MySQL credentials in `.env`
   - Ensure database `impact_analyzer` exists
   - Check MySQL service is running

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python start_all_services.py
```

## 📈 Performance Considerations

### Production Deployment
- Use production-grade database (MySQL cluster)
- Implement Redis caching for frequent queries
- Add load balancer for multiple service instances
- Use environment-specific configuration

### Scaling
- Horizontal scaling of microservices
- Separate vector store service for large projects
- Async task queues for heavy operations
- CDN for frontend assets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **GraphNet Plugin**: https://github.com/Afzal-dev2/GraphNet
- **Demo Project**: https://github.com/sinnedpenguin/angular-springboot-ecommerce
- **OpenAI**: For AI-powered analysis capabilities
- **FAISS**: For efficient vector similarity search

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check service logs for detailed error messages
4. Create an issue in the repository

---

**Note**: This is a development system. For production use, implement proper security measures, monitoring, and deployment practices.