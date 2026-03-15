> Last updated: 2026-03-07

# AdGenius AI

**Piattaforma AI per la generazione automatica di video pubblicitari**

> Uso personale - Powered by Claude Code Max

## Architettura

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│                    http://localhost:3012                     │
│                                                              │
│  Tabs: GitHub Repos | Video Generati | Progetti | + Manuale │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│                   http://localhost:8466                      │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Product    │  │  Market     │  │  Prompt Engine      │  │
│  │  Intel      │  │  Intel      │  │  (Video prompts)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  GitHub     │  │  Video      │  │  Videos DB          │  │
│  │  Intel      │  │  Generator  │  │  (SQLite persist.)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Claude Code CLI (OAuth)                     │ │
│  │         Gestisce analisi AI con abbonamento Max          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API Esterne                              │
│                                                              │
│  • OpenAI Sora (video generation)                           │
│  • Google Veo 3.1 (video generation)                        │
│  • Runway ML (video generation)                             │
│  • GitHub API (repository analysis)                         │
│  • Apify (Meta Ads Library scraping)                        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisiti

- Python 3.11+
- Node.js 18+
- Claude Code CLI con abbonamento Max

### Avvio Rapido

```bash
# Rendi eseguibile lo script
chmod +x start.sh

# Avvia l'applicazione
./start.sh
```

Oppure avvia manualmente:

