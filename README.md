# scibud-podcast-agent

**scibud-podcast-agent** is an automated pipeline for generating daily science podcasts highlighting the latest discoveries in **biology and AI**. The system retrieves newly published research from sources like PubMed, bioRxiv, and arXiv, scores and ranks articles based on relevance and scientific rigor, and generates podcast scripts using LLMs. The pipeline then produces audio episodes, updates an RSS feed, and publishes the content for listeners.

The private version of this repo underlies the ongoing production of SciBud podcasts. [Find the podcasts on Apple Podcasts.](https://podcasts.apple.com/us/podcast/scibud-emerging-discoveries-from-bioimaging/id1740828391)

## Features

- **Automated literature retrieval** from multiple scientific databases
- **AI-based article scoring and ranking** using fixed evaluation criteria
- **Natural language script generation** optimized for clarity and engagement
- **Text-to-speech synthesis** for professional-sounding narration
- **Automated RSS feed generation** and publishing to podcast platforms
- **Modular architecture** with retrieval, editorial, production, and storage assistants

## Purpose

The goal of this project is to provide researchers and science enthusiasts with a **daily, accessible digest of bioimaging discoveries**, bridging the gap between cutting-edge research and broader audiences.

## Tech Stack

- **Python** backend
- **Large Language Models (LLMs)** for script generation and content curation
- **Text-to-Speech (TTS)** for narration
- **Cloud Storage & Hosting** for RSS feed and audio files
- **Cron-based scheduling** for daily updates

## Example Workflow

1. **Retrieve** articles from PubMed, bioRxiv, and arXiv  
2. **Score & Rank** articles for relevance, novelty, and clarity  
3. **Generate** a podcast script using an LLM  
4. **Synthesize Audio** using a TTS engine  
5. **Publish** the episode via an RSS feed

## Entry point
Modify the generate_podcast script to change queries and article sources. Execute the script to generate podcasts. Automation is performed by a cron job on a Google Cloud virtual machine.

```python generate_podcast.py```

## Requirements not present here
The configs are not present in this public version.

