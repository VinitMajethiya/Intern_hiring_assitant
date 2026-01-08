import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    # using llama-3.3-70b-versatile which is the latest supported model
    return ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7, groq_api_key=api_key)

def generate_questions(tech_stack):
    llm = get_llm()
    if not llm:
        return ["Error: API Key not found. Please checking your settings."]
    
    prompt = f"Generate 3 to 5 technical interview questions for a candidate with the following tech stack: {tech_stack}. Return only the questions as a numbered list."
    response = llm.invoke([HumanMessage(content=prompt)])
    questions = response.content.strip().split('\n')
    # Clean up numbering if needed, but usually the prompt handles it
    return [q.strip() for q in questions if q.strip()]

def get_conversation_response(messages):
    llm = get_llm()
    if not llm:
        return "System Error: Groq API Key is missing. Please provide it to continue."
    
    response = llm.invoke(messages)
    return response.content

def analyze_conversation(history_text):
    """
    Analyzes the conversation history to determine if the candidate has provided their Tech Stack.
    Returns a dictionary with 'tech_stack' (str or None).
    """
    llm = get_llm()
    if not llm:
        return {"tech_stack": None}

    # Lightweight prompt to extract state
    analysis_prompt = f"""
    Analyze the following conversation history between a Recruiter (AI) and a Candidate (User).
    Determine if the candidate has explicitly stated their 'Tech Stack' (technologies, languages, frameworks they use).
    
    Conversation History:
    {history_text}
    
    Output JSON ONLY:
    {{
        "has_tech_stack": true/false,
        "tech_stack": "extracted tech stack text" or null
    }}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=analysis_prompt)])
        content = response.content.strip()
        # Basic JSON parsing cleanup if needed (though usually 3.5 is good)
        import json
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        data = json.loads(content)
        if data.get("has_tech_stack"):
            return {"tech_stack": data.get("tech_stack")}
    except Exception as e:
        print(f"Error in analysis: {e}")
        pass
        
    return {"tech_stack": None}
