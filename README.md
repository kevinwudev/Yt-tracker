# Yt-tracker

Yt-tracker is a Python project that automatically generates an **AI summary** from a **YouTube video** and sends the result to **Telegram** via a bot.

It is designed for people who want to **track videos efficiently** and get the key points without watching the entire content.

---

## Features

- 📥 Fetch YouTube video information (URL / video ID)
- 🧾 Extract transcript (subtitles) when available
- 🤖 Generate an AI summary (e.g., OpenAI / LLM-based)
- 💬 Send the summary to Telegram (bot → chat/group)
- 🗂️ Supports caching / storing intermediate results (via `data/`)

---

##  Workflow

1. Input the @channel name
2. Auto fetch the YouTube video from yesterday (UTC+0) by default.
3. Extract transcript (or process subtitle files)
4. Send the transcript to an AI model to summarize
5. Push the summary to Telegram

---

##  Project Structure

Based on the current repository layout:

```txt
Yt-tracker/
├── .github/              # CI / workflows
├── data/                 # Cache / intermediate outputs
├── src/                  # Source code
│   └── vtt/              
├── .gitignore
├── .python-version
├── main.py               # Main entry point
├── pyproject.toml
└── uv.lock
```

---

##  Quick Start

### 1) Clone

```bash
git clone https://github.com/kevinwudev/Yt-tracker.git
cd Yt-tracker
```

### 2) Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3) Install dependencies

If the repo provides a lockfile / pyproject, install with your preferred tool:

```bash
pip install -e .
```

If you use `uv`:

```bash
uv lock
uv sync
```
---

##  Configuration (Environment Variables)

Create a `.env` file in the project root:

```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID=YOUR_TELEGRAM_CHAT_ID
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
WAITING_LIST=["@TED", "@CHANNEL_NAME_1", "@CHANNEL_NAME_2"]
```

### Required

- `BOT_TOKEN`  
  Your Telegram bot token (from **@BotFather**).

- `CHAT_ID`  
  The target chat ID from your bot.

(Not sure how to get the `CHAT_ID` and `BOT_TOKEN`? Have a look [here](https://hackmd.io/suWEZSwNQA-OaFKW3x_-pw))

- `OPENAI_API_KEY`  
  The API key used for summarization (To register a key [here](https://platform.openai.com/docs/overview)).

- `YOUTUBE_API_KEY`  
  API key from YouTube Data API (To register a key [here](https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=project-4ffe3a74-5afa-48a0-943)).

---

##  Usage

Run the main script:

```bash
python main.py
python main.py -d YYYY-MM-DD # for fetching the specific date (default yesterday)
python main.py -t # send to telegram
```


Typical behavior:

- reads a target video list/video URL from the given channel name.
- extracts the transcript or downloads to the `.m4a` file, then generates the transcript via OpenAI.
- generates a summary using the configured AI provider
- sends the summary to Telegram

---

##  Development Notes

Recommended improvements if you want to make this production-grade:

- Add structured logging
- Add retries for network calls (YouTube / Telegram / AI)
- Cache transcripts to reduce API cost
- Add a prompt template file (so prompts are not hard-coded)
- Add unit tests for subtitle parsing and message formatting

---

## 🤝 Contributing

Contributions are welcome!

- Open an issue for bugs / feature requests
- Submit a pull request for improvements

---

## 📄 License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for details.

