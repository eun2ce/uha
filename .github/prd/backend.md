# UHA Backend Development Context

## 🏗️ Architecture Overview

### Clean Architecture / DDD Pattern
```
src/uha/backend/
├── entities/          # Domain entities (Pydantic models)
│   ├── stream.py      # Stream aggregate root
│   ├── youtube.py     # YouTube video entities
│   ├── naver_cafe.py  # Naver Cafe entities
│   └── ai_analysis.py # AI analysis entities
├── services/          # Business logic layer
│   ├── stream_service.py    # Stream orchestration
│   ├── youtube_service.py   # YouTube API integration
│   ├── ai_service.py        # LangChain AI services
│   ├── naver_cafe_service.py # Naver Cafe scraping
│   └── cache_service.py     # SQLite caching
├── containers/        # Dependency injection
│   └── di.py          # Single DI container
├── rest/             # API controllers
│   ├── stream_controller.py
│   ├── youtube_controller.py
│   ├── ai_controller.py
│   └── naver_cafe_controller.py
├── database/         # Data persistence
│   └── models.py     # SQLite models
├── models/           # Data transfer objects
│   └── stream_models.py
└── api/              # Legacy endpoints (backward compatibility)
```

## 🛠️ Technology Stack

### Core Framework
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM with async support
- **aiosqlite**: Async SQLite driver
- **Pydantic**: Data validation and serialization
- **dependency-injector**: DI container

### AI & External APIs
- **LangChain**: AI orchestration framework
- **LM Studio**: Local LLM server (Qwen3 model)
- **YouTube Data API v3**: Video metadata
- **httpx**: Async HTTP client
- **BeautifulSoup4**: HTML parsing for Naver Cafe

### Database Schema
```sql
-- Stream caching table
CREATE TABLE stream_cache (
    id INTEGER PRIMARY KEY,
    video_id VARCHAR(11) UNIQUE,
    url VARCHAR(255),
    date VARCHAR(10),
    title VARCHAR(500),
    thumbnail VARCHAR(500),
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    duration VARCHAR(50),
    ai_summary TEXT,
    highlights TEXT,        -- JSON array
    sentiment VARCHAR(100),
    engagement_score FLOAT,
    category VARCHAR(100),
    tags TEXT,             -- JSON array
    keywords TEXT,         -- JSON array
    created_at DATETIME,
    updated_at DATETIME,
    last_accessed DATETIME,
    cache_version INTEGER
);
```

## 🔧 Key Services

### StreamService (Main Orchestrator)
- **Purpose**: Coordinates stream processing pipeline
- **Dependencies**: AIService, YouTubeService, CacheService
- **Key Methods**:
  - `process_streams_batch()`: Batch process multiple streams
  - `enrich_with_details()`: Add YouTube metadata
  - `analyze_with_ai()`: Generate AI insights

### AIService (LangChain Integration)
- **LM Studio URL**: `http://localhost:1234/v1`
- **Model**: `qwen/qwen3-4b`
- **Features**:
  - Korean-only response enforcement
  - Sentiment analysis
  - Keyword extraction
  - Stream categorization
  - Engagement scoring

### CacheService (Performance Optimization)
- **Cache Duration**: 24 hours
- **Auto Cleanup**: 48 hours
- **Features**:
  - Smart cache invalidation
  - Batch operations
  - Statistics tracking

## 📡 API Endpoints

### Stream Management
```
GET    /api/v1/streams/categories     # Available categories
POST   /api/v1/streams/batch          # Batch create streams
GET    /api/v1/streams/{stream_id}    # Get single stream
```

### YouTube Integration
```
GET    /api/v1/youtube/video/{video_id}        # Video details
GET    /api/v1/youtube/video/{video_id}/stats  # Video statistics
POST   /api/v1/youtube/analyze                 # Batch analysis
```

### AI Analysis
```
POST   /api/v1/ai/summarize          # Generate summary
POST   /api/v1/ai/analyze-sentiment  # Sentiment analysis
POST   /api/v1/ai/extract-keywords   # Keyword extraction
```

### Cache Management
```
GET    /llm/cache/stats              # Cache statistics
POST   /llm/cache/clear              # Clear expired cache
```

### Legacy Endpoints (Backward Compatibility)
```
POST   /llm/streams                  # Paginated streams with details
POST   /llm/summarize                # AI summarization
GET    /llm/health                   # LM Studio health check
```

