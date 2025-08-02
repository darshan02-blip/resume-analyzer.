from flask import Flask, render_template, request 
import os
import PyPDF2
import openai

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ Add your OpenAI key here
openai.api_key = "YOUR_OPENAI_API_KEY"

# Predefined job skills
job_skills = ["Python", "Java", "Machine Learning", "Data Analysis", "SQL", "HTML", "CSS", "JavaScript"]

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def analyze_skills(text):
    found = [skill for skill in job_skills if skill.lower() in text.lower()]
    missing = [skill for skill in job_skills if skill.lower() not in text.lower()]
    return found, missing

# ✅ AI Suggestions function
def get_ai_suggestions(found, missing):
    prompt = f"""
    The user has these skills: {found}.
    They are missing these skills: {missing}.
    Suggest 3 job roles they can target, and 3 skills to learn to improve their resume.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["resume"]
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            text = extract_text_from_pdf(filepath)
            
            # ✅ Analyze skills
            found, missing = analyze_skills(text)
            
            # ✅ Get AI suggestions
            suggestions = get_ai_suggestions(found, missing)
            
            # ✅ Render with suggestions
            return render_template("index.html", found=found, missing=missing, suggestions=suggestions)
    
    # Default (no upload yet)
    return render_template("index.html", found=None, missing=None, suggestions=None)

if __name__ == "__main__":
    app.run(debug=True)
