# HireLens – AI-Powered ATS Resume Analyzer
# See your resume the way recruiters do.

HireLens is an AI-based Applicant Tracking System (ATS) that analyzes resumes against job descriptions to provide detailed insights and optimization suggestions. It helps users improve their resumes by identifying skill gaps, missing keywords, and overall ATS compatibility.

## Features

-📄 **Resume Analysis**
   Provides strengths, weaknesses, and improvement suggestions based on job description.
  
-🔑 **Keyword Optimization**
  Identifies missing keywords required to improve ATS performance.
  
-📊 **Percentage Match Score**
  Calculates resume-job match percentage with actionable feedback.
  
-✍️ **AI Resume Rewriter**
  Enhances resume content using AI to make it more impactful and ATS-friendly.
  
-🎯 **Skill Matching**
  Compares required skills with existing skills and highlights gaps.
  
-❓ **Interview Question Generator**
  Generates top 20 job-specific interview questions.
  
-📈 **Visual Analyzer**
  Displays resume insights using multiple interactive charts.

## Installation

1. Clone the repository:

```
git clone https://github.com/Rachita1851/Application-Tracking-System.git
```

Install the required dependencies:
```
pip install -r requirements.txt 
pip install --upgrade pip
pip install google-generativeai
pip install streamlit

```
Run the Streamlit app:
```
streamlit run app.py
```

## Usage
Open the Streamlit app in your browser.
Input the job description in the text area provided.
Upload the PDF resume using the "Upload your resume(PDF)..." button.
Click on the desired action buttons to perform various analyses.

## Technologies Used
- Python
- Streamlit
- pdf2image
- Google Gemini 2.5 Flash API 
- Pandas
-  NumPy
-Plotly (for visualizations)


#🔐 Note

API keys are stored locally using .streamlit/secrets.toml and are not included in the repository.
