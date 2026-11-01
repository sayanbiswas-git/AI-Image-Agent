# Platebot: Automated AI Food Image Pipeline

Platebot is an end-to-end automation pipeline designed to source, evaluate, process, and upload high-quality food images for restaurant menus. It leverages a local Vision Large Language Model (LLM) to ensure images are visually accurate and aesthetically pleasing before they ever reach the final menu.

## The Problem It Solves
Sourcing hundreds of food images manually is tedious. Simply downloading the first Google Image result often results in blurry, incorrect, or poorly framed photos. Platebot automates this workflow by acting as an autonomous agent that *looks* at the images it finds and only keeps the good ones.

## Architecture & Workflow

The pipeline operates in a sequential, resilient loop:

1. **Input:** Reads a list of food items from an Excel spreadsheet (`agent.py`).
2. **Search:** Uses the **Tavily API** to search the web for high-quality image candidates (`image_search.py`).
3. **Vision QA:** Uses a local **Ollama Vision LLM** (`moondream`) to evaluate the downloaded image. It scores the image based on focus, framing, and whether it accurately represents the requested dish (`image_quality.py`).
4. **Processing:** If the image passes the quality gate, **Pillow** crops, resizes (1800x1200), and compresses the image to optimize file size (`image_processor.py`).
5. **Cloud Upload:** Authenticates via **Google Drive OAuth 2.0** and uploads the processed image, generating a shareable link (`drive_upload.py`).
6. **Reporting:** Uses **Pandas** and **OpenPyXL** to generate a beautifully formatted Excel report with clickable hyperlinks to the source and the uploaded Drive file (`excel_io.py`).

## Tech Stack
- **Language:** Python
- **AI / Vision:** Ollama (Local Vision LLM), Tavily API (Search)
- **Libraries:** Pandas, Pillow, OpenPyXL, Requests
- **Cloud Integration:** Google Drive API (OAuth 2.0)
- **Security:** Environment variables (`python-dotenv`), strict `.gitignore` for credential management.

## Prerequisites
Before running this project, ensure you have:
1. Python 3.10+ installed.
2. **Ollama** installed and running locally ([ollama.com](https://ollama.com)).
3. The `moondream` vision model pulled in Ollama: `ollama run moondream`
4. A **Tavily API Key** ([tavily.com](https://tavily.com)).
5. A **Google Cloud Project** with the Google Drive API enabled and OAuth 2.0 `credentials.json` downloaded.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sayanbiswas-git/Platebot.git
   cd Platebot