## 🚀 Development Workflow

### Environment Setup
```bash
# Virtual environment
cd uha && uv venv && source .venv/bin/activate

# Install dependencies
cd projects/uha-backend && uv pip install -e .

# Environment variables
cp env.example .env
# Set UHA_YOUTUBE_API_KEY, UHA_LM_STUDIO_URL, etc.
```

### Running the Server
```bash
# Development
python -m uvicorn uha.backend.main:app --reload --host 0.0.0.0 --port 8000

# Production
python -m uvicorn uha.backend.main:app --host 0.0.0.0 --port 8000
```

### Database Management
```python
# Initialize database (auto-run on startup)
from uha.backend.database.models import DatabaseManager
db = DatabaseManager()
await db.create_tables()
```

## 🧪 Testing Strategy

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Cache stats
curl http://localhost:8000/llm/cache/stats

# Stream processing
curl -X POST http://localhost:8000/llm/streams \
  -H "Content-Type: application/json" \
  -d '{"year": 2025, "page": 1, "per_page": 5, "include_details": true}'
```

### Performance Monitoring
- **Cache Hit Rate**: Monitor via `/llm/cache/stats`
- **Response Times**: First load vs cached responses
- **Memory Usage**: SQLite database size
- **AI Processing**: LM Studio response times

## 🔮 Future Enhancements

### Scalability
- **Redis Caching**: Replace SQLite for distributed caching
- **Message Queue**: Add Celery for background processing
- **Database Migration**: PostgreSQL for production
- **Containerization**: Docker + Kubernetes deployment

### AI Improvements
- **Multiple Models**: Support different LLM providers
- **Vector Search**: Semantic similarity for streams
- **Real-time Analysis**: WebSocket for live processing
- **Custom Training**: Fine-tune models for specific domains

### Monitoring & Observability
- **Prometheus Metrics**: Custom metrics collection
- **Grafana Dashboards**: Performance visualization
- **Sentry Integration**: Error tracking
- **APM Tools**: Application performance monitoring

### Security Enhancements
- **JWT Authentication**: User session management
- **Rate Limiting**: API abuse prevention
- **Input Validation**: Enhanced security checks
- **HTTPS/TLS**: SSL certificate management

## 🐛 Common Issues & Solutions

### LM Studio Connection
```python
# Check if LM Studio is running
curl http://localhost:1234/v1/models

# Restart LM Studio if needed
# Verify model is loaded: qwen/qwen3-4b
```

### Database Issues
```python
# Reset database
rm stream_cache.db
# Restart server (auto-creates tables)
```

### Cache Performance
```python
# Clear expired cache manually
curl -X POST http://localhost:8000/llm/cache/clear

# Monitor cache statistics
curl http://localhost:8000/llm/cache/stats
```

### YouTube API Limits
- **Quota Management**: Monitor daily quota usage
- **Fallback Strategy**: Use dummy data when quota exceeded
- **Caching Strategy**: Extend cache duration during high usage

## 📚 Key Dependencies

### Production Dependencies
```toml
fastapi = ">=0.116.1"
sqlalchemy = ">=2.0.43"
aiosqlite = ">=0.21.0"
pydantic = ">=2.11.7"
langchain = ">=0.3.27"
langchain-openai = ">=0.3.32"
dependency-injector = ">=4.48.1"
httpx = ">=0.28.1"
beautifulsoup4 = ">=4.13.5"
```

### Development Dependencies
```toml
pytest = ">=8.4.2"
pytest-asyncio = ">=1.1.0"
ruff = ">=0.12.12"
uvicorn = ">=0.35.0"
```

## 🔄 Data Flow

### Stream Processing Pipeline
1. **Fetch**: Get stream URLs from GitHub submodule
2. **Parse**: Extract video IDs and dates
3. **Cache Check**: Query SQLite for existing data
4. **Enrich**: Fetch YouTube metadata if not cached
5. **Analyze**: Generate AI insights via LangChain
6. **Store**: Save to cache with metadata
7. **Return**: Formatted response to frontend

### Caching Strategy
- **Primary Key**: video_id (unique identifier)
- **TTL**: 24 hours for active data
- **Cleanup**: 48 hours for unused data
- **Indexing**: video_id, date for fast queries
- **Versioning**: cache_version for schema changes

updated: 2025-09-07