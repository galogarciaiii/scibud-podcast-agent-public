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
* **Modular architecture** with assistants and managers handling specialized tasks

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

The pipeline is coordinated by two core components:

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

---

## 👩‍💻 Assistants

The system uses **assistants** to divide responsibilities clearly:

* **RetrievalAssistant** – Fetches articles and full texts from configured sources.
* **EditorialAssistant** – Scores and ranks articles; generates podcast scripts, titles, descriptions, and social posts using LLMs.
* **ProductionAssistant** – Converts scripts into audio with TTS and generates the RSS feed.
* **StorageAssistant** – Handles databases, cloud storage, uploads, downloads, and cleanup.
* **CommunicationAssistant** – Publishes promotional posts to social media platforms.

---

## 🧩 Managers

Managers are lower-level modules that handle specific operational domains for the assistants.

* **AudioManager**
  Interfaces with Google TTS to synthesize long-form audio narration. Handles Google Cloud service authentication before generating episode audio.

* **CloudStorageManager**
  Provides upload/download operations for podcast assets using Google Cloud Storage. Manages authentication, API keys, and communication with the cloud.

* **DBManager**
  Handles SQLite operations for episode and article tracking. Inserts new episodes, updates article metadata, fetches full texts, checks whether articles were previously podcasted, and retrieves episode history.

* **LocalStorageManager**
  Manages local file cleanup. Removes temporary database or audio files after successful publishing.

* **RSSManager**
  Builds and formats the RSS feed XML for podcast distribution. Populates metadata, episodes, and links to audio files.

* **SocialMediaManager**
  Interfaces with the Bluesky API to authenticate and publish promotional posts for each episode.

* **TextGenerationManager**
  Wraps the OpenAI API for LLM-based text generation. Uses structured prompts to generate scripts, titles, descriptions, social media posts, and scoring justifications. Ensures responses are cleaned and properly formatted.

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
