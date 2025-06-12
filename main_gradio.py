'''I also developed a fully functional Gradio-based UI for the model to enable rapid prototyping and easy interaction. 
While this version worked as expected, I ultimately chose to proceed with main1.py, which integrates the model into 
a more structured Flask application with a custom HTML/CSS frontend for better flexibility, styling, and deployment control.'''
import gradio as gr
from app.scrape_job_description import scrape_job_description
from app.chains import Chain
from app.portfolio import Portfolio
from dotenv import load_dotenv
import os

load_dotenv()

chain = Chain()
portfolio = Portfolio()

# ✅ Load resume text once
with open("app/resource/my_resume.txt", "r", encoding="utf-8") as f:
    fixed_resume_text = f.read()

def generate_coverletter(job_url):
    job_desc = scrape_job_description(job_url)
    if job_desc.startswith("Error"):
        return job_desc

    jobs = chain.extract_jobs(job_desc)
    job = jobs[0] if jobs else {}

    skills = job.get('skills', [])
    if not isinstance(skills, list):
        skills = [str(skills)]
    skills_text = " ".join(skills)

    links = portfolio.query_links(skills_text)
    if not links:
        links = ["No relevant portfolio links found."]

    cover_letter = chain.write_coverletter(job, links, fixed_resume_text)

    # ✅ Skill match score
    resume_words = set(fixed_resume_text.lower().split())
    matched_skills = [skill for skill in skills if skill.lower() in resume_words]
    match_score = round((len(matched_skills) / len(skills)) * 100) if skills else 0

    # ✅ Relevant resume highlights
    highlights = [
        line for line in fixed_resume_text.split('\n')
        if any(skill.lower() in line.lower() for skill in skills)
    ]
    highlight_text = "\n".join(f"- {line.strip()}" for line in highlights[:5]) or "No strong matches found."

    # ✅ Final organized summary
    summary = (
        f"**🧑‍💼 Job Role:** {job.get('role', 'N/A')}\n" + '\n'
        f"**🛠️ Required Skills:** {', '.join(skills)}\n\n"
        f"**🔍 Full Job Description:**\n<details><summary>Click to expand</summary>\n\n{job.get('description', 'N/A')}\n\n</details>"
        f"**📊 Resume–Job Skill Match Score:** {match_score}%\n\n"
        f"**📄 Generated Cover Letter:**\n{cover_letter}\n\n"
        
    )

    return summary


with gr.Blocks() as demo:
    gr.Markdown("# 📄 Cover Letter Generator with Portfolio Matching\nPowered by Groq, ChromaDB, and Python 🧠")
    with gr.Row():
        with gr.Column():
            job_url_input = gr.Textbox(label="Job Posting URL", placeholder="Paste job URL here...")
            generate_btn = gr.Button("🚀 Generate Cover Letter")
        with gr.Column():
            coverletter_output = gr.Markdown(label="Cover Letter + Insights")

    generate_btn.click(
        generate_coverletter,
        inputs=[job_url_input],
        outputs=[coverletter_output]
    )

if __name__ == "__main__":
    demo.launch()
