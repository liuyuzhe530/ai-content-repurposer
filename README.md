<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Claude-Sonnet-ff6b6b?style=for-the-badge&logo=claude&logoColor=white" alt="Claude">
  <img src="https://img.shields.io/badge/AI-Content-7c3aed?style=for-the-badge&logo=robot&logoColor=white" alt="AI Content">
</p>

<h1 align="center">AI Content Repurposer</h1>

<p align="center">
  <strong>Transform one piece of content into multiple platform-optimized posts</strong><br>
  Blog posts, YouTube videos, podcasts — turn them into Twitter threads, LinkedIn posts, Instagram captions, and Dev.to articles with Claude AI.
</p>

<p align="center">
  <a href="https://github.com/liuyuzhe530/ai-content-repurposer"><img src="https://img.shields.io/github/stars/liuyuzhe530/ai-content-repurposer?style=social" alt="Stars"></a>
  <a href="https://github.com/liuyuzhe530/ai-content-repurposer/issues"><img src="https://img.shields.io/github/issues/liuyuzhe530/ai-content-repurposer" alt="Issues"></a>
  <a href="https://github.com/liuyuzhe530/ai-content-repurposer/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
</p>

---

## 🎯 What It Does

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Content Repurposer                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📝 Input: Blog Post / YouTube / Podcast                         │
│  "How to Build a REST API with Python Flask"                     │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  ▼  Claude AI Transforms  ▼                                      │
│                                                                  │
│  🐦 Twitter/X:                                                  │
│  "🧵 5 tips for building Flask APIs that actually scale...      │
│   (thread of 6 tweets with code snippets)"                       │
│                                                                  │
│  💼 LinkedIn:                                                   │
│  "I just published a deep dive on REST API design with          │
│   Python Flask. Here's everything I learned the hard way..."    │
│                                                                  │
│  📸 Instagram:                                                  │
│  "New tutorial! 🚀 Building APIs doesn't have to be painful.     │
│   Link in bio for the full guide..."                             │
│                                                                  │
│  ⌨️ Dev.to:                                                    │
│  "#Python #Flask #API — A comprehensive guide to REST API        │
│   design patterns, with real-world examples and code."           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Paste any URL, and the AI automatically extracts the content, analyzes it, and generates perfectly-formatted posts for each platform — with the right tone, length, hashtags, and engagement hooks.

---

## ✨ Features

- **🌐 Universal Content Fetching** — Extract content from any blog, YouTube video, or website
- **🤖 Claude AI Repurposing** — Intelligent transformation using Claude Sonnet
- **🐦 Twitter Thread Generation** — Create engaging multi-tweet threads (auto-splits into numbered tweets)
- **💼 LinkedIn Posts** — Professional posts optimized for LinkedIn's algorithm and engagement
- **📸 Instagram Captions** — Perfectly formatted with trending hashtags and emoji
- **⌨️ Dev.to Articles** — Technical articles with proper markdown formatting
- **📅 Scheduling** — Schedule posts for optimal publishing times
- **🔗 REST API** — Full API for integration with other tools and automation platforms
- **🎨 Clean Dark Web UI** — Modern, intuitive Flask interface

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Anthropic API key ([Get one here](https://anthropic.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/liuyuzhe530/ai-content-repurposer.git
cd ai-content-repurposer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API key

# Run the application
python run.py
```

Open [http://localhost:5000](http://localhost:5000) to use the web interface.

---

## ⚙️ Configuration

```env
ANTHROPIC_API_KEY=sk-ant-...
APP_SECRET_KEY=change-this-to-something-random
APP_URL=http://localhost:5000
FLASK_ENV=development
```

---

## 📡 API Reference

### Fetch Content

```bash
curl -X POST http://localhost:5000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/blog/post"}'
```

### Repurpose Content

```bash
curl -X POST http://localhost:5000/api/repurpose \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "uuid-here",
    "platform": "all",
    "api_key": "your-api-key"
  }'
```

### Generate Twitter Thread

```bash
curl -X POST http://localhost:5000/api/thread \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "uuid-here",
    "num_tweets": 5,
    "api_key": "your-api-key"
  }'
```

### Schedule Post

```bash
curl -X POST http://localhost:5000/api/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "uuid-here",
    "platform": "twitter",
    "scheduled_time": "2026-04-20T10:00:00Z"
  }'
```

---

## 🎨 Supported Platforms

| Platform | Max Length | Best For |
|----------|-----------|----------|
| Twitter/X | 280 chars/tweet | Quick tips, thread starters |
| LinkedIn | 3,000 chars | Professional insights, articles |
| Instagram | 2,200 chars | Visual content, stories |
| Dev.to | 50,000 chars | Technical tutorials, deep dives |

---

## 📁 Project Structure

```
ai-content-repurposer/
├── src/
│   ├── __init__.py          # Flask app factory
│   ├── models/
│   │   └── __init__.py     # Data models
│   ├── routes/
│   │   ├── main.py         # Web routes
│   │   └── api.py          # REST API
│   ├── services/
│   │   ├── content_fetcher.py  # URL content extraction
│   │   ├── repurposer.py       # AI repurposing
│   │   └── scheduler.py        # Post scheduling
│   └── templates/          # HTML templates
├── tests/
├── run.py                  # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 💼 Hire the Author

Need a custom content automation system, AI tool, or any other Python/Flask project built? I'm available for freelance work.

**Skills:** Python, Flask, Claude AI, OpenAI API, Content Automation, Web Scraping

**Services:**
- Web Scraping & Data Collection: $50–200
- AI Agent Development: $100–500
- Custom Python Scripts & Automation: $50–300
- GitHub Integration & CI/CD Tools: $100–400

**Contact:** [liuyuzhe530@gmail.com](mailto:liuyuzhe530@gmail.com) | [liuyuzhe530.github.io/hire-me](https://liuyuzhe530.github.io)

---

## 🔗 Similar Tools

- [GitHub PR Auto-Fixer](https://github.com/liuyuzhe530/github-pr-autofixer) — AI-powered PR analysis for failing CI/CD pipelines
- [Telegram Bot SaaS Template](https://github.com/liuyuzhe530/telegram-saas-bot) — Production-ready Telegram bot with payments & admin panel

---

<p align="center">
  Made with ❤️ and ☕ by <a href="https://github.com/liuyuzhe530">liuyuzhe530</a>
</p>
