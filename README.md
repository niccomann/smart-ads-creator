# AdGenius AI

**Piattaforma AI per la generazione automatica di video pubblicitari**

> Uso personale - Powered by Claude Code Max

## Architettura

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                   │
│                    http://localhost:3012                     │
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
│  • Apify (Meta Ads Library scraping)                        │
│  • Runway / Kling (fallback video)                          │
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

### 3. Prompt Engine
Genera prompt ottimizzati per:
- **Sora** (OpenAI) - qualità cinematografica
- **Runway** - buon bilanciamento
- **Kling** - opzione budget

### 4. Video Generation
Genera video pubblicitari AI-powered:
- Durata: 8-15 secondi
- Formati: 9:16 (Reels/TikTok), 1:1, 16:9
- Download diretto

## Workflow Tipico

1. **Crea Progetto** - Inserisci URL/immagini prodotto
2. **Analisi Prodotto** - AI estrae informazioni marketing
3. **Analisi Mercato** - Analizza competitor (opzionale)
4. **Genera Concept** - Crea 3 concept video con prompt
5. **Genera Video** - Usa Sora/Runway per generare il video

## Struttura Progetto

```
smart-ads-creator/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Pydantic schemas
│   │   ├── core/            # Prompts e config
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── lib/             # API client
│   │   └── types/           # TypeScript types
│   └── package.json
├── data/
│   └── videos/              # Video generati
├── .env                     # Chiavi API
├── specifica.md             # Documentazione completa
└── start.sh                 # Script avvio
```

## Costi

Questa versione usa **Claude Code Max** (abbonamento), quindi:
- **Nessun costo** per analisi AI (Claude)
- **Costo variabile** per generazione video:
  - Sora: ~$1-4 per video 10s
  - Runway: ~$0.50-1 per video 10s
  - Kling: ~$0.30-0.60 per video 10s

## Note

- L'applicazione è progettata per uso personale singolo
- I progetti sono salvati in memoria (riavviando il backend si perdono)
- Per persistenza, implementare database SQLite (già configurato in config)
