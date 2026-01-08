import streamlit as st
from utils import get_conversation_response, generate_questions, analyze_conversation
from prompts import SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from data_handler import save_session_data
import os

# Page Config
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="📝")

# User Interface styling
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
    }
    .chat-message.user {
        background-color: #2b313e
    }
    .chat-message.bot {
        background-color: #475063
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("TalentScout Hiring Assistant 🤖")
st.markdown("Welcome! I am here to screen candidates for technology roles.")
st.markdown("🔒 **Privacy Notice**: Your data is handled securely. PII will be anonymized for storage.")

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]
    # Add initial greeting via the AI to make it organic
    # We can trigger the first AI response to kick things off
    st.session_state.initial_greeting_done = False

if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}

if "stage" not in st.session_state:
    st.session_state.stage = "INFO_GATHERING" # INFO_GATHERING, QUESTIONS, FINISHED

# Sidebar removed for cleaner UI
# API Key is expected to be in .env now
if "GROQ_API_KEY" not in os.environ:
     # Fallback or silent error - relying on .env
     pass

# Initial Greeting Trigger
if not st.session_state.get("initial_greeting_done"):
    with st.spinner("Initializing..."):
        # We send an empty message or a system trigger to get the bot to speak first based on the instructions
        # Or we can just pretend the bot spoke. For better control, let's ask the bot to greet.
        # But wait, usually we just append an AI message. But the prompt says "Greet if not already done".
        # Let's force a generation.
        response = get_conversation_response(st.session_state.messages) 
        st.session_state.messages.append(AIMessage(content=response))
        st.session_state.initial_greeting_done = True
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    if isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)
    elif isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)

# Chat Input
if st.session_state.stage != "FINISHED":
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)
        
        # Check for exit keywords
        if prompt.lower() in ["exit", "quit", "bye", "end"]:
            st.session_state.stage = "FINISHED"
            
            # Save data
            record_id = save_session_data(st.session_state.candidate_info, st.session_state.messages)
            
            final_response = f"Thank you for your time! We have recorded your responses (Reference ID: {record_id}). A recruiter will be in touch soon. Goodbye!"
            st.session_state.messages.append(AIMessage(content=final_response))
            with st.chat_message("assistant"):
                st.write(final_response)
        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # 1. Analyze if we need to transition from INFO -> QUESTIONS
                    if st.session_state.stage == "INFO_GATHERING":
                        # Convert history to text for analysis
                        history_text = "\n".join([f"{type(m).__name__}: {m.content}" for m in st.session_state.messages])
                        analysis = analyze_conversation(history_text)
                        
                        if analysis.get("tech_stack"):
                            # We have the tech stack! Transition.
                            tech_stack = analysis["tech_stack"]
                            st.session_state.candidate_info["Tech Stack"] = tech_stack
                            st.session_state.stage = "QUESTIONS"
                            
                            # Generate questions
                            questions = generate_questions(tech_stack)
                            question_text = "\n".join(questions)
                            
                            # Inject instructions
                            system_instruction = f"""
                            SYSTEM UPDATE: The candidate has confirmed their tech stack: {tech_stack}.
                            Here are the generated technical interview questions:
                            {question_text}
                            
                            INSTRUCTIONS:
                            1. Acknowledge the candidate's last message.
                            2. Tell them you are now going to ask technical questions.
                            3. Ask the first question from the list above.
                            """
                            st.session_state.messages.append(SystemMessage(content=system_instruction))
                    
                    # 2. Generate response
                    response = get_conversation_response(st.session_state.messages)
                    st.write(response)
                    st.session_state.messages.append(AIMessage(content=response))