```bash
# Terminal 1 - Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd app
uvicorn main:app --reload --port 8466

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### URL

- **Frontend**: http://localhost:3012
- **Backend API**: http://localhost:8466
- **API Docs**: http://localhost:8466/docs

## Funzionalità

### 1. Product Intelligence
Analizza automaticamente il prodotto estraendo:
- Nome e categoria
- USP (Unique Selling Propositions)
- Target audience
- Stile visivo
- Competitor probabili

### 2. Market Intelligence
Analizza la concorrenza:
- Pattern pubblicitari dominanti
- Temi di messaging
- Gap di mercato
- Opportunità

### 3. GitHub Intelligence
Analizza automaticamente i repository GitHub:
- Lista tutti i repository dell'utente autenticato
- Legge README, package.json, pyproject.toml e struttura directory
- Genera analisi marketing-focused con Claude Code CLI
- Crea prompt video ottimizzati direttamente dai repository

### 4. Prompt Engine
Genera prompt ottimizzati per:
- **Sora** (OpenAI) - qualità cinematografica
- **Veo 3.1** (Google) - generazione video 1080p
- **Runway ML** - text-to-video

### 5. Video Generation
Genera video pubblicitari AI-powered con 3 provider:
- **OpenAI Sora**: durata 4/8/12 secondi, formati 720x1280, 1280x720
- **Google Veo 3.1**: 1080p, aspect ratio 16:9 o 9:16
- **Runway ML**: durata 5/10 secondi
- Modalità "auto": prova Sora, fallback su Veo
- Download diretto e streaming

### 6. Video Gallery
Gestione completa dei video generati:
- Lista con filtri per stato (completed, processing, queued, failed)
- Statistiche aggregate
- Streaming/download video
- Eliminazione video (file + database)
- Filtro per repository

## Workflow Tipico

### Flusso da GitHub (principale)
1. **Seleziona Repository** - Dalla tab "GitHub Repos", scegli un repository
2. **Scegli Provider** - Seleziona tra Runway ML, OpenAI Sora o Google Veo
3. **Analizza** (opzionale) - Clicca "Analizza" per vedere l'analisi AI del progetto
4. **Genera Video** - Clicca "Genera Video" per creare il video pubblicitario
5. **Scarica** - Dalla tab "Video Generati", scarica il video completato

### Flusso Manuale
1. **Crea Progetto** - Dalla tab "+ Manuale", inserisci URL/immagini prodotto
2. **Analisi Prodotto** - AI estrae informazioni marketing
3. **Analisi Mercato** - Analizza competitor (opzionale)
4. **Genera Concept** - Crea concept video con prompt
5. **Genera Video** - Usa il provider selezionato per generare il video

## Struttura Progetto

```
smart-ads-creator/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── projects.py     # CRUD progetti
│   │   │   ├── analysis.py     # Analisi prodotto/mercato
│   │   │   ├── video.py        # Generazione video da progetto
│   │   │   ├── github.py       # GitHub repos, analisi, generazione video
│   │   │   └── videos_db.py    # Lista, streaming, eliminazione video
│   │   ├── services/
│   │   │   ├── claude_code.py    # Wrapper Claude Code CLI (Max subscription)
│   │   │   ├── github_intel.py   # Analisi repository GitHub via API
│   │   │   ├── video_generator.py # Sora + Veo + Runway ML
│   │   │   ├── product_intel.py  # Analisi prodotto
│   │   │   ├── market_intel.py   # Analisi mercato/competitor
│   │   │   └── prompt_engine.py  # Generazione prompt video
│   │   ├── db/
│   │   │   ├── database.py      # SQLAlchemy + SQLite
│   │   │   └── models.py        # Video, RepoAnalysis models
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic schemas
│   │   ├── core/
│   │   │   └── prompts.py       # Prompt templates
│   │   ├── config.py            # Configurazione (pydantic-settings)
│   │   └── main.py              # FastAPI app
│   ├── tests/
│   │   └── test_video_providers.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── GitHubRepos.tsx    # Lista repos + selezione provider
│   │   │   ├── VideoGallery.tsx   # Galleria video con filtri e stats
│   │   │   ├── ProjectCard.tsx    # Card progetto
│   │   │   ├── ProjectDetail.tsx  # Dettaglio progetto
│   │   │   └── NewProjectForm.tsx # Form creazione manuale
│   │   ├── hooks/
│   │   │   └── useProjects.ts   # Hook gestione progetti
│   │   ├── lib/
│   │   │   └── api.ts           # Client API (GitHub, Videos, Projects)
│   │   └── types/
│   │       └── index.ts         # TypeScript types
│   └── package.json
├── data/
│   ├── adgenius.db              # Database SQLite
│   └── videos/                  # Video generati (file .mp4)
├── .env                         # Chiavi API
├── specifica.md                 # Documentazione tecnica completa
├── problemi.md                  # Note sui problemi con i provider
└── start.sh                     # Script avvio
```

## Variabili d'Ambiente

| Variabile | Descrizione | Obbligatoria |
|-----------|-------------|--------------|
| `CLAUDE_OAUTH_ACCESS_TOKEN` | Token OAuth per Claude Code Max | Si |
| `OPENAI_API_KEY` | API key OpenAI (per Sora) | Si |
| `GEMINI_API_KEY` | API key Google Gemini (per Veo) | Si |
| `GITHUB_API_KEY` | GitHub Personal Access Token | Si |
| `RUNWAYML_API_SECRET` | API key Runway ML | No |

## Database

Il backend utilizza **SQLite** (via SQLAlchemy) per la persistenza dei dati:
- **Video**: stato, metadata, prompt, provider, percorso file locale
- **RepoAnalysis**: cache delle analisi repository (JSON)
- Path: `data/adgenius.db`

## Stack Tecnologico

### Backend
- Python 3.11+, FastAPI, Uvicorn
- SQLAlchemy + aiosqlite (database)
- Pydantic v2 + pydantic-settings (validazione e config)
- OpenAI SDK (Sora), google-genai (Veo), runwayml (Runway)
- httpx (HTTP async), apify-client (scraping)
- Loguru (logging)

### Frontend
- React 19, TypeScript, Vite 7
- TailwindCSS 4
- ESLint + TypeScript-ESLint

## Costi

Questa versione usa **Claude Code Max** (abbonamento), quindi:
- **Nessun costo** per analisi AI (Claude)
- **Costo variabile** per generazione video:
  - Sora: ~$1-4 per video (richiede verifica organizzazione)
  - Veo: richiede piano a pagamento Gemini
  - Runway: 125 crediti gratuiti, poi 5 crediti/secondo

## Note

- L'applicazione è progettata per uso personale singolo
- I video e le analisi dei repository sono persistiti in SQLite
- I progetti creati manualmente (non da GitHub) sono salvati in memoria
