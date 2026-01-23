# 🎬 AI Video Ad Generator - Specifica Tecnica Completa

> **Nome Progetto:** AdGenius AI (nome provvisorio)
> **Versione:** 1.0 Draft
> **Data:** Gennaio 2026
> **Autore:** [Il tuo nome]
> **Uso:** Personale/Esclusivo (single user)

---

## ⚠️ Nota Architetturale Importante

**Questa applicazione è per uso esclusivo personale.**

Invece di utilizzare le API Claude a pagamento (pay-per-token), il sistema utilizza **Claude Code CLI** con abbonamento **Claude Code Max**. Questo permette:

1. **Nessun costo API per Claude** - L'abbonamento Max copre tutto
2. **Accesso completo a tool use** - Claude Code gestisce autonomamente le chiamate
3. **Orchestrazione semplificata** - Claude Code come "motore AI" del sistema

**Architettura modificata:**
```
Frontend (React/Vite)
    ↓ HTTP/WebSocket
FastAPI Backend (orchestrazione, storage, state)
    ↓ subprocess
Claude Code CLI (con OAuth token + system prompt personalizzato)
    ↓ tool use
API Esterne (Sora/OpenAI per video, Apify per scraping, etc.)
```

Il backend invoca Claude Code come subprocess con prompt specifici per ogni modulo (Product Intel, Market Intel, etc.), e Claude Code gestisce autonomamente le chiamate ai tool necessari.

---

## 📋 Indice

