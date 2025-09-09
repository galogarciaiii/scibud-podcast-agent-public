Here’s a merged and cleaned-up **README.md** that combines your version and mine into one consistent document:

---

# SciBud Podcast Agent

The **SciBud Podcast Agent** is an automated pipeline for generating daily science podcasts highlighting the latest discoveries in **biology and AI**. The system retrieves newly published research from PubMed, bioRxiv, and arXiv, scores and ranks articles based on scientific rigor and relevance, generates podcast scripts using large language models (LLMs), and produces narrated audio episodes. It then updates an RSS feed and publishes content to podcast platforms.

The private version of this repository underlies the ongoing production of SciBud podcasts.
🎧 [Find the podcasts on Apple Podcasts.](https://podcasts.apple.com/us/podcast/scibud-emerging-discoveries-from-bioimaging/id1740828391)

---

## ✨ Features

* **Automated literature retrieval** from multiple scientific databases
* **AI-based article scoring and ranking** using fixed evaluation criteria
* **Natural language script generation** optimized for clarity and engagement
* **Text-to-speech synthesis** for professional narration
* **Automated RSS feed updates** and publishing to podcast platforms
* **Modular architecture** with dedicated assistants for retrieval, editorial, production, communication, and storage

---

## 🎯 Purpose

The goal of this project is to provide researchers and science enthusiasts with a **daily, accessible digest of bioimaging discoveries**, bridging the gap between cutting-edge research and broader audiences.

---

## 🛠 Tech Stack

* **Python** backend
* **Large Language Models (LLMs)** for summarization and script generation
* **Text-to-Speech (TTS)** for narration
* **Google Cloud Storage & Hosting** for database, RSS feed, and audio files
* **Cron-based scheduling** for daily automation

---

## ⚙️ System Architecture

The podcast pipeline is coordinated by two core components:

### **1. PodcastCreator**

* Wraps query parameters (keywords, date ranges, result limits).
* Assembles strategies for each selected source (`PubMed`, `bioRxiv`, `arXiv`).
* Delegates orchestration to the `Director`.

### **2. Director**

Manages the **end-to-end process** of creating a podcast episode:

1. **Download database** from cloud storage.
2. **Fetch articles** via `RetrievalAssistant`.
3. **Filter new articles** (exclude previously podcasted).
4. **Retrieve full text** where available.
5. **Score articles** with `EditorialAssistant`.
6. **Rank and select** the top article (score ≥ 9 required).
7. **Generate script** for narration.
8. **Produce audio** with `ProductionAssistant`.
9. **Insert episode info** into the database.
10. **Update RSS feed** with new metadata.
11. **Post to social media** with `CommunicationAssistant`.
12. **Mark articles** as described in the database.
13. **Upload database** to cloud storage.
14. **Cleanup local database file** after publishing.

Each assistant has a clear responsibility:

* **RetrievalAssistant** – fetches articles and full texts
* **EditorialAssistant** – scores articles and writes scripts
* **ProductionAssistant** – generates audio and RSS feed
* **StorageAssistant** – manages DB and cloud uploads
* **CommunicationAssistant** – posts updates to social platforms

---

## 📂 Outputs

* **Audio files** stored under:

  ```
  audio/season_<year>/episode_<number>.mp3
  ```
* **Database** updated with article and episode metadata
* **RSS feed** regenerated and uploaded
* **Social media posts** published automatically

---

## ▶️ Example Workflow

1. **Retrieve** articles from PubMed, bioRxiv, and arXiv
2. **Score & Rank** articles for relevance, novelty, rigor, and clarity
3. **Generate** a podcast script with an LLM
4. **Synthesize audio** narration using TTS
5. **Publish** the episode via RSS and cloud hosting

---

## 🚦 Usage

To run the agent manually:

```bash
python ai_and_biology.py
```

To adjust the query, sources, or output path, edit the `generate_podcast` script parameters in `main()`.
A cron job on a Google Cloud VM automates daily podcast generation.

---

## ⚠️ Requirements Not Present

This public version omits private configuration files (e.g., API keys, database credentials, bucket names).
You’ll need to provide your own `config.json` for full functionality.

---

Would you like me to also add a **flowchart diagram (mermaid or image)** showing the assistants and how they interact (retrieval → scoring → production → publishing) for clarity?
