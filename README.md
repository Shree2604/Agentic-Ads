# AgenticAds - AI-Powered Ad Generation Platform

Transform your ideas into platform-perfect ads with AI-powered multimodal generation. Create stunning text, images, and videos optimized for every platform—all in seconds, completely free.

## 🎥 Demo Videos

<div style="display: flex; flex-direction: row; flex-wrap: nowrap; gap: 40px; justify-content: center; margin: 2rem 0; overflow-x: auto; padding: 20px 0;">
  <div style="flex: 0 0 500px; min-width: 0;">
    <h3 style="text-align: center; margin-bottom: 15px;">For Technical Users</h3>
    <a href="https://www.youtube.com/watch?v=4_i3H8mvVZk" target="_blank" style="display: block;">
      <img src="https://img.youtube.com/vi/4_i3H8mvVZk/maxresdefault.jpg" alt="Technical Demo" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); transition: transform 0.3s ease;">
    </a>
  </div>
  
  <div style="flex: 0 0 500px; min-width: 0;">
    <h3 style="text-align: center; margin-bottom: 15px;">For Non-Technical Users</h3>
    <a href="https://youtu.be/i0wvofuzU-Y" target="_blank" style="display: block;">
      <img src="https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg" alt="User Demo" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); transition: transform 0.3s ease;">
    </a>
  </div>
</div>


## 🚀 Features

- **Multi-Platform Support**: Generate ads for Instagram, LinkedIn, Twitter, and YouTube
- **Agentic RAG System**: Advanced Retrieval-Augmented Generation with LangGraph orchestration
- **Multi-Agent Architecture**: Specialized agents for research, copywriting, visual design, and quality assurance
- **Knowledge Base Integration**: Vector database with ChromaDB for enhanced content generation
- **Advanced Admin Dashboard**: Monitor usage, feedback, and analytics with multi-page navigation
- **Real-time Analytics**: Live data visualization with interactive charts and business intelligence
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Secure Admin Access**: JWT-protected admin APIs with session storage
- **Feedback-Driven Improvement Loop**: Continuous learning and adaptation based on user feedback

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: Custom components with CSS Modules
- **Icons**: Lucide React
- **State Management**: React Hooks with Context API
- **Styling**: CSS3 with CSS Variables and Glass Morphism effects
- **Charts**: Custom SVG-based visualizations

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with bcrypt password hashing
- **API**: RESTful architecture with WebSocket support

### AI/ML Stack
- **Orchestration**: LangGraph for multi-agent workflows
- **LLM Framework**: LangChain
- **Models**: Hugging Face Transformers
- **Vector Database**: ChromaDB with FAISS for similarity search
- **Knowledge Base**: RAG (Retrieval-Augmented Generation) system

### Multi-Agent System
- **Content Researcher**: Gathers and analyzes information
- **Copywriter Agent**: Generates compelling ad copy
- **Visual Designer**: Creates engaging visual content
- **Video Scriptwriter**: Produces video scripts and storyboards
- **Quality Assurance**: Ensures brand consistency and quality

## ⚡ Quick Start

### Prerequisites
- **Backend**: Python 3.10 or higher (required for AI/ML dependencies)
- **Frontend**: Node.js 16+, npm or yarn
- **Database**: MongoDB (local or Atlas cluster)
- **Vector Database**: ChromaDB for RAG system
- **Hugging Face API Key**: For accessing AI models

### Environment Setup

1. Create a `.env` file in the root directory with the following variables:
```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/agenticads

# JWT Configuration
JWT_SECRET=your_jwt_secret_here
JWT_EXPIRE=24h

# Hugging Face
HUGGINGFACE_API_KEY=your_huggingface_api_key

# Vector Database
CHROMA_DB_PATH=./chroma_db

```

### Get Started in Minutes

```bash
# Frontend
npm install
npm run dev

# Backend (Python 3.10+ required)
cd backend
pip install -r requirements.txt
python main.py
```

**Note**: Make sure to set up your environment variables before starting the application.

## 🎯 Usage

### For Users

1. **Welcome Page**: Learn about features and get started
2. **Ad Generation**:
   - Enter your ad text
   - Select tone and platform
   - Choose output types (text, poster, video)
   - Generate your perfect ad
3. **Download/Copy**: Get your generated content

### For Admins

1. **Login**: Use credentials `admin/admin` (click "Admin" in top-right corner)
2. **Dashboard Hub**: Overview of key metrics and business intelligence
3. **Recent Activity**: Click "Recent Activity" tab to view detailed generation history
4. **Customer Insights**: Click "Customer Insights" tab for comprehensive feedback analysis
5. **RAG Analytics**: Monitor knowledge base performance and generation quality
6. **Business Intelligence**: Track ROI, conversion rates, and platform performance

## 🏗️ Agentic AI Architecture

This project implements an advanced **Agentic RAG (Retrieval-Augmented Generation)** system with **LangGraph orchestration** and **Feedback-Driven Improvement Loops**.

**Detailed architecture documentation**: [architecture.md](architecture.md)

## 📚 Documentation

- **[Features & Updates](features.md)**: Detailed feature list and recent enhancements
- **[Tech Stack & Structure](tech-stack.md)**: Technology stack and project organization
- **[Setup Guide](setup.md)**: Complete installation and configuration instructions
- **[Contributing](contributing.md)**: Guidelines for contributing to the project

## 🧠 Advanced Features

### Multi-Agent System
- **Content Researcher Agent**: Retrieves relevant templates, examples, and guidelines from the knowledge base using semantic search
- **Copywriter Agent**: Generates platform-optimized ad copy with tone consistency and brand alignment
- **Visual Designer Agent**: Creates detailed prompts for AI image generation with design specifications
- **Video Scriptwriter Agent**: Develops structured video scripts with scene descriptions and narration
- **Quality Assurance Agent**: Validates outputs against quality criteria and provides refinement suggestions

### Feedback-Driven Pattern Recognition & Improvement Loop

The system implements a sophisticated **Pattern Recognition and Improvement Loop** that continuously learns and adapts:

**Pattern Recognition Engine:**
- Aggregates user feedback from MongoDB database
- Identifies positive highlights, improvement suggestions, and keyword patterns
- Calculates average ratings and sentiment trends per platform/tone combination

**Adaptive Generation Process:**
- Injects feedback insights into agent contexts before generation
- Guides copywriting, visual design, and video scripting based on user preferences
- Continuously improves output quality through iterative learning

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Detailed contribution guidelines**: [contributing.md](contributing.md)

## 🙏 Acknowledgments

- React team for the amazing framework
- Lucide for beautiful icons
- Vite for the fast build tool
- The open-source community for inspiration

## 📞 Support

If you have any questions or need help, please contact shree.xai.dev@gmail.com

---

**Built with ❤️ by Shreeraj Mummidivarapu**
