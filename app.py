import os
import json
import re
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = genai.Client()


# In-memory store for shared roadmaps (production: use Redis/DB)
shared_roadmaps = {}


def clean_json(text: str) -> str:
    """Strip markdown fences and extract JSON from model response."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", shared_roadmap=None)

@app.route("/share/<share_id>")
def shared(share_id):
    entry = shared_roadmaps.get(share_id)
    if not entry:
        return "Roadmap not found or expired.", 404
    return render_template("index.html", shared_roadmap=entry)


# ─────────────────────────────────────────────────────────────────────────────
# API: Generate full roadmap
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    job_title      = data.get("job_title", "").strip()
    timeframe      = data.get("timeframe", "6 months")
    hours_per_week = data.get("hours_per_week", "10")
    known_skills   = data.get("known_skills", [])
    current_role   = data.get("current_role", "").strip()

    if not job_title:
        return jsonify({"error": "Job title is required"}), 400

    known_str = ""
    if known_skills:
        known_str = f"\nThe user ALREADY knows these skills — do NOT include them: {', '.join(known_skills)}."

    current_role_str = ""
    if current_role:
        current_role_str = f"\nThe user's current role/background is: {current_role}."

    prompt = f"""
You are a senior tech career coach who has helped thousands of professionals land roles at top companies.
A user wants to become: "{job_title}".{current_role_str}
They can commit {hours_per_week} hours per week and want to achieve this in {timeframe}.{known_str}

Generate a realistic, highly specific career roadmap broken into 4 logical phases.
Each phase should reflect real industry expectations — mention REAL certifications, tools, companies, and roles.

Respond with ONLY valid JSON in this EXACT structure (no markdown, no explanation):
{{
  "job": "{job_title}",
  "overview": "2-sentence overview of what this path looks like",
  "phases": [
    {{
      "phase_name": "Short phase title",
      "description": "What this phase achieves and why it matters",
      "estimated_time": "e.g. 6 weeks",
      "skills_to_learn": ["Skill A", "Skill B", "Skill C"],
      "milestone": "The tangible output/milestone that proves this phase is complete",
      "entry_roles": ["Junior title that maps to this phase"],
      "side_projects": [
        {{
          "title": "Project name",
          "description": "What to build and why it impresses recruiters"
        }}
      ],
      "people_who_took_this_path": [
        {{
          "role": "Mid-level role they held",
          "company_type": "Type of company e.g. Series B fintech",
          "duration": "How long they stayed"
        }}
      ]
    }}
  ],
  "salary_range": "Expected salary range after completing the full roadmap",
  "top_companies": ["Company or company type that hires for this role"],
  "overlap_skills": []
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )
        cleaned  = clean_json(response.text)
        result   = json.loads(cleaned)
        return jsonify(result)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}. Raw response: {response.text}")
        return jsonify({"error": f"AI returned malformed JSON: {str(e)}", "raw": response.text}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# API: Dynamic advice for a specific skill node
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/advice", methods=["POST"])
def advice():
    data      = request.get_json()
    skill     = data.get("skill", "").strip()
    job_title = data.get("job_title", "").strip()
    phase     = data.get("phase", "").strip()

    if not skill:
        return jsonify({"error": "Skill is required"}), 400

    prompt = f"""
You are a senior engineer and interviewer who specializes in hiring for "{job_title}" roles.
A candidate is currently learning "{skill}" (part of the "{phase}" phase).

Give them hyper-specific, actionable advice. Respond with ONLY valid JSON:
{{
  "advice": "3-4 sentence explanation of HOW to learn this skill effectively, not just what it is",
  "project_idea": {{
    "title": "Specific weekend project title",
    "description": "Step-by-step what to build, what tech to use, and why it will impress a {job_title} interviewer",
    "github_inspiration": "A real or realistic GitHub repo name / tutorial to start from"
  }},
  "resources": [
    {{"type": "Course/Book/Doc", "name": "Name of the resource", "url_hint": "Official site or platform name"}}
  ],
  "interview_questions": [
    "Question 1 — the kind asked at FAANG",
    "Question 2 — mid-level company style",
    "Question 3 — startup-style practical question"
  ],
  "common_mistakes": "The #1 mistake beginners make when learning this skill"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )
        cleaned  = clean_json(response.text)
        result   = json.loads(cleaned)
        return jsonify(result)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"AI returned malformed JSON: {str(e)}", "raw": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# API: Compare two roles
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/compare", methods=["POST"])
def compare():
    data   = request.get_json()
    role_a = data.get("role_a", "").strip()
    role_b = data.get("role_b", "").strip()

    if not role_a or not role_b:
        return jsonify({"error": "Both roles are required"}), 400

    prompt = f"""
Compare these two career paths for a college student deciding between them:
Role A: "{role_a}"
Role B: "{role_b}"

Respond with ONLY valid JSON:
{{
  "role_a": "{role_a}",
  "role_b": "{role_b}",
  "shared_skills": ["Skills that appear in BOTH paths — list at least 5"],
  "unique_to_a": ["Skills only needed for {role_a}"],
  "unique_to_b": ["Skills only needed for {role_b}"],
  "salary_a": "Expected salary range for {role_a}",
  "salary_b": "Expected salary range for {role_b}",
  "time_to_hire_a": "Realistic time to first job for {role_a}",
  "time_to_hire_b": "Realistic time to first job for {role_b}",
  "verdict": "2-sentence honest recommendation on which path to choose and why",
  "switchability": "How easy is it to switch from one path to the other mid-career?"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )
        cleaned  = clean_json(response.text)
        result   = json.loads(cleaned)
        return jsonify(result)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"AI returned malformed JSON: {str(e)}", "raw": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# API: Share roadmap — save and return a link
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/share", methods=["POST"])
def share():
    data = request.get_json()
    roadmap_data = data.get("roadmap")
    if not roadmap_data:
        return jsonify({"error": "No roadmap data provided"}), 400

    share_id = str(uuid.uuid4())[:8]
    shared_roadmaps[share_id] = {
        "roadmap": roadmap_data,
        "created_at": datetime.utcnow().isoformat()
    }
    return jsonify({"share_id": share_id, "url": f"/share/{share_id}"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)