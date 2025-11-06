from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

chat = ChatOpenAI(api_key=openai_api_key, temperature=0.7, model="gpt-3.5-turbo")

def get_student_profile(user_input):
    template = """
    Extract structured data from this student's message:
    "{user_input}"

    Return as JSON with keys: major, GPA, projects, desired_role
    """
    prompt = ChatPromptTemplate.from_template(template)
    messages = prompt.format_messages(user_input=user_input)
    response = chat(messages)
    return response.content
