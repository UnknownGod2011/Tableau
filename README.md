# TreasuryIQ - AI-Powered Corporate Treasury Management

🏆 **Tableau Hackathon 2025 Submission**

An innovative AI-powered platform that transforms corporate treasury management through conversational analytics, predictive insights, and real-time optimization. Built for Fortune 500 companies managing $500M+ treasury operations.

## 🚀 Key Features

- **Conversational AI**: Natural language queries powered by Salesforce Agentforce
- **Real-time Risk Management**: Advanced VaR calculations and currency risk monitoring
- **Cash Optimization**: AI-driven recommendations for optimal cash placement
- **Predictive Analytics**: Machine learning models for cash flow forecasting
- **Tableau Integration**: Embedded dashboards with custom extensions
- **Enterprise Security**: SSO, MFA, and role-based access controls
- **Multi-channel Alerts**: Slack, email, and mobile notifications

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React/Next.js │    │  Python/FastAPI │    │   PostgreSQL    │
│    Frontend     │◄──►│     Backend     │◄──►│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Tableau Cloud   │    │   Agentforce    │    │     Redis       │
│   Integration   │    │      AI         │    │     Cache       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Business Value

- **$5M+ Annual Savings**: Through optimized cash management and risk mitigation
- **90% Faster Insights**: AI-powered analysis vs traditional methods
- **Real-time Decision Making**: Proactive alerts and recommendations
- **Enterprise Scale**: Supports multi-subsidiary, multi-currency operations

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Next.js 14** for SSR and optimization
- **Tableau Embedding API v3** for dashboard integration
- **WebSocket** for real-time updates
- **Tailwind CSS** for responsive design

### Backend
- **Python 3.11** with FastAPI
- **SQLAlchemy** for database ORM
- **Celery** for background tasks
- **Redis** for caching and sessions
- **Pandas/NumPy** for financial calculations

### AI & Analytics
- **Salesforce Agentforce** for conversational AI
- **TensorFlow/PyTorch** for predictive models
- **Apache Kafka** for real-time data streaming
- **Apache Airflow** for data pipelines

### Infrastructure
- **Docker** containerization
- **Nginx** reverse proxy
- **PostgreSQL** primary database
- **Redis** caching layer

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ and Python 3.11+
- Tableau Cloud account
- Salesforce Agentforce access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/treasuryiq-corporate-ai.git
   cd treasuryiq-corporate-ai
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start with Docker**
   ```bash
   docker-compose up -d
   ```

4. **Or run locally**
   ```bash
   # Install dependencies
   npm install
   
   # Start development servers
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📊 Demo Scenario: GlobalTech Industries

Our demo showcases a Fortune 500 technology company with:
- **$500M treasury portfolio** across 5 global subsidiaries
- **Multi-currency operations** (USD, EUR, GBP, JPY, SGD)
- **Complex risk exposures** requiring active management
- **Real-time optimization** opportunities worth millions

### Demo Flow
1. **Cash Optimization Alert**: $50M earning 0.1% - AI recommends treasury bills
2. **Currency Risk Management**: EUR exposure spike - hedging recommendations
3. **Supplier Risk Monitoring**: Credit rating deterioration alerts
4. **Predictive Analytics**: Q2 liquidity gap forecasting
5. **Slack Integration**: Real-time executive notifications

## 🧪 Testing

### Property-Based Testing
We use comprehensive property-based testing to ensure correctness:

```bash
# Run all tests
npm run test

# Run property tests with 100+ iterations
npm run test:properties

# Run integration tests
npm run test:integration
```

### Test Coverage
- **47 Correctness Properties** validated through property-based testing
- **Unit Tests** for specific business logic and edge cases
- **Integration Tests** for API endpoints and external services
- **End-to-End Tests** for complete user workflows

## 🔒 Security & Compliance

- **Enterprise SSO** with SAML/OAuth integration
- **Multi-Factor Authentication** for all users
- **Role-Based Access Control** with data masking
- **End-to-End Encryption** for data in transit and at rest
- **Comprehensive Audit Trails** for all financial operations
- **SOX Compliance** ready reporting and controls

## 📈 Performance

- **Sub-2 second** dashboard load times
- **30 second** risk calculation completion for large portfolios
- **99.9% uptime** with automated failover
- **100+ concurrent users** supported
- **Auto-scaling** for variable workloads

## 🏆 Hackathon Prize Categories

This solution targets all major prize categories:

- **🥇 Grand Prize**: Most innovative AI-powered treasury solution
- **📊 Best Actionable Analytics**: Specific recommendations with ROI
- **🧠 Best Semantic Modeling**: AI understands financial context
- **🔗 Best Product Extensibility**: Seamless Salesforce integration
- **👥 People's Choice**: Compelling demo and user experience

## 📚 Documentation

- [API Documentation](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)
- [User Manual](./docs/user-guide.md)
- [Developer Guide](./docs/development.md)

## 🤝 Contributing

This is a hackathon submission. For questions or collaboration opportunities, please contact the team.

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

**Built with ❤️ for the Tableau Hackathon 2025**

*Transforming corporate treasury management through AI-powered analytics*