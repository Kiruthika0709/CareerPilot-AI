from flask import Flask, render_template, request
import pdfplumber
import os
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

SKILLS = [
    "python","sql","java","flask","html","css",
    "javascript","git","github","docker",
    "excel","tableau","machine learning","power bi",
    "rest api","mysql","mongodb","django","aws"
]
def extract_text(file_path):

    if file_path.lower().endswith(".pdf"):

        text = ""

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                if page.extract_text():

                    text += page.extract_text()

        return text.lower()

    else:

        image = Image.open(file_path)

        return pytesseract.image_to_string(image).lower()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
@app.route("/analyze", methods=["POST"])
def analyze():

    resume = request.files["resume"]
    jd = request.files["job"]

    resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
    jd_path = os.path.join(app.config["UPLOAD_FOLDER"], jd.filename)

    resume.save(resume_path)
    jd.save(jd_path)

    resume_text = extract_text(resume_path)
    job_text = extract_text(jd_path)

    found = []
    missing = []
    required_skills = []

    for skill in SKILLS:
        if skill in job_text:
            required_skills.append(skill)

    for skill in required_skills:
        if skill in resume_text:
            found.append(skill.title())
        else:
            missing.append(skill.title())

    if len(required_skills) == 0:
        score = 0
    else:
        score = round((len(found) / len(required_skills)) * 100)

    suggestions = []

    if score >= 85:
        suggestions.append("Excellent match for this job.")
    elif score >= 70:
        suggestions.append("Good match. Add the missing skills if you have them.")
    elif score >= 50:
        suggestions.append("Average match. Improve your resume before applying.")
    else:
        suggestions.append("Low match. Add more relevant skills and projects.")

    if missing:
        suggestions.append("Missing Skills: " + ", ".join(missing))

    resume_words = len(resume_text.split())
    job_words = len(job_text.split())
    resume_skills = len(found)
    missing_skills = len(missing)

    if score >= 85:
        rating = "Excellent ⭐⭐⭐⭐⭐"
    elif score >= 70:
        rating = "Good ⭐⭐⭐⭐"
    elif score >= 50:
        rating = "Average ⭐⭐⭐"
    else:
        rating = "Needs Improvement ⭐⭐"

    return render_template(
        "result.html",
        score=score,
        found=found,
        missing=missing,
        suggestions=suggestions,
        resume_words=resume_words,
        job_words=job_words,
        resume_skills=resume_skills,
        missing_skills=missing_skills,
        rating=rating
    )

if __name__ == "__main__":
    app.run(debug=True)
