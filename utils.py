import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
@st.cache_resource
def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except (KeyError, FileNotFoundError):
            api_key = None
            
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
        yield "System Error: Groq API Key is missing. Please provide it to continue."
        return
    
    # Return a generator for streaming
    try:
        for chunk in llm.stream(messages):
            if hasattr(chunk, "content"):
                yield chunk.content
    except Exception as e:
        yield f"Connection Error: {str(e)}"

def analyze_conversation(history_text):
    """
    Analyzes the conversation history to extract detailed candidate information.
    Returns a dictionary with extracted fields or None/Empty strings if not found.
    """
    llm = get_llm()
    if not llm:
        return {}

    # Comprehensive prompt to extract all PII and Professional Data
    # Note: In a real production system, handling PII requires stricter controls.
    analysis_prompt = f"""
    Analyze the following conversation history between a Recruiter (AI) and a Candidate (User).
    Extract the following information if available:
    - user_name
    - email
    - phone
    - experience (years)
    - position (desired role)
    - location
    - tech_stack (languages, frameworks)

    Conversation History:
    {history_text}
    
    Output JSON ONLY:
    {{
        "has_tech_stack": true/false,
        "tech_stack": "...",
        "user_name": "...",
        "email": "...",
        "phone": "...",
        "experience": "...",
        "position": "...",
        "location": "..."
    }}
    If a field is not found, use null.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=analysis_prompt)])
        content = response.content.strip()
        
        import json
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        data = json.loads(content)
        # Flatten return
        return data
    except Exception as e:
        print(f"Error in analysis: {e}")
        pass
        
    return {}


def analyze_sentiment(text):
    """
    Analyzes the sentiment of the user's message.
    Returns a dictionary with 'sentiment' (Positive, Neutral, Negative) and 'score' (optional confidence).
    """
    llm = get_llm()
    if not llm:
        return {"sentiment": "Neutral"}
        
    prompt = f"""
    Analyze the sentiment of the following text from a job candidate. 
    Classify it as "Positive", "Neutral", or "Negative".
    
    Text: "{text}"
    
    Return ONLY the one word label.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        sentiment = response.content.strip().replace('"', '').replace('.', '')
        # Normalize
        if "positive" in sentiment.lower(): return {"sentiment": "Positive"}
        if "negative" in sentiment.lower(): return {"sentiment": "Negative"}
        return {"sentiment": "Neutral"}
    except Exception:
        return {"sentiment": "Neutral"}

        return {"sentiment": "Neutral"}

def evaluate_candidate(conversation_history_text, tech_stack):
    """
    Evaluates the candidate's performance based on the conversation history.
    Returns a dictionary with score, recommendation, strengths, weaknesses, and summary.
    """
    llm = get_llm()
    if not llm:
        return {}

    prompt = f"""
    You are an expert Technical Interviewer. 
    Analyze the following interview transcript for a candidate specializing in {tech_stack}.
    
    Transcript:
    {conversation_history_text}
    
    Evaluate the candidate based on:
    1. Technical Accuracy (Did they answer the questions correctly?)
    2. Depth of Knowledge (Did they understand the underlying concepts?)
    3. Communication Clarity (Were they concise and clear?)
    
    Provide your evaluation in the following JSON format ONLY:
    {{
        "score": (integer 0-100),
        "recommendation": "Strong Hire" | "Hire" | "Weak Hire" | "No Hire",
        "strengths": ["point 1", "point 2", ...],
        "weaknesses": ["point 1", "point 2", ...],
        "summary": "A brief 2-3 sentence summary of the candidate's performance."
    }}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        import json
        # Robust JSON extraction
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        evaluation = json.loads(content)
        return evaluation
    except Exception as e:
        print(f"Error in evaluation: {e}")
        return {
            "score": 0,
            "recommendation": "Error",
            "strengths": [],
            "weaknesses": [],
            "summary": "Could not generate evaluation due to system error."
        }
