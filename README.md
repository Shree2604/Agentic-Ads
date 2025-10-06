# AgenticAds - AI-Powered Ad Generation Platform

Transform your ideas into platform-perfect ads with AI-powered multimodal generation. Create stunning text, images, and videos optimized for every platform—all in seconds, completely free.

## 🚀 Features

- **Multi-Platform Support**: Generate ads for Instagram, LinkedIn, TikTok, Facebook, and Twitter
- **AI-Powered Content Creation**: Smart text rewriting with different tones
- **Multimodal Generation**: Create text, poster images, and video reels
- **Brand Integration**: Automatic logo overlay and brand consistency
- **Advanced Admin Dashboard**: Monitor usage, feedback, and analytics with multi-page navigation
- **Card-Based Activity View**: Beautiful card interface for recent activity with filtering
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

- **Frontend**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS3 with CSS Variables and Glass Morphism effects
- **Icons**: Lucide React
- **State Management**: React Hooks (Custom hooks following SOLID principles)
- **Charts & Visualizations**: Custom SVG-based charts for analytics

## 📁 Project Structure

```
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
│   ├── useDataState.ts  # Data management state
│   ├── useAdGeneration.ts # Ad generation logic
│   ├── useAdminAuth.ts  # Admin authentication
│   └── useFeedbackHandler.ts # Feedback handling
├── types/               # TypeScript type definitions
├── styles/              # Global styles
└── App.tsx              # Main application component
```

## 🏗️ Architecture & Design Principles

This project follows **SOLID principles**:

- **Single Responsibility**: Each component has a single, well-defined purpose
- **Open/Closed**: Components are open for extension but closed for modification
- **Liskov Substitution**: Components can be replaced with their subtypes
- **Interface Segregation**: Interfaces are specific to client needs
- **Dependency Inversion**: High-level modules don't depend on low-level modules

### Key Architectural Decisions

1. **Component Separation**: Monolithic component split into focused, reusable components
2. **Custom Hooks**: Business logic extracted into custom hooks for reusability
3. **Type Safety**: Full TypeScript implementation with proper interfaces
4. **CSS Modularity**: Component-specific CSS files for better maintainability
5. **State Management**: Centralized state management using custom hooks
6. **Multi-Page Navigation**: Separate pages for detailed views with state management

## 🚀 Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Shree2604/Agentic-Ads.git
   cd Agentic-Ads
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000` to view the application

### Building for Production

```bash
npm run build
# or
yarn build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
# or
yarn preview
```

## 🔧 Available Scripts

- `npm run dev` - Start development server (port 5173)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

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
4. **Customer Insights**: Click "Customer Insights" tab for detailed feedback analysis
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
