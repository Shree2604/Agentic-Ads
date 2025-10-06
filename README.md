# AgenticAds - AI-Powered Ad Generation Platform

Transform your ideas into platform-perfect ads with AI-powered multimodal generation. Create stunning text, images, and videos optimized for every platform—all in seconds, completely free.

## 🚀 Features

- **Multi-Platform Support**: Generate ads for Instagram, LinkedIn, Twitter, and YouTube
- **AI-Powered Content Creation**: Smart text rewriting with different tones
- **Multimodal Generation**: Create text, poster images, and video reels
- **Brand Integration**: Automatic logo overlay and brand consistency
- **Advanced Admin Dashboard**: Monitor usage, feedback, and analytics with multi-page navigation
- **Card-Based Activity View**: Beautiful card interface for recent activity with filtering
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Secure Admin Access**: JWT-protected admin APIs with session storage

## 🛠️ Tech Stack

- **Frontend**: React 18 with TypeScript
- **Backend**: FastAPI with Python
- **Database**: MongoDB with Motor (async driver)
- **Build Tool**: Vite
- **Styling**: CSS3 with CSS Variables and Glass Morphism effects
- **Icons**: Lucide React
- **State Management**: React Hooks (Custom hooks following SOLID principles)
- **Data Persistence**: RESTful API with MongoDB backend
- **Charts & Visualizations**: Custom SVG-based charts for analytics
- **Authentication**: JWT-based admin login with token storage in localStorage

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Backend dependencies
├── .env.example         # Sample environment configuration
└── ...
│ 
src/
├── components/           # Reusable UI components
│   ├── ui/              # Basic UI components (Button, Modal, Input, etc.)
│   ├── Navigation/      # Navigation component
│   ├── AdminLogin/      # Admin login modal
│   └── FeedbackModal/   # User feedback modal
├── pages/               # Page components
│   ├── WelcomePage/     # Landing page
│   ├── AppPage/         # Main ad generation interface
│   ├── AdminPage/       # Admin dashboard hub
│   ├── ActivityPage/    # Detailed activity view page
│   └── InsightsPage/    # Customer insights page
├── hooks/               # Custom React hooks
│   ├── useAppState.ts   # Main application state
│   ├── useApiData.ts    # Data fetching and persistence layer
│   ├── useAdGeneration.ts # Ad generation logic
│   ├── useAdminAuth.ts  # Admin authentication
│   └── useFeedbackHandler.ts # Feedback handling
├── types/               # TypeScript type definitions
├── styles/              # Global styles
└── App.tsx              # Main application component
```

## 🏗️ Architecture & Design Principles

This project follows **SOLID principles** and implements a clean, modular architecture:

### SOLID Principles Implementation

- **Single Responsibility Principle (SRP)**: Each component, hook, and service has a single, well-defined purpose
- **Open/Closed Principle (OCP)**: Components are open for extension (new platforms, features) but closed for modification
- **Liskov Substitution Principle (LSP)**: Components can be replaced with their subtypes without affecting functionality
- **Interface Segregation Principle (ISP)**: TypeScript interfaces are specific to client needs, avoiding bloated interfaces
- **Dependency Inversion Principle (DIP)**: High-level modules depend on abstractions (hooks, services) rather than concrete implementations

### Key Architectural Decisions

1. **Full-Stack Separation**: Clear separation between React frontend and FastAPI backend
2. **API-First Design**: All data flows through RESTful API endpoints with MongoDB persistence
3. **Component Modularity**: Atomic, reusable components with clear responsibilities
4. **Custom Hooks Pattern**: Business logic extracted into focused, testable hooks
5. **Type Safety**: Comprehensive TypeScript implementation with strict interfaces
6. **CSS Architecture**: Component-scoped styling for maintainability and isolation
7. **State Management**: Centralized yet modular state management with API integration
8. **Multi-Page Architecture**: Dedicated page components for complex views with shared state

### Data Flow Architecture

```
User Action → React Component → Custom Hook → API Call → FastAPI → MongoDB → Response → Hook → Component → UI Update
```

- **Frontend Hooks**: `useApiData`, `useAdGeneration`, `useFeedbackHandler` handle API communication
- **Backend Services**: FastAPI endpoints provide CRUD operations for all data
- **Database Layer**: MongoDB stores all generation history, feedback, and analytics data
- **Authentication Middleware**: `get_current_admin()` guards protected endpoints by verifying JWT tokens issued by `/api/auth/login`
- **Real-time Updates**: All dashboard data reflects actual usage from MongoDB

## ⚙️ Setup & Development

Full backend and frontend setup instructions live in [`SETUP.md`](./SETUP.md). It covers:

- **Backend (FastAPI + MongoDB)** installation, environment variables, and API routes
- **Frontend (React + Vite)** installation, dev workflow, and production build steps
- Troubleshooting tips for common issues
- Authentication setup and environment configuration

Quick start commands:

```bash
# Frontend
npm install
npm run dev

# Backend
cd backend
pip install -r requirements.txt
python main.py
```

Refer to `SETUP.md` whenever you need the complete end-to-end environment instructions.

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
2. **Dashboard Hub**: Overview of key metrics and quick navigation
3. **Recent Activity**: Click "Recent Activity" tab to view card-based activity with filters
4. **Customer Insights**: Click "Customer Insights" tab for detailed feedback analysis sourced from MongoDB
5. **Monitor**: Track user feedback and generation history across dedicated pages

## 🌟 Recent Features

### Multi-Page Admin Dashboard
- **Navigation Tabs**: Switch between Dashboard, Recent Activity, and Customer Insights
- **Dedicated Pages**: Full-page experiences for detailed analysis
- **State Management**: Seamless navigation with React state management

### Card-Based Activity View
- **Beautiful Cards**: Individual cards for each generation activity
- **Advanced Filters**: Filter by platform and status
- **Performance Metrics**: Visual performance indicators for each activity
- **Responsive Design**: Cards adapt perfectly to all screen sizes

### Enhanced Analytics
- **SVG Pie Charts**: Multi-color pie charts for content tone analysis
- **Interactive Elements**: Hover effects and smooth animations
- **Real-time Data**: Live updates of generation statistics
- **Business Intelligence**: Comprehensive analytics for decision-making

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- React team for the amazing framework
- Lucide for beautiful icons
- Vite for the fast build tool
- The open-source community for inspiration

## 📞 Support

If you have any questions or need help, please contact shree.xai.dev@gmail.com

---

**Built with ❤️ by Shreeraj Mummidivarapu**
