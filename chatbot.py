from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    print("Warning: OPENAI_API_KEY not found in .env file")

chat = ChatOpenAI(
    api_key=openai_api_key,
    temperature=0.7,
    model_name="gpt-3.5-turbo"
)

def get_student_profile(user_input):
    template = """Extract structured data from this student's message:
    "{user_input}"
    
    Return as JSON with these keys:
    - major: their field of study
    - GPA: their GPA if mentioned, or "Not specified"
    - projects: any projects or experience mentioned
    - desired_role: their career interests or desired role
    
    Format the response as valid JSON only, no other text."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that extracts structured data from student messages."),
        ("human", template.format(user_input=user_input))
    ])
    
    try:
        # Get response
        response = chat.invoke(prompt.format_messages(user_input=user_input))
        
        # Try to parse the response to ensure it's valid JSON
        json_response = json.loads(response.content)
        return json.dumps(json_response)
    except Exception as e:
        print(f"Error processing chat response: {str(e)}")
        # Fallback if response isn't valid JSON
        return json.dumps({
            "major": "Not specified",
            "GPA": "Not specified",
            "projects": "Not specified",
            "desired_role": "Not specified"
        })
