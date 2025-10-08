# Setup & Development

## Prerequisites

- **Backend**: Python 3.10 or higher (required for AI/ML dependencies)
- **Frontend**: Node.js 16+, npm or yarn
- **Database**: MongoDB (local or Atlas cluster)

## Quick Start Commands

```bash
# Frontend
npm install
npm run dev

# Backend (Python 3.10+ required)
cd backend
pip install -r requirements.txt
python main.py
```

## Environment Configuration

### Backend Environment Variables (.env)

```bash
# Database
MONGODB_URL=mongodb://localhost:27017/agentic_ads

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# Hugging Face API (Optional - for enhanced models)
HUGGINGFACE_API_TOKEN=your-hf-token-here

# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Frontend Environment Variables (.env)

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AgenticAds

# Optional: Analytics
VITE_GA_TRACKING_ID=your-ga-id-here
```

## MongoDB Setup

### Local MongoDB Installation

```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb/brew/mongodb-community

# Windows - Download from https://www.mongodb.com/try/download/community
```

### MongoDB Atlas (Cloud)

1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create new cluster
3. Get connection string from "Connect" button
4. Update `MONGODB_URL` in `.env` file

## Troubleshooting

### Common Issues

**Python Version Issues:**
- Ensure Python 3.10+ is installed: `python --version`
- Use `python3` instead of `python` if needed
- Consider using virtual environment: `python -m venv venv`

**MongoDB Connection Issues:**
- Check if MongoDB is running: `sudo systemctl status mongodb`
- Verify connection string in `.env`
- Ensure network access (for Atlas clusters)

**Port Conflicts:**
- Backend uses port 8000 by default
- Frontend uses port 5173 by default (Vite dev server)
- Change ports in respective config files if needed

**Memory Issues:**
- For large knowledge bases, ensure sufficient RAM (8GB+ recommended)
- Monitor ChromaDB memory usage
- Consider using MongoDB Atlas for production deployments

### Development Tips

**Hot Reload:**
- Both frontend and backend support hot reload
- Changes to React components update instantly
- Python changes require server restart

**Debugging:**
- Use browser dev tools for frontend debugging
- Check backend logs: `python main.py` (visible in terminal)
- MongoDB logs: `tail -f /var/log/mongodb/mongod.log`

**Performance:**
- First startup may take time due to dependency installation
- Knowledge base seeding happens on first run
- Consider using pre-built Docker image for faster setup
