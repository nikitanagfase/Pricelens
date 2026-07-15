# ✈️ PriceLens: Flight Price Intelligence Platform

## Author
Nikita Nagfase

## Affiliation
Department of MCA
Suryodaya College Of Engineering And Technology, Nagpur

---

## Abstract

PriceLens is a full-stack flight price intelligence web application designed to help Indian domestic travelers make smarter booking decisions through machine learning-based fare prediction and real-time analytics. The platform allows users to search flights, predict future prices with confidence scores, analyse historical fare trends, plan trips within a budget, and set smart fare alerts.

The system is built using React.js (frontend), FastAPI (backend), SQLite/PostgreSQL (database), XGBoost ensemble model (ML), and SHAP library (Explainable AI). It follows a client-server REST API architecture with a 7-member XGBoost ensemble achieving MAE of ₹218 and R² of 0.978 on validation data.

The proposed solution aims to replace scattered, unreliable flight price information with a single intelligent platform that not only shows prices but explains why those prices exist — making it genuinely useful for budget-conscious travelers.

---

## 1. Introduction

Flight ticket pricing in India is highly dynamic and often opaque — prices change multiple times a day based on demand, season, booking window, and airline strategy. Most travelers either book too early (overpaying) or too late (missing cheaper windows), with no data-driven guidance available.

PriceLens addresses this gap by providing a dedicated platform where users can search flights with ML-backed price predictions on every result, view historical price trends, understand why a price is predicted through Explainable AI (SHAP), plan trips within a budget, and receive alerts when a fare drops to their target price. This structured, data-driven approach helps travelers book at exactly the right moment.

---

## 2. Literature Review

Existing systems in the domain of flight booking and price tracking exhibit partial solutions to the identified problem:

* **General Flight Booking Platforms:**
  Platforms such as MakeMyTrip and Goibibo display current prices but offer no historical trends, no price prediction, and no explanation of why prices are high or low on a given day.

* **Price Alert Tools:**
  Google Flights offers basic price tracking but lacks ML-based prediction, route-level analytics, budget planning, or Explainable AI features.

* **Academic ML Models:**
  Several research papers propose flight price prediction using regression and tree-based models but do not combine prediction with a complete, deployable web application that non-technical users can interact with.

### Research Gap

* Lack of a unified platform combining live search, ML prediction, and explainable AI in one interface
* Absence of budget-aware route planning for price-sensitive Indian domestic travelers
* No lightweight, student-deployable system that gracefully handles missing API keys (mock/live switchable mode)

PriceLens addresses these gaps through a modular, end-to-end full-stack architecture with a real trained ML model and a transparent XAI layer.

---

## 3. Methodology

### System Architecture

The system follows a **client-server REST API architecture**, where the React frontend communicates with FastAPI backend endpoints, which integrate an XGBoost ML ensemble, SQLite/PostgreSQL database, Redis cache (with in-memory fallback), and optionally the Amadeus Flight Offers Search API for live data.

### Development Approach

An **incremental development model** was adopted — starting with the ML model training pipeline, then the backend API layer, then the frontend UI, and finally integrating all layers end-to-end.

### Functional Modules

* Module 01 — Flight Search (with per-result ML prediction badges)
* Module 02 — Price Analytics Dashboard (historical trends, day-of-week, airline comparison)
* Module 03 — Price Heatmap Calendar (cheapest days visualised)
* Module 04 — Price Predictor with Explainable AI (XGBoost + SHAP)
* Module 05 — Budget Planner (route suggestions within a user-defined budget)
* Module 06 — Smart Fare Alerts (DB-backed, auth-protected, real notifications)
* Bonus — AI Travel Assistant (Claude API with rule-based fallback)

---

## 4. Implementation

### Frontend
* React.js 18 with Vite build tool
* React Router DOM for multi-page navigation
* Recharts for interactive price charts
* Axios for API communication
* Custom CSS3 design system (Space Grotesk + DM Sans + JetBrains Mono)

