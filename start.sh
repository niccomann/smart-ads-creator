#!/bin/bash

# AdGenius AI - Start Script
# Avvia sia il backend che il frontend

set -e

echo "🎬 AdGenius AI - Avvio applicazione..."
echo ""

# Controlla se siamo nella cartella giusta
if [ ! -f ".env" ]; then
    echo "❌ Errore: File .env non trovato. Assicurati di essere nella cartella del progetto."
    exit 1
fi

# Funzione per terminare i processi figlio
cleanup() {
    echo ""
    echo "🛑 Arresto dei servizi..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Avvia Backend
echo "🚀 Avvio Backend (FastAPI)..."
cd backend

# Crea virtual environment se non esiste
if [ ! -d "venv" ]; then
    echo "📦 Creazione virtual environment..."
    python3 -m venv venv
fi

# Attiva venv e installa dipendenze
source venv/bin/activate
pip install -q -r requirements.txt

# Crea directory dati
mkdir -p ../data/videos

# Avvia backend in background (dalla cartella backend)
uvicorn app.main:app --host 0.0.0.0 --port 8466 --reload &
BACKEND_PID=$!
cd ..

echo "✅ Backend avviato su http://localhost:8466"
echo ""

# Attendi che il backend sia pronto
sleep 3

# Avvia Frontend
echo "🎨 Avvio Frontend (Vite + React)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Frontend avviato su http://localhost:3012"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎬 AdGenius AI è pronto!"
echo ""
echo "   Frontend: http://localhost:3012"
echo "   Backend:  http://localhost:8466"
echo "   API Docs: http://localhost:8466/docs"
echo ""
echo "   Premi Ctrl+C per terminare"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Attendi che i processi terminino
wait
