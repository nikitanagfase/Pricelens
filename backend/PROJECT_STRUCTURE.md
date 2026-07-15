# 🗂️ Project Structure

```text
PriceLens/
│
├── 📁 frontend/                          # React.js + Vite Frontend
│   ├── 📄 index.html                     # Main HTML file
│   ├── 📄 vite.config.js                 # Vite configuration
│   ├── 📄 package.json                   # Dependencies & scripts
│   ├── 📄 .env.example                   # Environment variables template
│   └── 📁 src/
│       ├── 📄 main.jsx                   # React entry point
│       ├── 📄 App.jsx                    # Root component
│       │
│       ├── 📁 components/
│       │   ├── 📄 Navbar.jsx             # Navigation bar
│       │   ├── 📄 SearchForm.jsx         # Flight search form
│       │   ├── 📄 FlightResults.jsx      # Search results
│       │   ├── 📄 PriceChart.jsx         # Price trend visualization
│       │   ├── 📄 Heatmap.jsx            # Fare heatmap
│       │   ├── 📄 Predictor.jsx          # Price prediction UI
│       │   ├── 📄 BudgetPlanner.jsx      # Budget planner
│       │   ├── 📄 AlertsPanel.jsx        # Fare alerts
│       │   ├── 📄 ChatAssistant.jsx      # AI chatbot
│       │   └── 📄 AuthModals.jsx         # Login & Signup modals
│       │
│       ├── 📁 pages/
│       │   ├── 📄 Home.jsx               # Landing page
│       │   ├── 📄 Analytics.jsx          # Analytics dashboard
│       │   └── 📄 Dashboard.jsx          # User dashboard
│       │
│       ├── 📁 context/
│       │   ├── 📄 AuthContext.jsx        # Authentication state
│       │   └── 📄 ToastContext.jsx       # Notifications
│       │
│       ├── 📁 services/
│       │   └── 📄 api.js                 # API requests
│       │
│       └── 📁 styles/
│           ├── 📄 globals.css            # Global styles
│           └── 📄 variables.css          # CSS variables
│
├── 📁 backend/                           # FastAPI Backend
│   ├── 📄 requirements.txt               # Python dependencies
│   ├── 📄 .env.example                   # Backend environment variables
│   └── 📁 app/
│       ├── 📄 main.py                    # FastAPI entry point
│       │
│       ├── 📁 core/
│       │   ├── 📄 config.py              # Project configuration
│       │   └── 📄 security.py            # JWT & authentication
│       │
│       ├── 📁 api/
│       │   ├── 📄 deps.py                # API dependencies
│       │   └── 📁 routes/
│       │       ├── 📄 auth.py            # Authentication APIs
│       │       ├── 📄 flights.py         # Flight APIs
│       │       ├── 📄 predict.py         # ML prediction APIs
│       │       ├── 📄 analytics.py       # Analytics APIs
│       │       ├── 📄 budget.py          # Budget planner APIs
│       │       ├── 📄 alerts.py          # Fare alert APIs
│       │       └── 📄 chat.py            # AI Assistant APIs
│       │
│       ├── 📁 db/
│       │   ├── 📄 models.py              # Database models
│       │   ├── 📄 schemas.py             # Pydantic schemas
│       │   ├── 📄 crud.py                # CRUD operations
│       │   └── 📄 session.py             # Database connection
│       │
│       ├── 📁 ml/
│       │   ├── 📄 train.py               # Model training
│       │   ├── 📄 model.py               # ML prediction logic
│       │   ├── 📄 shap_explainer.py      # SHAP explainability
│       │   └── 📁 saved_models/
│       │       └── 📄 price_model.pkl    # Trained model
│       │
│       ├── 📁 services/
│       │   ├── 📄 amadeus_client.py      # Flight API integration
│       │   ├── 📄 cache_service.py       # Redis caching
│       │   └── 📄 notification_service.py# Email/Push alerts
│       │
│       └── 📁 utils/
│           └── 📄 helpers.py             # Utility functions
│
├── 📁 data/
│   ├── 📄 kaggle_flight_prices.csv       # Dataset
│   └── 📁 notebooks/
│       └── 📄 eda_and_training.ipynb     # EDA & model training notebook
│
├── 📁 docs/
│   └── 📄 project_report.docx            # Project documentation
│
├── 📄 .gitignore                         # Git ignored files
├── 📄 README.md                          # Project overview
└── 📄 SETUP.md                           # Installation guide
```
