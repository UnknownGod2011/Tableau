# TreasuryIQ Frontend - State-of-the-Art UI

A modern, AI-powered corporate treasury management dashboard built with Next.js 14, TypeScript, and cutting-edge UI technologies.

## 🚀 Features

### Core Functionality
- **Real-time Treasury Dashboard** - Live portfolio monitoring and analytics
- **AI-Powered Insights** - Conversational AI assistant for treasury operations
- **Advanced Risk Analytics** - VaR calculations, stress testing, and risk monitoring
- **Cash Optimization** - Intelligent cash allocation recommendations
- **Tableau Integration** - Interactive business intelligence dashboards
- **Multi-entity Support** - Global treasury management across entities

### Modern UI/UX
- **State-of-the-art Design** - Clean, modern interface with glassmorphism effects
- **Smooth Animations** - Framer Motion powered transitions and micro-interactions
- **Responsive Design** - Mobile-first approach with adaptive layouts
- **Smart Search** - AI-powered search with intelligent suggestions
- **Real-time Notifications** - Advanced notification center with priority management
- **Dark Mode Support** - Automatic theme switching based on system preferences

### Technical Excellence
- **TypeScript** - Full type safety and enhanced developer experience
- **Component Architecture** - Modular, reusable components with proper separation of concerns
- **State Management** - Zustand for efficient global state management
- **Performance Optimized** - Code splitting, lazy loading, and optimized bundle sizes
- **Accessibility** - WCAG 2.1 compliant with keyboard navigation support
- **Testing Ready** - Jest and React Testing Library setup

## 🛠 Technology Stack

### Core Framework
- **Next.js 14** - React framework with App Router
- **React 18** - Latest React with concurrent features
- **TypeScript** - Static type checking

### Styling & UI
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Production-ready motion library
- **Heroicons** - Beautiful hand-crafted SVG icons
- **Headless UI** - Unstyled, accessible UI components

### Data & State
- **Zustand** - Lightweight state management
- **React Query** - Server state management
- **Axios** - HTTP client for API calls

### Charts & Visualization
- **Recharts** - Composable charting library
- **Tableau JavaScript API** - Interactive dashboard embedding

### Development Tools
- **ESLint** - Code linting and formatting
- **Prettier** - Code formatting
- **Jest** - Testing framework
- **React Testing Library** - Component testing utilities

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout component
│   │   └── page.tsx           # Main dashboard page
│   ├── components/            # Reusable UI components
│   │   ├── AdvancedCharts.tsx # Modern chart components
│   │   ├── AIChat.tsx         # AI assistant interface
│   │   ├── DashboardLayout.tsx # Main layout wrapper
│   │   ├── LoadingSpinner.tsx # Loading states
│   │   ├── MetricCard.tsx     # KPI display cards
│   │   ├── NotificationCenter.tsx # Notification system
│   │   ├── RiskDashboard.tsx  # Risk analytics dashboard
│   │   ├── SmartSearch.tsx    # AI-powered search
│   │   ├── TableauDashboard.tsx # Tableau integration
│   │   └── TreasuryOverview.tsx # Portfolio overview
│   ├── hooks/                 # Custom React hooks
│   │   └── useTreasuryData.ts # Treasury data management
│   ├── lib/                   # Utility libraries
│   │   └── utils.ts           # Helper functions
│   ├── store/                 # State management
│   │   └── treasuryStore.ts   # Global treasury state
│   └── styles/                # Global styles
│       └── globals.css        # Tailwind and custom CSS
├── public/                    # Static assets
├── tailwind.config.js         # Tailwind configuration
├── postcss.config.js          # PostCSS configuration
├── next.config.js             # Next.js configuration
├── package.json               # Dependencies and scripts
└── tsconfig.json              # TypeScript configuration
```

## 🎨 Design System

### Color Palette
- **Primary**: Blue gradient (#3B82F6 to #2563EB)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)
- **Neutral**: Gray scale (#F9FAFB to #111827)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: Bold weights with gradient text effects
- **Body**: Regular weight with proper line heights
- **Code**: Monospace for technical content

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Multiple variants (primary, secondary, ghost)
- **Forms**: Clean inputs with focus states
- **Charts**: Interactive with hover effects and tooltips

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Configure the following variables:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_TABLEAU_SERVER_URL=your-tableau-server
   NEXT_PUBLIC_TABLEAU_SITE_ID=your-site-id
   ```

4. **Start the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
npm run build
npm start
```

## 🧪 Testing

### Run Tests
```bash
npm test                # Run tests once
npm run test:watch      # Run tests in watch mode
npm run test:coverage   # Run tests with coverage report
```

### Type Checking
```bash
npm run type-check      # TypeScript type checking
```

### Linting
```bash
npm run lint            # ESLint code analysis
```

## 📱 Features Overview

### Dashboard Components

#### 1. Treasury Overview
- Portfolio summary with key metrics
- Cash allocation visualization
- Investment portfolio breakdown
- Entity-based filtering
- Real-time data updates

#### 2. Risk Management
- Value at Risk (VaR) calculations
- Risk breakdown by category
- FX exposure analysis
- Stress testing scenarios
- Risk alerts and notifications

#### 3. Advanced Analytics
- Cash flow forecasting
- Performance attribution
- Portfolio allocation analysis
- Correlation matrices
- Predictive modeling

#### 4. AI Assistant
- Natural language processing
- Conversational interface
- Context-aware responses
- Action suggestions
- Integration with treasury data

#### 5. Tableau Integration
- Interactive dashboard embedding
- Real-time data refresh
- Export capabilities
- Mobile-responsive viewing
- Role-based access control

### Modern UI Features

#### Smart Search
- AI-powered suggestions
- Real-time search results
- Category-based filtering
- Keyboard navigation
- Recent searches

#### Notification Center
- Priority-based alerts
- Real-time updates
- Action buttons
- Read/unread states
- Entity-specific notifications

#### Responsive Design
- Mobile-first approach
- Tablet optimization
- Desktop enhancements
- Touch-friendly interactions
- Adaptive layouts

## 🔧 Configuration

### Tailwind CSS
Custom configuration includes:
- Extended color palette
- Custom animations
- Responsive breakpoints
- Component utilities
- Dark mode support

### Next.js
Optimized configuration with:
- App Router setup
- Image optimization
- Bundle analysis
- Performance monitoring
- SEO optimization

### TypeScript
Strict configuration ensuring:
- Type safety
- IntelliSense support
- Compile-time error checking
- Better refactoring
- Enhanced developer experience

## 🚀 Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Docker
```bash
docker build -t treasuryiq-frontend .
docker run -p 3000:3000 treasuryiq-frontend
```

### Static Export
```bash
npm run build
npm run export
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

---

**TreasuryIQ Frontend** - Built with ❤️ for modern treasury management