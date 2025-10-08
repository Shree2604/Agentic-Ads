# Tech Stack & Project Structure

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript for type-safe component development
- **Vite** for fast development and optimized production builds
- **Lucide React** for beautiful, customizable icons
- **CSS3** with CSS Variables and Glass Morphism effects
- **Custom Hooks** following SOLID principles for business logic separation

### Backend
- **FastAPI** with Python 3.10+ for high-performance async APIs
- **MongoDB** with Motor (async driver) for document storage
- **LangGraph** for multi-agent workflow orchestration
- **LangChain** for LLM integration and prompt management
- **ChromaDB** with FAISS for vector similarity search

### AI/ML Stack
- **Hugging Face Transformers** for pre-trained language models
- **PyTorch** for deep learning model inference
- **Sentence Transformers** for text embedding generation
- **Agentic RAG** system with feedback-driven adaptation

### Authentication & Security
- **JWT** (JSON Web Tokens) for stateless authentication
- **bcrypt** for secure password hashing
- **Session storage** for admin authentication state

### Development Tools
- **TypeScript** for type-safe frontend development
- **ESLint** for code quality and consistency
- **Prettier** for code formatting
- **Vite** dev server with hot module replacement

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI application with RAG endpoints
├── requirements.txt          # Python dependencies (Python 3.10+ required)
├── .env                      # Environment configuration
├── rag/                      # RAG implementation with LangGraph
│   ├── __init__.py          # RAG system initialization
│   ├── agents.py            # Multi-agent system (Research, Copywriter, Designer, QA)
│   ├── graph.py             # LangGraph workflow orchestration
│   ├── knowledge_base.py    # Knowledge base management
│   ├── enhanced_vector_store.py # ChromaDB vector operations
│   ├── chunking.py          # Text chunking for RAG
│   ├── config.py            # RAG configuration
│   ├── text_generation.py   # Text generation with RAG
│   └── feedback_insights.py # Feedback aggregation and insights
├── data/                     # Data seeding and templates
└── knowledge_base/           # Vector database storage

src/
├── components/               # Reusable UI components
│   ├── ui/                  # Basic UI components (Button, Modal, Input, etc.)
│   ├── Navigation/          # Navigation component
│   ├── AdminLogin/          # Admin login modal
│   └── FeedbackModal/       # User feedback modal
├── pages/                   # Page components
│   ├── WelcomePage/         # Landing page
│   ├── AppPage/             # Main ad generation interface
│   ├── AdminPage/           # Admin dashboard hub
│   ├── ActivityPage/        # Detailed activity view page
│   └── InsightsPage/        # Customer insights page
├── hooks/                   # Custom React hooks
│   ├── useAppState.ts       # Main application state
│   ├── useApiData.ts        # Data fetching and persistence layer
│   ├── useAdGeneration.ts   # Ad generation logic
│   ├── useAdminAuth.ts      # Admin authentication
│   └── useFeedbackHandler.ts # Feedback handling
├── types/                   # TypeScript type definitions
├── styles/                  # Global styles
└── App.tsx                  # Main application component
```

## 🔧 Key Architecture Patterns

### SOLID Principles Implementation

- **Single Responsibility Principle (SRP)**: Each component, hook, and service has a single, well-defined purpose
- **Open/Closed Principle (OCP)**: Components are open for extension (new platforms, features) but closed for modification
- **Liskov Substitution Principle (LSP)**: Components can be replaced with their subtypes without affecting functionality
- **Interface Segregation Principle (ISP)**: TypeScript interfaces are specific to client needs, avoiding bloated interfaces
- **Dependency Inversion Principle (DIP)**: High-level modules depend on abstractions (hooks, services) rather than concrete implementations

### Data Flow Architecture

```
User Action → React Component → Custom Hook → API Call → FastAPI → MongoDB → Response → Hook → Component → UI Update
```

### Component Architecture

- **Atomic Design**: Components follow atomic design principles (atoms, molecules, organisms)
- **Composition over Inheritance**: Components are composed rather than extended
- **Prop Drilling Prevention**: Context and custom hooks prevent prop drilling
- **Performance Optimization**: Memoization and virtualization for large lists

### State Management

- **Local State**: React useState for component-specific state
- **Global State**: Custom hooks for application-wide state management
- **Server State**: React Query for server state management and caching
- **Form State**: React Hook Form for complex form handling

### API Design

- **RESTful Endpoints**: Resource-based API design
- **Async/Await**: Modern async programming patterns
- **Error Handling**: Comprehensive error handling and user feedback
- **Rate Limiting**: Built-in rate limiting for API protection

### Database Design

- **Document-Oriented**: MongoDB for flexible schema design
- **Indexing Strategy**: Optimized indexes for query performance
- **Aggregation Pipeline**: MongoDB aggregation for complex queries
- **Connection Pooling**: Efficient database connection management

This tech stack provides a solid foundation for a scalable, maintainable, and high-performance AI-powered ad generation platform.
