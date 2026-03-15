> Last updated: 2026-03-15 18:00

# AdGenius AI - Frontend

Frontend dell'applicazione **Smart Ads Creator**: una piattaforma che analizza repository GitHub (o prodotti inseriti manualmente) e genera video pubblicitari tramite AI (Sora, Runway, Kling, Veo).

## Cosa Fa

- **Importa repository GitHub**: lista i repo dell'utente, analizza codice e README per estrarre nome prodotto, target audience, USP e stile visivo
- **Analisi prodotto e mercato**: lancia analisi automatiche (prodotto, competitor, trend) e genera concept video
- **Generazione video AI**: invia prompt a provider video (Sora, Runway, Kling, Veo) con stili diversi (cinematic, lifestyle, UGC, product demo, testimonial)
- **Galleria video**: visualizza, scarica e gestisce tutti i video generati con statistiche aggregate
- **Creazione manuale**: form per inserire prodotti/servizi non presenti su GitHub

## Stack Tecnico

- **React 19** + **TypeScript 5.9**
- **Vite 7** (dev server e build)
- **Tailwind CSS 4** (plugin Vite nativo)
- Nessuna libreria UI esterna -- componenti custom con classi Tailwind

## Struttura Progetto

```
src/
  App.tsx                  # Layout principale con navigazione a tab
  components/
    GitHubRepos.tsx        # Lista repo GitHub, analisi e creazione progetto
    VideoGallery.tsx       # Galleria video generati con streaming
    ProjectCard.tsx        # Card progetto con stato e azioni
    ProjectDetail.tsx      # Vista dettaglio con analisi e generazione video
    NewProjectForm.tsx     # Form creazione progetto manuale
  hooks/
    useProjects.ts         # Hook per CRUD progetti (list, create, delete, refresh)
  lib/
    api.ts                 # Client API: projects, analysis, video, github, videos
  types/
    index.ts               # Tipi TypeScript (Project, VideoConcept, GeneratedVideo, etc.)
```

## API Backend

Il frontend comunica con il backend tramite `/api` (proxy Vite). Endpoint principali:

- `GET/POST/DELETE /api/projects/` -- gestione progetti
- `POST /api/analysis/{id}/full-analysis` -- analisi completa
- `POST /api/video/{id}/generate/{concept}` -- generazione video
- `GET/POST /api/github/repos` -- integrazione GitHub
- `GET /api/videos` -- galleria video con statistiche

## Come Avviare

```bash
npm install
npm run dev      # Server di sviluppo (Vite)
npm run build    # Type-check + build produzione
npm run preview  # Anteprima build
npm run lint     # ESLint
```
