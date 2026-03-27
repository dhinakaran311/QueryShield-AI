# 🚀 QueryShield AI — Service Startup Guide

This guide explains how to start **all services** required to run QueryShield AI locally.

---

## 📋 Prerequisites

Make sure the following are installed on your system:

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| PostgreSQL | 14+ | Database |
| Git | any | Version control |

---

## ⚙️ One-Time Setup

### 1. Clone the Repository
```bash
git clone https://github.com/dhinakaran311/QueryShield-AI.git
cd "QueryShield AI"
```

### 2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd frontend-next
npm install
cd ..
```

### 5. Configure Environment Variables

Create a `.env` file in the project root (copy the template below):

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=queryshield_db
DB_USER=postgres
DB_PASSWORD=your_password_here

# LLM Provider: "ollama" | "gemini" | "groq"
LLM_PROVIDER=groq

# Ollama (local - no API key needed)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Gemini (cloud)
GEMINI_API_KEY=your_gemini_key_here

# Groq (Llama - cloud) ← RECOMMENDED
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# App
APP_ENV=development
MAX_UPLOAD_SIZE_MB=50
QUERY_COST_THRESHOLD=10000
```

> **Get your free Groq API key at:** https://console.groq.com

### 6. Setup PostgreSQL Database
```bash
# Connect to PostgreSQL and create the database
psql -U postgres -c "CREATE DATABASE queryshield_db;"
```

---

## 🟢 Starting All Services

Open **3 separate terminals** and run one command in each:

### Terminal 1 — Backend (FastAPI)
```bash
# From project root, with .venv activated
uvicorn backend.main:app --reload --port 8000
```
✅ API will be available at: http://localhost:8000  
✅ Swagger docs at: http://localhost:8000/docs

---

### Terminal 2 — Frontend (Next.js)
```bash
cd frontend-next
npm run dev
```
✅ Frontend will be available at: http://localhost:3000

---

### Terminal 3 — (Optional) Ollama — only if `LLM_PROVIDER=ollama`
```bash
ollama serve
# In a new shell, pull the model if not already downloaded:
ollama pull llama3.2:3b
```

---

## 🔍 Health Check

After starting services, verify everything is running:

```bash
# Check API health
curl http://localhost:8000/health

# Check DB connectivity
curl http://localhost:8000/

# Test SQL generation (Groq/Llama)
curl -X POST http://localhost:8000/generate-sql \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Show top 5 sales\"}"
```

---

## 🛑 Stopping Services

In each terminal, press **`Ctrl + C`** to stop the respective service.

---

## 🗂️ Project Structure

```
QueryShield AI/
├── backend/               # FastAPI backend
│   ├── main.py            # API entry point
│   ├── sql_generator.py   # LLM SQL generation (Groq/Gemini/Ollama)
│   ├── security.py        # SQL injection shield
│   ├── schema_detector.py # Auto schema detection
│   ├── csv_uploader.py    # CSV → PostgreSQL
│   ├── optimizer.py       # Query cost analysis
│   ├── access_control.py  # Role-based access (RBAC)
│   └── memory.py          # Conversation memory
├── frontend-next/         # Next.js frontend
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── .env                   # Environment config (NOT committed)
└── STARTUP.md             # This file
```

---

## 🔑 LLM Provider Options

| Provider | Speed | Cost | Setup |
|----------|-------|------|-------|
| **Groq (Llama 3.3 70B)** ← default | ⚡ Very Fast | Free tier | API key only |
| Gemini 2.0 Flash | Fast | Free tier | API key only |
| Ollama (local) | Moderate | Free | Local install |

Switch providers by changing `LLM_PROVIDER` in `.env`.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|---------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| DB connection failed | Check PostgreSQL is running, verify `.env` credentials |
| Port 8000 in use | Use `uvicorn backend.main:app --reload --port 8001` |
| Port 3000 in use | Use `npm run dev -- --port 3001` in `frontend-next/` |
| Groq API error | Verify `GROQ_API_KEY` in `.env` at https://console.groq.com |
