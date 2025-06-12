##This is the gradio UI for the model which i did not use
from flask import Flask, render_template, request, jsonify
from app.scrape_job_description import scrape_job_description
from app.chains import Chain
from app.portfolio import Portfolio
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, template_folder="app/templates")
chain = Chain()
portfolio = Portfolio()

# Load resume text
with open("app/resource/my_resume.txt", "r", encoding="utf-8") as f:
    fixed_resume_text = f.read()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    job_url = data.get("job_url")

    job_desc = scrape_job_description(job_url)
    if job_desc.startswith("Error"):
        return jsonify({"error": job_desc})

    try:
        jobs = chain.extract_jobs(job_desc)
    except Exception as e:
        return jsonify({"error": str(e)})

    job = jobs[0] if jobs else {}
    skills = job.get('skills', [])
    if not isinstance(skills, list):
        skills = [str(skills)]
    skills_text = " ".join(skills)

    links = portfolio.query_links(skills_text)
    if not links:
        links = ["No relevant portfolio links found."]

    cover_letter = chain.write_coverletter(job, links, fixed_resume_text)

    # Skill match score
    resume_words = set(fixed_resume_text.lower().split())
    matched_skills = [skill for skill in skills if skill.lower() in resume_words]
    match_score = round((len(matched_skills) / len(skills)) * 100) if skills else 0

#     # Resume highlights
#     highlights = [
#         line for line in fixed_resume_text.split('\n')
#         if any(skill.lower() in line.lower() for skill in skills)
#     ]
#    # highlight_text = highlights[:5] if highlights else ["No strong matches found."]

    return jsonify({
        "role": job.get("role", "N/A"),
        "skills": skills,
        "description": job.get("description", "N/A"),
        "match_score": match_score,
        "cover_letter": cover_letter
      
    })

if __name__ == "__main__":
    app.run(debug=False)
