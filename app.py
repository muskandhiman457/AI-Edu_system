from flask import Flask, render_template, request, jsonify
from recommender import recommend
from chatbot import get_student_profile
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']
    profile_json = get_student_profile(user_message)
    profile = json.loads(profile_json)
    recommendations = recommend(profile)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
