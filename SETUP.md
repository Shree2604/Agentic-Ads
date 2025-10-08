# AgenticAds Setup Guide

This guide covers the complete setup for both the **FastAPI + MongoDB + RAG** backend and the **React** frontend.

**⚠️ IMPORTANT**: The backend requires **Python 3.10 or higher** due to AI/ML dependencies like PyTorch, Transformers, and LangGraph.

## Backend (FastAPI + MongoDB + RAG)

### Prerequisites
- **Python 3.10 or higher** (required for AI/ML dependencies)
- MongoDB (local installation or Atlas cluster)
- 8GB+ RAM recommended (for AI model loading)
- 4GB+ free disk space (for model storage and vector database)

### Installation

1. **Install Python 3.10+**
   ```bash
   # Check your Python version
   python --version
   # Should show Python 3.10.0 or higher
   ```

2. **Navigate to backend directory**
   ```bash
   cd backend
   ```

3. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: This will install AI/ML packages including:
   - `torch>=2.1.0` (PyTorch for deep learning)
   - `transformers>=4.39.0` (Hugging Face transformers)
   - `langgraph>=0.4.0` (Agent orchestration)
   - `chromadb>=1.1.1` (Vector database)
   - `sentence-transformers>=2.6.0` (Text embeddings)

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URL and other settings
   ```

6. **Start MongoDB**
   - **Local MongoDB**: Start `mongod` service
   - **Atlas**: Ensure your cluster is running and accessible

### Start the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000` with the following endpoints:

#### Core API Endpoints
- `GET /api/generation-history` - Get all generation records
- `POST /api/generation-history` - Create new generation record
- `GET /api/feedback` - Get user feedback
- `POST /api/feedback` - Submit user feedback
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/charts` - Get chart data for visualizations

#### RAG System Endpoints
- `POST /api/rag/generate` - Generate content using RAG system
- `POST /api/rag/knowledge-base` - Manage knowledge base documents
- `GET /api/rag/status` - Get RAG system status

#### Authentication Endpoints
- `POST /api/auth/login` - Admin login (username: admin, password: admin)
- `GET /api/auth/me` - Get current admin info (protected)

Sample data is seeded automatically on first run if collections are empty.

---

## Frontend (React + Vite)

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install
```

### Start the Development Server

```bash
npm run dev
```

The app runs at `http://localhost:5173`.

### Production Build

```bash
npm run build
npm run preview
```

## Integration Notes

- The frontend expects the backend at `http://localhost:8000`
- CORS is configured for `localhost:5173` and `localhost:3000`
- Ensure MongoDB is running before starting the API server
- The React app uses the backend for:
  - Generation history and analytics data
  - User feedback management
  - Admin dashboard statistics
  - RAG-powered content generation

## Environment Configuration

### Backend (.env)

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
# For Atlas: mongodb+srv://username:password@cluster.mongodb.net/agentic_ads

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# RAG Configuration (optional)
RAG_MODEL_PATH=./knowledge_base
CHROMA_DB_PATH=./chroma_db
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=AgenticAds
```

## Troubleshooting

### Backend Issues

- **Python version error**: Ensure you're using Python 3.10 or higher
  ```bash
  python --version  # Should show 3.10.0 or higher
  ```

- **Import errors with AI packages**:
  - Install Visual C++ Build Tools (Windows)
  - Ensure sufficient RAM (8GB+) for model loading
  - Try: `pip install --upgrade pip setuptools wheel`

- **MongoDB connection error**:
  - Verify `MONGODB_URL` in `.env`
  - Ensure MongoDB is running locally or cluster is accessible
  - Check network connectivity for Atlas clusters

- **RAG system errors**:
  - Ensure knowledge base files exist in `./backend/knowledge_base/`
  - Check ChromaDB path permissions
  - Verify model downloads completed successfully

### Frontend Issues

- **Module not found errors**: Run `npm install` to ensure all dependencies are installed
- **CORS errors**: Ensure backend is running and accessible at `localhost:8000`
- **Build errors**: Check Node.js version (16+ required)

### Performance Optimization

- **Memory usage**: The RAG system loads AI models into memory (2-4GB typical)
- **Storage**: Vector database and models require 2-4GB disk space
- **First run**: Initial model download may take 5-10 minutes
- **Subsequent runs**: Models are cached for faster startup

### Development Tips

- **Hot reload**: Both frontend and backend support hot reloading
- **Debug mode**: Run backend with `python main.py` for debug output
- **Environment**: Use `.env` files to manage different configurations
- **Logs**: Check console output for detailed error messages

You're now ready to run AgenticAds locally with a fully integrated RAG-powered backend and React frontend!
