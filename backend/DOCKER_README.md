# Agentic-Ads Backend - Docker Setup Guide

## Quick Start

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - API: http://localhost:8000
   - Swagger Documentation: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc

## Services

- **Backend API** (Port 8000): FastAPI application with AI-powered content generation
- **MongoDB** (Port 27017): Database for storing generations, feedback, and analytics
- **Redis** (Port 6379): Caching layer (ready for future use)
- **Nginx** (Port 80): Reverse proxy for production deployment

## Development

### Build individual service:
```bash
docker build -t agentic-ads-backend .
docker run -p 8000:8000 agentic-ads-backend
```

### Environment Variables:
Copy `.env.example` to `.env` and configure:
- Database connection strings
- API keys for AI services
- Admin credentials
- JWT secrets

## Production Deployment

For production, consider:
1. Use proper secrets management
2. Configure SSL certificates in `ssl/` directory
3. Set up proper logging and monitoring
4. Configure resource limits in docker-compose.yml

## File Structure

```
backend/
├── Dockerfile          # Main application container
├── docker-compose.yml  # Multi-service orchestration
├── .dockerignore       # Files to exclude from build context
├── .env.example        # Environment variables template
├── nginx.conf          # Reverse proxy configuration
└── mongo-init/         # MongoDB initialization scripts (create this directory)
    └── init.js         # Database initialization script
```

## Troubleshooting

- **Build fails**: Check that all dependencies in requirements.txt are compatible
- **MongoDB connection fails**: Verify MongoDB service is running and accessible
- **File uploads don't work**: Ensure proper volume mounts for temp directories
- **Memory issues**: Increase memory limits in Docker settings for ML workloads
