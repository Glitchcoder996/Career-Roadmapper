# Reverse-Engineered Career Roadmapper

## What it does
An AI-powered web application that takes any hyper-specific dream job (e.g. "Full Stack Developer at a climate tech startup") and reverse-engineers it into a beautiful, interactive skill-tree roadmap. Instead of generic text advice, users get a zoomable, clickable graph where every node delivers dynamically generated AI advice — custom weekend projects, interview questions, real career paths, and resources.

## Architecture and why
- **Backend:** Python + Flask — lightweight, easy to deploy anywhere. Handles AI API calls with prompt-engineered queries to Google Gemini 1.5 Flash.
- **AI:** Google Gemini 1.5 Flash — fast, high-quality JSON responses, generous free tier suitable for a hackathon demo.
- **Visualisation:** `vis-network` (Vis.js) — hierarchical skill-tree layout with built-in zoom, pan, drag, and click events. No complex React/D3 setup needed; pure vanilla JS ensures zero build step.
- **Styling:** Tailwind CSS CDN — instant dark UI with glassmorphism effects.

## Features
| Feature | Status |
|---|---|
| AI-generated interactive skill tree (zoom, pan, click) | ✅ |
| Hyper-specific AI advice per skill node | ✅ |
| Tabbed advice panel (Advice / Project / Resources / Interview Prep / Real Paths) | ✅ |
| User time constraints (timeframe + hrs/week) | ✅ |
| Current background input for personalised planning | ✅ |
| Mark as Completed — node turns green + confetti | ✅ |
| "I already know this" → AI re-plans the full roadmap | ✅ |
| Progress bar (skills completed / total) | ✅ |
| Compare two dream roles side-by-side | ✅ |
| Export roadmap as PNG | ✅ |
| Share roadmap via link | ✅ |
| "People who took this path" — real intermediate roles | ✅ |
| Side project suggestions per phase | ✅ |
| Salary range + top companies summary bar | ✅ |

## How to run it

### Prerequisites
- Python 3.9+
- A Gemini API key → https://aistudio.google.com/app/apikey

### Setup
```bash
# 1. Clone / enter the project
cd Career-Roadmapper

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo GEMINI_API_KEY=your_key_here > .env

# 5. Run
python app.py
```
Open http://127.0.0.1:5000

## Tools and AI used
- **Google Gemini 1.5 Flash** — all AI generation (roadmap, advice, compare). Users are shown the loading indicator "Powered by Gemini 1.5 Flash" so they know AI is generating content.
- **vis-network** — interactive graph rendering
- **Tailwind CSS** — styling
- **Flask** — web server + API routing

## Who it is for
College students and early-career professionals who are tired of generic "just learn React" advice. Career Roadmapper gives them a personalised, visual plan that adapts to what they already know and the time they have — and they come back every week to check off milestones and unlock the next step.