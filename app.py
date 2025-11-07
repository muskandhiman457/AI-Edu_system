from flask import Flask, render_template, request, jsonify
from recommender import recommend
from chatbot import get_student_profile
import json
import logging
import os
import pandas as pd
from werkzeug.utils import secure_filename


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)


UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_SKILL_EXT = {'.csv', '.xls', '.xlsx'}

@app.route('/')
def home():
    logger.info("Accessing home page")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}")
        return "Error loading page", 500

@app.route('/chat', methods=['POST'])
def chat():
  
    data = None
    try:
        data = request.get_json(silent=True)
    except Exception:
        data = None

    if data and isinstance(data, dict):
        user_message = data.get('message', '')
        parsed_profile = data.get('parsed_profile')
    else:
        user_message = request.form.get('message', '')
        parsed_profile = None

    profile_json = get_student_profile(user_message)
    try:
        profile = json.loads(profile_json)
    except Exception:
        profile = {"major": "Not specified", "GPA": "Not specified", "projects": "", "desired_role": ""}

   
   
    if parsed_profile:
       
        try:
            if isinstance(parsed_profile, str):
                parsed_profile = json.loads(parsed_profile)
        except Exception:
            pass

     
        skills = []
        if isinstance(parsed_profile, dict):
            for k, v in parsed_profile.items():
                key = k.lower()
                if isinstance(v, list):
                    vals = v
                else:
                    vals = [v]

                if 'skill' in key or 'skills' in key:
                    skills += [str(x) for x in vals]
                elif 'interest' in key or 'interests' in key:
                    profile['desired_role'] = (profile.get('desired_role','') + ' ' + ' '.join([str(x) for x in vals])).strip()
                elif 'intern' in key:
                    profile['projects'] = (profile.get('projects','') + ' ' + ' '.join([str(x) for x in vals])).strip()
                elif 'desired' in key or 'role' in key:
                    profile['desired_role'] = (profile.get('desired_role','') + ' ' + ' '.join([str(x) for x in vals])).strip()

        if skills:
      
            profile['projects'] = (profile.get('projects','') + ' ' + ','.join(skills)).strip()

    recommendations = recommend(profile)
    return jsonify(recommendations)


@app.route('/profile', methods=['POST'])
def profile():
    """Extract structured student profile from a message without running recommendations."""
    data = request.get_json(silent=True) or {}
    message = data.get('message') or request.form.get('message', '')
    profile_json = get_student_profile(message)
    try:
        profile = json.loads(profile_json)
    except Exception:
        profile = {"major": "Not specified", "GPA": "Not specified", "projects": "", "desired_role": ""}
    return jsonify({'profile': profile})


@app.route('/upload', methods=['POST'])
def upload():
    """Accepts resume (optional) and skills CSV/XLSX file, saves them, parses skills/interest/internship/desired_job and returns parsed JSON."""
    files = request.files
    resume = files.get('resume')
    skills_file = files.get('skills_file')

    result = {'resume_saved': False, 'parsed_profile': {}}

    if resume:
        filename = secure_filename(resume.filename)
        resume_path = os.path.join(UPLOAD_FOLDER, filename)
        resume.save(resume_path)
        result['resume_saved'] = True

    if skills_file:
        filename = secure_filename(skills_file.filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_SKILL_EXT:
            return jsonify({'error': f'Unsupported file type: {ext}'}), 400

        path = os.path.join(UPLOAD_FOLDER, filename)
        skills_file.save(path)

        try:
            if ext == '.csv':
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)

            parsed = {}
          
            for col in df.columns:
                low = col.lower()
                if any(x in low for x in ['skill', 'skills', 'interest', 'interests', 'intern', 'desired', 'role', 'job']):
                    values = df[col].dropna().astype(str).tolist()
                    parsed[col] = values

        
            if not parsed and len(df) >= 1:
                row = df.iloc[0].to_dict()
                for k, v in row.items():
                    parsed[str(k)] = [str(v)]

            result['parsed_profile'] = parsed
        except Exception as e:
            logger.error(f"Error parsing skills file: {e}")
            return jsonify({'error': str(e)}), 500

    return jsonify(result)

if __name__ == '__main__':
    print("Starting Flask app on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', debug=True, port=5000, use_reloader=True)