### Backend
* FastAPI (Python) for REST API
* SQLAlchemy ORM for database abstraction
* Pydantic for request/response validation
* python-jose for JWT authentication
* bcrypt for password hashing

### Machine Learning
* XGBoost — 7-member ensemble (trained on 25,000 synthetic samples encoding real-world pricing patterns)
* SHAP (TreeExplainer) — per-prediction feature importance for Explainable AI
* Scikit-learn — train/test split and evaluation metrics
* Joblib — model serialization

### Database
* SQLite (default, zero-setup) / PostgreSQL (production)
* Tables: users, fare_alerts, search_history, price_snapshots

### External APIs
* Amadeus Self-Service API — live Indian domestic flight search (optional, free tier)
* Anthropic Claude API — AI travel assistant (optional)

### Caching
* Redis (with automatic in-memory fallback if Redis not running)
* TTL: 15 minutes per unique route+date combination

---

## 5. System Workflow

1. User opens the app — homepage loads with animated hero, flight search form visible
2. User enters origin, destination, date and clicks "Search & Analyse Fares"
3. Backend checks Redis cache; if miss, calls Amadeus API (or generates mock data)
4. Each flight result is returned with a live ML prediction badge (price rising/dropping/stable)
5. User navigates to Analytics page — historical line chart, day-of-week bar chart, airline comparison, and festival impact data load from the backend
6. User opens Dashboard → Predictor tab — enters route and days before travel
7. Backend runs XGBoost ensemble prediction, SHAP explains top contributing factors
8. Confidence score shown (based on ensemble agreement), verdict: "Book Now" or "Wait"
9. User creates a Fare Alert (login required) — alert is saved to database
10. On next page load, alert prices are refreshed; if target met, status flips to "Triggered"
11. AI Assistant (floating chat widget) answers plain-language travel questions

---

## 6. Results and Discussion

The system demonstrates effective end-to-end implementation of a flight price intelligence platform. The XGBoost ensemble model achieves **MAE of ₹218** and **R² of 0.978** on held-out validation data, indicating strong predictive accuracy for the encoded pricing patterns.

The mock/live switchable architecture ensures the platform demos completely without any API keys, while upgrading to live Amadeus data requires only adding credentials to the `.env` file — no code changes. All 6 backend API modules (auth, flights, predict, analytics, budget, alerts) were tested end-to-end with a real ASGI server and passed. The React frontend builds with zero errors across 900 modules.

---

## 7. Limitations

* ML model trained on synthetic data (real historical Indian domestic fare datasets are not freely redistributable); a real dataset would improve accuracy further
* Amadeus free tier has monthly call limits — Redis caching is used to conserve quota
* Smart Alerts currently notify via logs only (email/Firebase notification requires additional SMTP/Firebase credentials)
* No real-time WebSocket price updates — prices refresh on page load
* AI assistant falls back to rule-based responses when Anthropic API key is absent

---

## 8. Future Scope

* Integration with a large real historical fare dataset (e.g., Kaggle Indian flight prices) to retrain the ML model on genuine data
* Real-time price streaming via WebSockets
* Email/SMS notifications for fare alerts using SendGrid or Twilio
* Firebase push notifications for mobile browser alerts
* Multi-city and flexible date search support
* Deployment on cloud infrastructure (Render backend + Vercel frontend + Neon PostgreSQL)
* User preference learning — personalised route recommendations based on search history
* Mobile app version using React Native

---

## 9. Conclusion

PriceLens provides a complete, working solution for data-driven flight price intelligence. It enables users to search flights with ML-backed predictions, understand price drivers through Explainable AI, visualise historical trends, plan within a budget, and set fare alerts — all within a single platform.

The clean separation between frontend, backend, ML pipeline, and data layers makes the system modular and extensible. The mock/live switchable design ensures it is practical for both demonstration and real-world use. PriceLens demonstrates how machine learning, explainable AI, and modern full-stack development can be combined to solve a real, everyday problem for Indian travelers.


