import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def recommend(student_profile):
    # Load datasets
    courses = pd.read_csv('data/courses.csv')
    careers = pd.read_csv('data/career_paths.csv')
    resources = pd.read_csv('data/university_resources.csv')

    # Create combined text for similarity
    student_text = f"{student_profile['major']} {student_profile['projects']} {student_profile['desired_role']}"

    # Compute embeddings
    student_embedding = model.encode(student_text, convert_to_tensor=True)

    def get_top_matches(df, text_column, top_n=3):
        embeddings = model.encode(df[text_column].tolist(), convert_to_tensor=True)
        scores = util.cos_sim(student_embedding, embeddings)[0]
        top_indices = scores.argsort(descending=True)[:top_n]
        return df.iloc[top_indices.cpu().numpy()]

    top_courses = get_top_matches(courses, 'description')
    top_careers = get_top_matches(careers, 'description')
    top_resources = get_top_matches(resources, 'description')

    return {
        "courses": top_courses.to_dict(orient='records'),
        "careers": top_careers.to_dict(orient='records'),
        "resources": top_resources.to_dict(orient='records')
    }