1. [Executive Summary](#executive-summary)
2. [Problema e Opportunità](#problema-e-opportunità)
3. [Soluzione Proposta](#soluzione-proposta)
4. [Architettura del Sistema](#architettura-del-sistema)
5. [Stack Tecnologico e API](#stack-tecnologico-e-api)
6. [Moduli del Sistema](#moduli-del-sistema)
7. [Flusso Utente](#flusso-utente)
8. [Analisi Costi](#analisi-costi)
9. [Modello di Business](#modello-di-business)
10. [Analisi Competitiva](#analisi-competitiva)
11. [Roadmap di Sviluppo](#roadmap-di-sviluppo)
12. [Rischi e Mitigazioni](#rischi-e-mitigazioni)
13. [Metriche di Successo](#metriche-di-successo)
14. [Appendici](#appendici)

---

## Executive Summary

### Vision
Creare una piattaforma AI che automatizzi completamente la creazione di video pubblicitari ad alte prestazioni, partendo dall'analisi del prodotto fino alla generazione del video finale ottimizzato per le diverse piattaforme social.

### Value Proposition
- **Per PMI e Imprenditori:** Video ads professionali senza bisogno di agenzie o competenze video
- **Per Agenzie:** Scalare la produzione creativa riducendo i costi del 70%
- **Per E-commerce:** A/B testing video automatizzato per massimizzare ROAS

### Differenziatore Chiave
L'unica piattaforma che combina:
1. Analisi automatica del prodotto e del mercato
2. Intelligence sui competitor (scraping Meta Ads Library)
3. Generazione prompt ottimizzati per video AI (Sora, Runway, Kling)
4. Output multi-variante pronto per campagne

---

## Problema e Opportunità

### Il Problema

#### Per le PMI
- Costo medio per video pubblicitario professionale: **€1.500-5.000**
- Tempo di produzione: **2-4 settimane**
- Necessità di brief creativi, storyboard, riprese, editing
- Difficoltà a testare multiple varianti (A/B testing)

#### Per le Agenzie
- Bottleneck creativo: i designer non scalano
- Margini compressi dalla commoditizzazione
- Clienti che chiedono più varianti a meno costo

#### Dati di Mercato
| Metrica | Valore | Fonte |
|---------|--------|-------|
| Mercato globale video advertising | $180B (2025) | Statista |
| Crescita annua AI video generation | +35% CAGR | Grand View Research |
| % budget marketing su video | 47% del totale | HubSpot |
| Costo medio CPM video vs statico | -40% | Meta Business |

### L'Opportunità

Il mercato dei tool AI per advertising è in esplosione, ma:
- **AdCreative.ai** genera solo banner e copy, non video cinematografici
- **Creatify** fa video con avatar, non analisi competitor
- **Pencil** è enterprise-only (€10k+/anno)

**Gap identificato:** Nessuno offre analisi competitor + generazione video AI + ottimizzazione prompt in un'unica soluzione accessibile.

---

## Soluzione Proposta

### Descrizione del Prodotto

Una piattaforma SaaS che permette di:

1. **Inserire un prodotto** (URL, immagini, descrizione)
2. **Analizzare automaticamente** competitor e target audience
3. **Generare prompt ottimizzati** per piattaforme di video AI
4. **Produrre video pubblicitari** pronti per Meta, TikTok, YouTube
5. **Esportare varianti multiple** per A/B testing

### User Flow Sintetico

```
[Input Prodotto] → [Analisi AI] → [Prompt Generation] → [Video AI] → [Export Multi-formato]
     ↓                  ↓                 ↓                 ↓              ↓
  URL/Immagini    Competitor +      Template +         Sora/Runway     9:16, 1:1,
                  Target Persona    Best Practices                      16:9 + Copy
```

---

## Architettura del Sistema

### Diagramma ad Alto Livello

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React/Next.js)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Dashboard  │  │  Wizard     │  │  Video      │  │  Analytics &        │ │
│  │  Progetti   │  │  Creazione  │  │  Preview    │  │  Performance        │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ API REST / WebSocket
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (Node.js/Python)                        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        API Gateway & Auth (JWT)                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│  ┌─────────────┬─────────────┬───────┴───────┬─────────────┬─────────────┐  │
│  │             │             │               │             │             │  │
│  │  Product    │  Market     │   Audience    │  Prompt     │   Video     │  │
│  │  Intel      │  Intel      │   Intel       │  Engine     │   Gen       │  │
│  │  Module     │  Module     │   Module      │  Module     │   Module    │  │
│  │             │             │               │             │             │  │
│  └──────┬──────┴──────┬──────┴───────┬───────┴──────┬──────┴──────┬──────┘  │
│         │             │              │              │             │         │
└─────────┼─────────────┼──────────────┼──────────────┼─────────────┼─────────┘
          │             │              │              │             │
          ▼             ▼              ▼              ▼             ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
    │ Claude   │  │ Apify    │  │ Claude   │  │ Prompt   │  │ Sora 2 API   │
    │ API      │  │ Scrapers │  │ API      │  │ Library  │  │ Runway API   │
    │ (Vision) │  │ (Meta)   │  │          │  │ (DB)     │  │ Kling API    │
    └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────────┘
```

### Componenti Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE                           │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Vercel    │  │   Railway   │  │   Cloudflare R2         │  │
│  │  Frontend   │  │   Backend   │  │   Video Storage         │  │
│  │  + Edge     │  │   + Workers │  │   + CDN                 │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Supabase   │  │   Redis     │  │   BullMQ                │  │
│  │  PostgreSQL │  │   Cache     │  │   Job Queue             │  │
│  │  + Auth     │  │             │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stack Tecnologico e API

### Frontend
| Tecnologia | Scopo | Motivazione |
|------------|-------|-------------|
| Next.js 14 | Framework | SSR, API routes, performance |
| TypeScript | Linguaggio | Type safety, DX |
| Tailwind CSS | Styling | Rapid development |
| Shadcn/ui | Componenti | Qualità, accessibilità |
| React Query | Data fetching | Caching, sync |
| Zustand | State management | Semplicità |

### Backend
| Tecnologia | Scopo | Motivazione |
|------------|-------|-------------|
| Node.js + Express | API Server | Ecosistema, performance |
| Python (FastAPI) | ML Services | AI/ML libraries |
| PostgreSQL | Database | Relational, JSONB |
| Redis | Cache | Rate limiting, sessions |
| BullMQ | Job Queue | Video generation async |

### API Esterne Principali

#### 1. AI/LLM APIs

| API | Uso | Pricing | Rate Limits |
|-----|-----|---------|-------------|
| **Anthropic Claude API** | Analisi prodotto, competitor, prompt generation | $3-15/1M tokens | 4000 RPM |
| Claude Vision | Analisi immagini prodotto | Incluso | Incluso |
| OpenAI GPT-4o | Fallback/comparison | $5-15/1M tokens | Varia per tier |

**Esempio chiamata Claude per analisi prodotto:**
```python
import anthropic

client = anthropic.Anthropic()

def analyze_product(url: str, images: list[str]) -> dict:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Analizza questo prodotto per creare una video ad efficace.
                        
URL: {url}

Estrai:
1. Nome prodotto e categoria
2. USP (Unique Selling Proposition) principale
3. Target audience probabile (età, interessi, pain points)
4. Tone of voice del brand
5. Colori dominanti e stile visivo
6. Prezzo e posizionamento (budget/premium/luxury)
7. CTA principale usata
8. Competitor probabili

Rispondi in JSON strutturato."""
                    },
                    *[{"type": "image", "source": {"type": "url", "url": img}} for img in images]
                ]
            }
        ]
    )
    return json.loads(message.content[0].text)
```

#### 2. Video Generation APIs

| API | Qualità | Max Durata | Pricing | API Status |
|-----|---------|------------|---------|------------|
| **Sora 2** | ⭐⭐⭐⭐⭐ | 20 sec | $0.10-0.50/sec | ✅ Disponibile |
| **Sora 2 Pro** | ⭐⭐⭐⭐⭐ | 20 sec | $0.20-1.00/sec | ✅ Disponibile |
| **Runway Gen-4** | ⭐⭐⭐⭐ | 10 sec | ~$0.05/sec | ✅ Disponibile |
| **Kling AI** | ⭐⭐⭐⭐ | 2 min | ~$0.03/sec | ✅ Disponibile |
| **Pika Labs** | ⭐⭐⭐ | 4 sec | $10-60/mese | ⚠️ Limitato |

**Esempio chiamata Sora 2 API:**
```python
import openai

client = openai.OpenAI()

def generate_video(prompt: str, duration: int = 8, resolution: str = "1280x720") -> str:
    # Avvia job di generazione
    video = client.videos.create(
        model="sora-2",
        prompt=prompt,
        size=resolution,
        seconds=duration
    )
    
    video_id = video.id
    
    # Polling per completamento
    while True:
        status = client.videos.retrieve(video_id)
        if status.status == "completed":
            break
        elif status.status == "failed":
            raise Exception(f"Video generation failed: {status.error}")
        time.sleep(10)
    
    # Download video
    video_bytes = client.videos.download(video_id)
    
    return save_to_storage(video_bytes)
```

#### 3. Scraping & Data APIs

| API | Uso | Pricing | Note |
|-----|-----|---------|------|
| **Apify (Meta Ads Library)** | Scraping competitor ads | ~$0.20/1000 ads | Legale, dati pubblici |
| **Instagram Graph API** | Insights account utente | Gratis | 200 call/h, solo business |
| **TikTok Display API** | Trend e analytics | Gratis | Richiede approvazione |
| **SimilarWeb API** | Traffic data competitor | $$$$ | Opzionale, enterprise |

**Esempio scraping Meta Ads Library:**
```python
from apify_client import ApifyClient

def scrape_competitor_ads(competitor_name: str, country: str = "IT", limit: int = 50) -> list:
    client = ApifyClient("YOUR_APIFY_TOKEN")
    
    run_input = {
        "searchQuery": competitor_name,
        "countryCode": country,
        "adType": "all",
        "mediaType": "all",  # video, image, all
        "maxResults": limit
    }
    
    run = client.actor("curious_coder/facebook-ads-library-scraper").call(run_input=run_input)
    
    ads = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        ads.append({
            "ad_id": item.get("adId"),
            "page_name": item.get("pageName"),
            "ad_text": item.get("adText"),
            "media_url": item.get("mediaUrl"),
            "cta": item.get("callToAction"),
            "start_date": item.get("startDate"),
            "platforms": item.get("platforms"),
            "is_active": item.get("isActive")
        })
    
    return ads
```

---

## Moduli del Sistema

### Modulo 1: Product Intelligence

**Scopo:** Estrarre informazioni strutturate sul prodotto dell'utente.

**Input:**
- URL landing page/sito
- Immagini prodotto (1-10)
- Descrizione testuale (opzionale)
- Categoria (opzionale)

**Output (JSON):**
```json
{
  "product": {
    "name": "Sneaker EcoRun Pro",
    "category": "Footwear > Running > Sustainable",
    "price": 129.00,
    "currency": "EUR",
    "positioning": "premium"
  },
  "brand": {
    "name": "GreenStep",
    "tone_of_voice": "eco-conscious, youthful, energetic",
    "colors": {
      "primary": "#2ECC71",
      "secondary": "#27AE60",
      "accent": "#F39C12"
    }
  },
  "usp": [
    "Made from 100% recycled ocean plastic",
    "Carbon-neutral production",
    "30-day comfort guarantee"
  ],
  "target_audience": {
    "age_range": "25-40",
    "gender": "unisex",
    "interests": ["running", "sustainability", "fitness", "eco-friendly"],
    "pain_points": ["guilt about environmental impact", "want style + ethics"]
  },
  "visual_style": {
    "aesthetic": "clean, nature-inspired, modern",
    "photography_style": "bright, outdoor, action shots",
    "suggested_video_style": "cinematic outdoor, slow-motion running"
  },
  "cta_current": "Shop Sustainable",
  "competitors_inferred": ["Allbirds", "Veja", "On Running"]
}
```

**Tecnologie:**
- Claude API (text + vision)
- Web scraping (Playwright/Puppeteer)
- Image analysis

**Costo stimato per analisi:** ~$0.05-0.15

---

### Modulo 2: Market Intelligence

**Scopo:** Analizzare competitor e trend di mercato.

**Input:**
- Nome competitor (o auto-detected)
- Categoria prodotto
- Mercato geografico

**Output (JSON):**
```json
{
  "competitor_analysis": [
    {
      "name": "Allbirds",
      "total_active_ads": 47,
      "ads_analyzed": 50,
      "dominant_formats": {
        "video": 65,
        "image": 30,
        "carousel": 5
      },
      "avg_ad_duration_days": 23,
      "top_performing_ads": [
        {
          "ad_id": "123456",
          "running_since": "2025-11-01",
          "days_active": 82,
          "format": "video",
          "hook": "What if your shoes could save the planet?",
          "cta": "Shop Now",
          "visual_style": "lifestyle, urban outdoor",
          "estimated_performance": "high"
        }
      ],
      "messaging_themes": [
        "sustainability (78%)",
        "comfort (45%)",
        "style (34%)"
      ],
      "gaps_identified": [
        "No focus on performance/running",
        "Limited UGC content",
        "No influencer collaborations visible"
      ]
    }
  ],
  "industry_trends": {
    "rising_formats": ["short-form video", "UGC style", "before/after"],
    "declining_formats": ["static product shots", "studio backgrounds"],
    "avg_video_length": "8-15 seconds",
    "best_performing_hooks": [
      "Question opening",
      "Bold claim",
      "Pain point callout"
    ]
  },
  "opportunities": [
    "Performance-focused messaging underserved",
    "No competitor using AI-generated visuals",
    "Opportunity for athlete testimonials"
  ]
}
```

**Tecnologie:**
- Apify scrapers (Meta Ads Library)
- Claude API per analisi pattern
- Caching aggressivo (ads cambiano poco)

**Costo stimato:** ~$0.02-0.10 (con caching)

---

### Modulo 3: Audience Intelligence

**Scopo:** Definire buyer persona e pain points.

**Input:**
- Dati da Modulo 1 e 2
- Settore/nicchia
- (Opzionale) Dati Instagram Insights utente

**Output (JSON):**
```json
{
  "primary_persona": {
    "name": "Eco-conscious Emma",
    "demographics": {
      "age": "28-35",
      "gender": "female",
      "location": "urban areas, Northern Italy",
      "income": "€35-60k/year"
    },
    "psychographics": {
      "values": ["sustainability", "health", "authenticity"],
      "lifestyle": "active, urban professional, yoga/running",
      "media_consumption": ["Instagram", "TikTok", "podcasts"]
    },
    "pain_points": [
      "Wants to make ethical choices but limited options",
      "Skeptical of greenwashing",
      "Price sensitivity for sustainable products"
    ],
    "buying_triggers": [
      "Social proof (reviews, influencer endorsement)",
      "Transparency about materials/production",
      "Limited-time offers"
    ],
    "objections": [
      "Is it really sustainable or just marketing?",
      "Will it perform as well as traditional options?",
      "Is the premium price worth it?"
    ]
  },
  "secondary_personas": [...],
  "messaging_recommendations": {
    "primary_hook": "Address sustainability skepticism head-on",
    "emotional_angle": "Pride in making a difference",
    "rational_angle": "Specific impact metrics (X bottles recycled)",
    "cta_style": "Urgent but not pushy"
  },
  "platform_recommendations": {
    "primary": "Instagram Reels",
    "secondary": "TikTok",
    "rationale": "Target demographic 85% active on IG, video content preferred"
  }
}
```

**Tecnologie:**
- Claude API
- (Opzionale) Instagram Insights API
- Dati aggregati da ricerche di mercato

**Costo stimato:** ~$0.05-0.10

---

### Modulo 4: Prompt Engineering Engine

**Scopo:** Generare prompt ottimizzati per video AI.

**Input:**
- Output dei Moduli 1, 2, 3
- Tipo di video richiesto (product demo, lifestyle, UGC-style, cinematic)
- Durata target
- Piattaforma target (IG Reels, TikTok, YouTube Shorts)

**Output (JSON):**
```json
{
  "video_concept": {
    "title": "Ocean to Sole - The Journey",
    "duration_seconds": 10,
    "aspect_ratio": "9:16",
    "style": "cinematic documentary",
    "mood": "inspiring, hopeful"
  },
  "prompts": {
    "sora_2": {
      "main_prompt": "Cinematic close-up of running shoes on a pristine beach at golden hour. Camera slowly pulls back to reveal a runner's feet splashing through shallow surf. The shoes gleam with water droplets catching sunlight. Smooth tracking shot following the runner along the shoreline, waves gently rolling. Colors are vibrant teal ocean, warm golden sunset, and the distinctive green of the eco-friendly sneakers. Shot on anamorphic lens with subtle lens flares. Documentary style, authentic movement, no slow motion. Natural ambient ocean sounds.",
      "style_reference": "Shot like a Nike commercial meets National Geographic documentary",
      "negative_prompt": "No text overlays, no artificial poses, no studio lighting",
      "technical_params": {
        "model": "sora-2-pro",
        "resolution": "1080x1920",
        "duration": 10,
        "fps": 24
      }
    },
    "runway_gen4": {
      "main_prompt": "...",
      "motion_settings": {...}
    },
    "kling": {
      "main_prompt": "...",
      "duration": 10
    }
  },
  "variations": [
    {
      "name": "Urban Version",
      "prompt_delta": "Replace beach with city park morning jog...",
      "target_audience": "Urban professionals"
    },
    {
      "name": "UGC Style",
      "prompt_delta": "Selfie-style video, handheld smartphone aesthetic...",
      "target_audience": "Gen Z, authenticity-seekers"
    }
  ],
  "post_production_notes": {
    "text_overlay": {
      "hook": "Your next run could save the ocean",
      "timing": "0:00-0:03",
      "style": "minimal, sans-serif, bottom third"
    },
    "cta_overlay": {
      "text": "Shop Now - Link in Bio",
      "timing": "0:08-0:10"
    },
    "music_suggestion": "Uplifting acoustic, 120 BPM, builds to crescendo"
  }
}
```

**Prompt Library Structure:**
```
/prompt-templates
  /by-industry
    /fashion
    /food-beverage
    /tech-gadgets
    /beauty
    /fitness
  /by-style
    /cinematic
    /ugc-style
    /product-demo
    /testimonial
    /before-after
  /by-platform
    /instagram-reels
    /tiktok
    /youtube-shorts
    /facebook-feed
```

**Tecnologie:**
- Claude API con prompt engineering avanzato
- Template library proprietaria (Supabase/PostgreSQL)
- A/B testing framework per ottimizzazione continua

**Costo stimato:** ~$0.05-0.15

---

### Modulo 5: Video Generation

**Scopo:** Generare il video finale usando AI.

**Input:**
- Prompt ottimizzato da Modulo 4
- Piattaforma video scelta (Sora, Runway, Kling)
- Immagini prodotto (per image-to-video)
- Preferenze utente (qualità, budget)

**Output:**
- File video MP4 (multiple risoluzioni)
- Thumbnail suggerite
- Metadata per upload

**Workflow:**
```python
async def generate_video_workflow(project_id: str, config: VideoConfig) -> VideoResult:
    # 1. Seleziona provider basato su config
    provider = select_provider(
        quality=config.quality,
        budget=config.budget,
        style=config.style
    )
    
    # 2. Prepara il job
    job = await create_job(
        provider=provider,
        prompt=config.prompt,
        duration=config.duration,
        resolution=config.resolution
    )
    
    # 3. Invia a coda di elaborazione
    await job_queue.add("video_generation", {
        "job_id": job.id,
        "project_id": project_id,
        "provider": provider,
        "config": config
    })
    
    # 4. Webhook riceverà il completamento
    return VideoResult(
        job_id=job.id,
        status="processing",
        estimated_time=estimate_time(provider, config)
    )

async def process_video_job(job_data: dict):
    provider = job_data["provider"]
    
    if provider == "sora":
        result = await sora_generate(job_data)
    elif provider == "runway":
        result = await runway_generate(job_data)
    elif provider == "kling":
        result = await kling_generate(job_data)
    
    # Post-processing
    processed = await post_process(
        video=result.video_url,
        add_text=job_data.get("text_overlay"),
        resize_to=job_data.get("export_formats", ["1080x1920", "1080x1080"])
    )
    
    # Salva e notifica
    await save_to_storage(processed)
    await notify_user(job_data["project_id"], processed)
```

**Gestione Coda e Rate Limits:**
```python
# BullMQ configuration
video_queue = Queue("video_generation", {
    "defaultJobOptions": {
        "attempts": 3,
        "backoff": {
            "type": "exponential",
            "delay": 30000  # 30 sec initial delay
        },
        "removeOnComplete": 100,
        "removeOnFail": 50
    },
    "limiter": {
        "max": 5,  # Max 5 concurrent jobs
        "duration": 60000  # Per minute
    }
})
```

**Costo stimato per video 10 sec:**
| Provider | 720p | 1080p | Note |
|----------|------|-------|------|
| Sora 2 | $1.00 | $2.00 | Migliore qualità |
| Sora 2 Pro | $2.00 | $4.00 | Ultra quality |
| Runway Gen-4 | $0.50 | $1.00 | Buon balance |
| Kling | $0.30 | $0.60 | Budget option |

---

## Flusso Utente

### User Journey Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: ONBOARDING                                                          │
│ ─────────────────                                                           │
│ • Registrazione (email/Google)                                              │
│ • Selezione piano (Free trial / Paid)                                       │
│ • Brief wizard: settore, obiettivi, budget                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: INSERIMENTO PRODOTTO                                                │
│ ────────────────────────────                                                │
│ • Input URL landing page                                                    │
│ • Upload immagini prodotto (drag & drop)                                    │
│ • (Opzionale) Descrizione aggiuntiva                                        │
│ • Click "Analizza Prodotto"                                                 │
│                                                                             │
│ [Loading: "Analizzo il tuo prodotto..." ~15 sec]                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: REVIEW ANALISI                                                      │
│ ────────────────────                                                        │
│ • Dashboard con: USP, Target, Competitor                                    │
│ • Edit/conferma informazioni estratte                                       │
│ • Aggiunta competitor manuali (opzionale)                                   │
│ • Click "Genera Video Concepts"                                             │
│                                                                             │
│ [Loading: "Analizzo competitor e genero concept..." ~30 sec]               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: SELEZIONE CONCEPT                                                   │
│ ────────────────────────                                                    │
│ • 3-5 concept video proposti con:                                           │
│   - Titolo e descrizione                                                    │
│   - Storyboard visivo (AI-generated thumbnails)                            │
│   - Stile suggerito                                                         │
│   - Piattaforma target                                                      │
│ • Selezione concept preferito                                               │
│ • Customizzazione (durata, stile, varianti)                                 │
│ • Click "Genera Video"                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: GENERAZIONE VIDEO                                                   │
│ ────────────────────────                                                    │
│ • Progress bar con status                                                   │
│ • Tempo stimato: 2-5 minuti                                                 │
│ • Email notification al completamento                                       │
│ • Preview video in-app                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: REVIEW & EXPORT                                                     │
│ ───────────────────────                                                     │
│ • Video player con tutte le varianti                                        │
│ • Richiesta rigenerazione (se non soddisfatto)                             │
│ • Download formati: 9:16, 1:1, 16:9                                        │
│ • Copy suggerito per caption                                                │
│ • Export diretto a Meta Business Suite (futuro)                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Wireframe Chiave

#### Dashboard Principale
```
┌─────────────────────────────────────────────────────────────────┐
│  🎬 AdGenius AI                    [Credits: 47]  [Account ▼]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  + Nuovo Progetto Video                                    │  │
│  │  ─────────────────────                                     │  │
│  │  Crea un nuovo video ad in pochi minuti                   │  │
│  │                                        [Inizia →]          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  I Tuoi Progetti Recenti                                        │
│  ───────────────────────                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 🎥          │  │ 🎥          │  │ ⏳          │             │
│  │ Sneaker     │  │ Crema Viso  │  │ Borsa XYZ   │             │
│  │ EcoRun      │  │ Bio         │  │             │             │
│  │             │  │             │  │ In corso... │             │
│  │ ✅ Completo │  │ ✅ Completo │  │ 67%         │             │
│  │ 3 varianti  │  │ 5 varianti  │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  Analytics Rapidi                                               │
│  ────────────────                                               │
│  Video generati questo mese: 12                                 │
│  Crediti utilizzati: 53/100                                     │
│  Tempo medio generazione: 3.2 min                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Analisi Costi

### Costo per Video Generato (Breakdown)

**Scenario: 1 pacchetto con 3 varianti video da 10 secondi, 1080p**

| Componente | Costo Unitario | Quantità | Totale |
|------------|----------------|----------|--------|
| Analisi prodotto (Claude) | $0.10 | 1 | $0.10 |
| Scraping competitor | $0.01 | 50 ads | $0.50 |
| Analisi competitor (Claude) | $0.15 | 1 | $0.15 |
| Audience analysis (Claude) | $0.10 | 1 | $0.10 |
| Prompt generation (Claude) | $0.10 | 3 | $0.30 |
| **Video Sora 2 (10s, 1080p)** | $2.00 | 3 | **$6.00** |
| Post-processing | $0.05 | 3 | $0.15 |
| Storage (1 mese) | $0.02 | 3 | $0.06 |
| **TOTALE** | | | **$7.36** |

### Tabella Costi per Tier

| Tier | Video Inclusi | Costo Nostro | Prezzo Utente | Margine |
|------|---------------|--------------|---------------|---------|
| Starter | 3 video/mese | ~$22 | €49/mese | 56% |
| Pro | 10 video/mese | ~$74 | €149/mese | 50% |
| Agency | 30 video/mese | ~$221 | €399/mese | 45% |
| Enterprise | Illimitato | Variabile | Custom | 40%+ |

### Proiezione Costi Infrastruttura (Mensile)

| Servizio | Free Tier | 100 utenti | 1000 utenti |
|----------|-----------|------------|-------------|
| Vercel (Frontend) | $0 | $20 | $150 |
| Railway (Backend) | $5 | $25 | $100 |
| Supabase (DB) | $0 | $25 | $75 |
| Cloudflare R2 | $0 | $15 | $100 |
| Redis (Upstash) | $0 | $10 | $50 |
| **Totale Infra** | **$5** | **$95** | **$475** |

---

## Modello di Business

### Pricing Strategy

#### Piano Free (Lead Generation)
- 1 video/mese (720p, watermark)
- Analisi prodotto base
- No download HD
- **Scopo:** Conversione a paid

#### Piano Starter - €49/mese
- 3 video/mese (1080p)
- 3 varianti per video
- Analisi competitor (5 brand)
- Export tutti i formati
- Email support

#### Piano Pro - €149/mese
- 10 video/mese (1080p)
- 5 varianti per video
- Analisi competitor (20 brand)
- Accesso Sora 2 Pro
- Priority rendering
- Chat support

#### Piano Agency - €399/mese
- 30 video/mese
- Varianti illimitate
- White-label export
- Multi-brand management
- API access
- Dedicated account manager

#### Enterprise - Custom
- Volume illimitato
- SLA garantito
- Integrazione custom
- Training team
- On-premise option

### Revenue Projections

**Assunzioni:**
- Lancio: Mese 1
- Marketing budget: €2.000/mese
- Conversion rate trial→paid: 15%
- Churn mensile: 8%

| Mese | Utenti Trial | Utenti Paganti | MRR | Costi | Profit |
|------|--------------|----------------|-----|-------|--------|
| 1 | 50 | 0 | €0 | €3.000 | -€3.000 |
| 3 | 200 | 30 | €2.400 | €4.500 | -€2.100 |
| 6 | 500 | 120 | €10.800 | €8.000 | €2.800 |
| 12 | 1500 | 450 | €45.000 | €22.000 | €23.000 |

---

## Analisi Competitiva

### Competitor Diretti

#### 1. AdCreative.ai
| Aspetto | AdCreative.ai | Noi |
|---------|---------------|-----|
| Pricing | €29-359/mese | €49-399/mese |
| Focus | Banner + Copy | **Video AI** |
| Video | ❌ Basici, no AI video gen | ✅ Sora/Runway |
| Competitor analysis | ✅ Sì | ✅ Sì |
| Mercato | Global | **Focus Italia/EU** |

#### 2. Creatify
| Aspetto | Creatify | Noi |
|---------|----------|-----|
| Pricing | €27+/mese | €49-399/mese |
| Video style | Avatar AI | **Cinematic AI** |
| Analisi | ❌ Minima | ✅ Completa |
| Batch mode | ✅ Sì | ✅ Sì |

#### 3. Pencil
| Aspetto | Pencil | Noi |
|---------|--------|-----|
| Pricing | €€€€ (Enterprise) | €49-399/mese |
| Target | Enterprise | **PMI + Agency** |
| Video | ✅ Editing AI | ✅ Generation AI |
| Accessibilità | Bassa | **Alta** |

### Matrice Posizionamento

```
                    QUALITÀ VIDEO
                         ▲
                         │
         Pencil ●        │        ● NOI (Target)
                         │
                         │
    ─────────────────────┼─────────────────────► ACCESSIBILITÀ
                         │
                         │
      AdCreative.ai ●    │    ● Creatify
         (no video)      │
                         │
```

### Competitive Moat (Difese Competitive)

1. **Prompt Library Proprietaria:** Database di prompt ottimizzati per settore
2. **Dati di Performance:** A/B testing results → miglioramento continuo
3. **Focus Locale:** Italiano/Europeo, GDPR-compliant
4. **Integrazione Verticale:** Dall'analisi al video in un flusso unico

---

## Roadmap di Sviluppo

### Fase 1: MVP (Settimane 1-6)

**Obiettivo:** Validare il core concept con utenti reali.

**Scope:**
- [ ] Landing page con waitlist
- [ ] Auth (Supabase)
- [ ] Input: URL + 3 immagini
- [ ] Analisi prodotto base (Claude)
- [ ] 1 prompt template (lifestyle video)
- [ ] Integrazione Runway API (più accessibile)
- [ ] 1 video output (no varianti)
- [ ] Download diretto

**Stack MVP:**
- Next.js + Vercel
- Supabase (auth + db)
- Claude API
- Runway API

**Metriche successo:**
- 50 utenti beta
- 100 video generati
- NPS > 40

### Fase 2: Beta Pubblica (Settimane 7-14)

**Obiettivo:** Product-market fit con early adopters.

**Nuove Features:**
- [ ] Scraping Meta Ads Library
- [ ] Analisi competitor automatica
- [ ] 3 stili video (lifestyle, product demo, UGC)
- [ ] 3 varianti per progetto
- [ ] Integrazione Sora 2 API
- [ ] Sistema crediti
- [ ] Pagamenti (Stripe)
- [ ] Dashboard analytics base

**Metriche successo:**
- 500 utenti registrati
- 50 utenti paganti
- €2.500 MRR
- Churn < 15%

### Fase 3: Growth (Settimane 15-26)

**Obiettivo:** Scalare acquisizione e retention.

**Nuove Features:**
- [ ] Audience intelligence module
- [ ] 10+ template per settore
- [ ] Multi-brand (Agency plan)
- [ ] API pubblica
- [ ] Integrazioni (Zapier, Make)
- [ ] Export a Meta Business Suite
- [ ] A/B testing automatico
- [ ] AI copy generation per caption

**Metriche successo:**
- 3000 utenti registrati
- 300 utenti paganti
- €25.000 MRR
- CAC < €50

### Fase 4: Scale (Mesi 7-12)

**Obiettivo:** Leadership di mercato nel segmento.

**Nuove Features:**
- [ ] Mobile app
- [ ] White-label solution
- [ ] AI voice-over integration
- [ ] Music licensing integration
- [ ] Advanced analytics (predicted ROAS)
- [ ] Team collaboration
- [ ] Enterprise SSO

**Metriche successo:**
- 10.000 utenti
- 1.000 utenti paganti
- €100.000 MRR
- Break-even raggiunto

---

## Rischi e Mitigazioni

### Rischi Tecnici

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Sora API non disponibile/costosa | Media | Alto | Multi-provider strategy (Runway, Kling fallback) |
| Rate limits Instagram API | Alta | Medio | Caching aggressivo, focus su Meta Ads Library |
| Qualità video inconsistente | Media | Alto | QA automatico, rigenerazione gratuita, prompt optimization |
| Costi API superiori al previsto | Media | Alto | Usage caps, tier pricing, margin buffers |

### Rischi di Business

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Competitor con più risorse entra nel mercato | Alta | Alto | First mover advantage, focus su nicchia (Italia/PMI) |
| Churn elevato | Media | Alto | Onboarding eccellente, success team, feature stickiness |
| CAC troppo alto | Media | Medio | Content marketing, referral program, partnerships |
| Problemi legali (copyright, IP) | Bassa | Alto | Legal review, T&C chiari, watermark compliance |

### Rischi Regolatori

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Nuove regole EU su AI-generated content | Media | Medio | Monitoraggio normativo, watermark C2PA |
| GDPR compliance issues | Bassa | Alto | Privacy by design, DPO, audit regolari |
| Meta cambia policy Ads Library | Media | Medio | Diversificazione fonti dati |

---

## Metriche di Successo

### North Star Metric
**Video pubblicati dagli utenti che generano engagement**
(Misurato tramite tracking pixel o self-report)

### Metriche Chiave (KPIs)

#### Acquisition
- Visitatori unici/mese
- Sign-up rate
- Trial-to-paid conversion rate
- CAC (Customer Acquisition Cost)

#### Activation
- Time to first video generated
- Onboarding completion rate
- First video quality rating (NPS)

#### Retention
- Monthly Active Users (MAU)
- Video generati per utente/mese
- Churn rate
- Net Revenue Retention

#### Revenue
- MRR (Monthly Recurring Revenue)
- ARPU (Average Revenue Per User)
- LTV (Lifetime Value)
- LTV/CAC ratio (target: >3)

#### Product
- Tempo medio generazione video
- Tasso di rigenerazione (insoddisfazione)
- Feature adoption rate
- NPS

### Dashboard Metriche (Esempio)

```
┌─────────────────────────────────────────────────────────────────┐
│  📊 Dashboard Metriche - Gennaio 2026                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Utenti          MRR              Video Gen        NPS          │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐   │
│  │   487   │     │ €12.4K  │     │  1,247  │     │   52    │   │
│  │  ↑ 23%  │     │  ↑ 18%  │     │  ↑ 31%  │     │  ↑ 8    │   │
│  └─────────┘     └─────────┘     └─────────┘     └─────────┘   │
│                                                                 │
│  Conversion Funnel                                              │
│  ─────────────────                                              │
│  Visitatori  →  Sign-up  →  Trial  →  Paid  →  Retained        │
│    5,420         812        487      73        61               │
│              (15.0%)    (60.0%)   (15.0%)   (83.6%)            │
│                                                                 │
│  Costo per Video                                                │
│  ─────────────────                                              │
│  Medio: $6.82 | Target: $7.00 | ✅ On track                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Appendici

### A. Glossario

| Termine | Definizione |
|---------|-------------|
| **USP** | Unique Selling Proposition - caratteristica distintiva del prodotto |
| **CTA** | Call To Action - invito all'azione (es. "Compra Ora") |
| **ROAS** | Return On Ad Spend - ritorno sulla spesa pubblicitaria |
| **MRR** | Monthly Recurring Revenue - ricavi ricorrenti mensili |
| **NPS** | Net Promoter Score - metrica di soddisfazione cliente |
| **Prompt** | Istruzione testuale per generare contenuto AI |
| **UGC** | User Generated Content - contenuto stile amatoriale |

### B. API Reference Links

- [OpenAI Sora API](https://platform.openai.com/docs/guides/video-generation)
- [Runway API](https://docs.dev.runwayml.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Meta Graph API](https://developers.facebook.com/docs/graph-api/)
- [Apify Marketplace](https://apify.com/store)
- [Stripe API](https://stripe.com/docs/api)

### C. Risorse Utili

- [Meta Ads Library](https://www.facebook.com/ads/library/)
- [TikTok Creative Center](https://ads.tiktok.com/business/creativecenter)
- [Sora Prompting Guide](https://platform.openai.com/docs/guides/sora-prompting)

### D. Stack Tecnologico Dettagliato

```yaml
frontend:
  framework: Next.js 14
  language: TypeScript
  styling: Tailwind CSS
  components: shadcn/ui
  state: Zustand
  data-fetching: TanStack Query
  forms: React Hook Form + Zod
  hosting: Vercel

backend:
  runtime: Node.js 20
  framework: Express.js / Hono
  language: TypeScript
  api-style: REST + WebSocket
  hosting: Railway

database:
  primary: PostgreSQL (Supabase)
  cache: Redis (Upstash)
  storage: Cloudflare R2
  search: PostgreSQL Full-text (future: Algolia)

queue:
  system: BullMQ
  backend: Redis

auth:
  provider: Supabase Auth
  methods: Email, Google, Magic Link

payments:
  provider: Stripe
  model: Subscription + Usage-based

monitoring:
  errors: Sentry
  analytics: PostHog
  uptime: Better Uptime

ai-apis:
  llm: Anthropic Claude (primary), OpenAI (fallback)
  video: Sora 2, Runway Gen-4, Kling AI
  scraping: Apify
```

### E. Esempio Prompt Sora Ottimizzato

```
PROMPT PER VIDEO AD - SNEAKER SOSTENIBILE

[SCENE SETUP]
Cinematic tracking shot of premium eco-friendly running shoes on a pristine Mediterranean beach at golden hour. The camera is positioned low, at shoe level, capturing the texture of the recycled materials catching the warm sunset light.

[MOTION]
A runner's feet enter frame from the left, splashing through 2 inches of crystal-clear surf. Each footstep creates a small spray of water droplets that catch the sunlight like tiny prisms. The camera smoothly tracks alongside the runner at a steady pace.

[VISUAL DETAILS]
- Shoes: distinctive sage green with white accents, visible texture of recycled materials
- Water: shallow turquoise Mediterranean sea, gentle waves
- Light: golden hour, sun 15 degrees above horizon, creating long shadows
- Background: blurred beach with distant cliffs, shallow depth of field

[STYLE REFERENCES]
Shot on Arri Alexa with vintage anamorphic lenses. Color grade similar to "Free Solo" documentary - natural, slightly desaturated highlights, rich shadows. No artificial filters or heavy color manipulation.

[AUDIO]
Natural ambient sound: gentle waves, soft sand footsteps, subtle wind. No music.

[TECHNICAL]
- Duration: 10 seconds
- Resolution: 1920x1080
- Frame rate: 24fps
- Aspect ratio: 16:9 (will be cropped to 9:16 for Reels)

[NEGATIVE PROMPT]
No text overlays, no slow motion, no artificial studio lighting, no unnatural colors, no CGI elements, no face visible, no brand logos.
```

---

## Changelog

| Versione | Data | Modifiche |
|----------|------|-----------|
| 1.0 | Gen 2026 | Prima stesura completa |

---

## Contatti e Risorse

- **Progetto GitHub:** [da creare]
- **Figma Design:** [da creare]
- **Notion Board:** [da creare]

---

*Documento generato con assistenza AI. Ultima revisione: Gennaio 2026.*