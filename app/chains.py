import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

class Chain:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set.")
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name='llama-3.3-70b-versatile'
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
"""
### RAW JOB POSTING TEXT:
{page_data}

### TASK:
Parse this job posting carefully and extract the following into a valid JSON object:

- "role": The official job title. This is usually near the top (e.g., "Staff Machine Learning Engineer").
- "experience": Years of experience or related requirements.
- "skills": List of core technical or soft skills (ML, Python, etc.).
- "description": Summary of the role, including responsibilities and focus areas.

Return only valid JSON. If you're unsure about a field, use an empty string or best estimate.
Do not include team names or navigation text. Focus only on the main job description.
### INPUT:
{page_data}

### OUTPUT (JSON ONLY):
            """
        )
        chain_extract = prompt_extract | self.llm
        try:
            result = chain_extract.invoke({"page_data": cleaned_text})
            parser = JsonOutputParser()
            parsed = parser.parse(result.content)
            return parsed if isinstance(parsed, list) else [parsed]
        except OutputParserException:
            raise OutputParserException("Context too large or malformed JSON. Unable to parse job description.")

    def write_coverletter(self, job, links, resume_text):
        prompt_coverletter = PromptTemplate.from_template(
            """
### JOB DESCRIPTION
{job_description}

### CANDIDATE RESUME SUMMARY
{resume_summary}

### INSTRUCTION:
You are **Saketh Ram Kalavakuntla**, a graduate student in Computational Data Science at Purdue University, graduating in December. You are currently seeking full-time roles in **machine learning, data science, or data analytics**.

You have over 2 years of experience in analytics and modeling. Write a **short, personalized cover letter** to a recruiter using the job description and your resume summary.

Also, **incorporate the most relevant portfolio links** from the list below:
{link_list}

Write this as a short and professional **email/cover letter**, without any preamble.

### EMAIL:
            """
        )
        chain_coverletter = prompt_coverletter | self.llm
        links_text = "\n".join(f"<{link}>" for link in links)
        result = chain_coverletter.invoke({
            "job_description": str(job),
            "resume_summary": resume_text,
            "link_list": links_text
        })
        return result.content
