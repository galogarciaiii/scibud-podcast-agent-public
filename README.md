# SciBud Podcast Agent

The **SciBud Podcast Agent** turns the latest **biology & AI** research into a daily podcast. It retrieves papers from PubMed, bioRxiv, and arXiv; scores and ranks them with fixed criteria; generates an engaging script with LLMs; produces narrated audio; updates the RSS feed; and posts to social—all automatically.

🎧 Listen: [SciBud — Emerging Discoveries from Bioimaging (Apple Podcasts)](https://podcasts.apple.com/us/podcast/scibud-emerging-discoveries-from-bioimaging/id1740828391)

---

## ✨ Features

* **Automated literature retrieval** (PubMed, bioRxiv, arXiv) with date-bounded queries
* **LLM scoring & ranking** using fixed, programmatically parsed criteria
* **Script generation** (title, description, citations, social post)
* **Text-to-speech** long-form narration (Google Cloud TTS)
* **RSS feed** generation & upload (ready for podcast platforms)
* **Hands-off publishing** (cloud DB sync + social post)
* **Modular design**: strategies → assistants → managers → services

---

## 🎯 Purpose

Provide an **accessible daily digest** of bioimaging discoveries for researchers and enthusiasts, bridging cutting-edge literature and broader audiences.

---

## 🛠 Tech Stack

* **Python** (typed helpers via `TypedDict`)
* **OpenAI** (text generation), **Google Cloud TTS/Storage** (audio + hosting)
* **SQLite** (episode & article registry)
* **Cron** on a GCP VM (automation)
* **feedgen** (RSS) · **PyMuPDF** (PDF text) · **requests** (HTTP)

---

## ⚙️ Architecture (High-Level)

* **PodcastCreator**: builds `QueryParams`, assembles source strategies, hands off to Director.
* **Director**: orchestrates the end-to-end pipeline:

  1. Download DB → 2) Fetch articles → 3) Filter existing → 4) Retrieve full text
  2. Score with LLM → 6) Rank & require **score ≥ 9** → 7) Generate script
  3. TTS audio → 9) Persist episode → 10) Generate & upload RSS
  4. Social post → 12) Mark article & upsert → 13) Upload DB → 14) Cleanup local

**Design patterns:** Strategy (per source), Facade (assistants), Manager/Service layering, Dependency injection via `UtilitiesBundle`, separation of concerns, explicit IO boundaries.

---

## 👩‍💻 Assistants (Orchestration Layer)

* **RetrievalAssistant**
  Calls a source strategy to **fetch article metadata & full text**.

* **EditorialAssistant**
  Uses `TextGenerationManager` to **score** (returns score + justification), **generate script**, **title**, **description**, and a **social post**. Randomizes persona/voice from config.

* **ProductionAssistant**
  Uses `AudioManager` for **long-form TTS** and `RSSManager` for **RSS XML**.

* **StorageAssistant**
  Wraps `DBManager`, `CloudStorageManager`, and `LocalStorageManager` for **DB ops**, **cloud uploads/downloads**, and **local cleanup**.

* **CommunicationAssistant**
  Uses `SocialMediaManager` to **post** the episode blurb (e.g., Bluesky).

---

## 🧩 Managers (Operational Layer)

* **TextGenerationManager**
  Orchestrates **OpenAI** prompts (via `PromptHelper`) and **response parsing** (`ResponseHelper`).

  * `generate_script|description|title|social_media_post|score`

* **AudioManager**
  Authenticates GCP (`GoogleAuthService`) and **synthesizes long audio** with `GoogleTTSService`.

* **RSSManager**
  Builds **podcast-ready RSS** (FeedGenerator + iTunes tags), links episode pages & audio assets.

* **DBManager**
  **SQLite** read/write: next episode number, insert/update Articles & Episodes, fetch full text, idempotent checks (`article_described_in_podcast`), and score lookups.

* **CloudStorageManager**
  **GCS** uploads/downloads/strings; handles keys & no-cache headers via `GoogleCloudService`.

* **LocalStorageManager**
  **Removes temp files** after publishing.

* **SocialMediaManager**
  **Bluesky** auth + posting via `BlueSkyService`.

---

## 🔌 Services (Integration Layer)

* **ArxivService**

  * Builds `export.arxiv.org` queries (Atom XML), parses entries, and derives **PDF** URLs.
  * Optional **full-text extraction** from PDFs via PyMuPDF.

* **BiorxivService**

  * Fetches **JSON** collections by date window; **filters** using OR-separated keywords across title/abstract.
  * Optional PDF full-text extraction with PyMuPDF.

* **PubmedService**

  * Uses E-utilities (`esearch`, `efetch`) for **PMC** articles, with tool/email and **API key**.
  * Parses **XML**: title, authors, DOI, abstract, body text; builds canonical **PMC URLs**.

* **OpenAIAuthService / OpenAITextGenService**

  * Loads **OPENAI\_API\_KEY**, creates client, handles **chat completions** with model from config.
  * Handles context-length guardrails and basic exception routing.

* **GoogleAuthService**

  * Loads **GOOGLE\_APPLICATION\_CREDENTIALS**, enables required **GCP services** (e.g., Text-to-Speech).

* **GoogleCloudService**

  * **Upload/download** with MD5 checks (avoid redundant transfers), **no-cache** headers on blobs, metadata refresh.

* **GoogleTTSService**

  * **Long-audio synthesis** (Linear16) to **GCS** URI with configurable **voice** and **language**; waits for LRO completion.

* **BlueSkyService**

  * Loads **BLUESKY\_API\_KEY**, authenticates, **refreshes** tokens, posts with **richtext facets** and link handling.

---

## 📦 Outputs

```
audio/season_<year>/episode_<number>.wav   # narrated episode (Linear16 from GCP TTS)
<db>.sqlite                                # Episodes & Articles registry (synced to GCS)
rss.xml                                    # Podcast feed (uploaded to public bucket)
```

---

## ▶️ Usage

Run manually:

```bash
python ai_and_biology.py
```

Tweak **query / sources / path** in `main()` (see `PodcastCreator`), or run via **cron** on a GCP VM for daily automation.

---

## Design Principles

* **Robustness & Idempotency**

  * DB lookups prevent re-podcasting the same article.
  * Full-text retrieval gracefully skips unavailable PDFs.
  * GCS MD5 checks avoid redundant transfers.

* **Observability**

  * Structured logging at each step (fetch → score → generate → publish).
  * Short, explicit info/warn/error lines for debugging in production.

* **Reliability & Rate Limits**

  * PubMed: tool/email/API key usage; lightweight throttling in `efetch`.
  * Long-running TTS operations handled with timeouts and status checks.

* **Security & Config**

  * Secrets via `.env` (OpenAI, PubMed, Bluesky) and GCP credentials.
  * Public repo omits private configs; all keys pulled at runtime.

* **Extensibility**

  * **Strategy** pattern for sources (add Elsevier/Crossref/IEEE easily).
  * Clean layering: **Services → Managers → Assistants → Director**.
  * Persona/voice are data-driven from config.

* **Maintainability**

  * Typed dicts (`ArticleInfo`, `EpisodeInfo`) and narrow interfaces.
  * Strict separation of concerns; minimal cross-module coupling.

* **Performance**

  * Bounded `max_results`; streaming PDFs; stepwise short-circuit on “no new” or low scores.

*(CI, and retries/backoff can be added easily—hooks are clear at service boundaries.)*

---

## ⚙️ Configuration & Env

**Not included** in public repo. Provide your own `config.json` and `.env`.

Required environment variables (examples):

* `OPENAI_API_KEY`
* `PUBMED_API_KEY`
* `BLUESKY_API_KEY`
* `GOOGLE_APPLICATION_CREDENTIALS` → path to service account JSON

Key config fields (examples):

```json
{
  "general_info": {
    "bucket_name": "bucket",
    "public_base_url": "https://storage.googleapis.com/bucket/",
    "private_base_url": "gs://bucket/",
    "audio_file_type": ".wav",
    "project_path": "projects/<gcp-project>/locations/global",
    "db_filename": "podcast.db",
    "rss_filename": "podcast.xml",
    "tool": "scibud-agent",
    "email": "owner@scibud",
    "logo_filename": "logo_channel.png"
  },
  "google_tts": {
    "language": "en-US",
    "voice_options": [{"Narrator A":"en-US-Standard-C"}]
  },
  "podcast_info": {
    "title": "SciBud",
    "artist_name": "SciBud Media",
    "description": "Daily bioimaging discoveries.",
    "podcast_link": "https://scibud.media",
    "primary_category": "Science",
    "type": "episodic",
    "episode_type": "full",
    "copyright": "SciBud Media"
  },
  "models": {
    "gpt_model": "gpt-4o"
  }
}
```

---

## 🧭 Example Entry Point

```python
# ai_and_biology.py
from podcast.creator import PodcastCreator
from podcast.utilities.bundle import UtilitiesBundle

def main() -> None:
    utilities = UtilitiesBundle()
    max_date = utilities.time.current_time
    min_date = utilities.time.get_time_offset(days=7)

    podcast_creator = PodcastCreator(
        query=("biological imaging OR bioimaging OR microscopy OR live-cell imaging OR "
               "fluorescence microscopy OR cryo-EM OR super-resolution microscopy OR "
               "light sheet microscopy OR electron microscopy OR multiphoton imaging"),
        utilities=utilities,
        path="bioimaging/",
        arxiv=False,
        biorxiv=True,
        pubmed=True,
        min_date=min_date,
        max_date=max_date,
        max_results=50,
    )
    podcast_creator.generate_podcast()

if __name__ == "__main__":
    main()
```

---

## 🚀 Roadmap (Suggested)

* Retries/backoff + circuit breakers at service layer
* Structured logs → GCP Logging; metrics via OpenTelemetry
* Parallel fetch & batching; caching for repeat queries

---

## ⚠️ Notes

This public repo omits private config and secrets. Provide your own keys and bucket settings to run end-to-end.
